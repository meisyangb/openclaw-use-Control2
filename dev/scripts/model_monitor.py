#!/usr/bin/env python3
"""
OpenClaw Model Monitor - 监控模型使用状态并自动切换
V3版本 - 改进错误去重和检测逻辑

关键改进:
1. 基于错误内容哈希去重，而非message id
2. 每次运行只报告新发现的错误
3. 自动清理过期的错误记录
4. 只在检测到真正的新错误时才切换模型
"""

import json
import os
import hashlib
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, List, Any, Set

# 配置路径
HOME = Path.home()
CONFIG_PATH = HOME / ".openclaw" / "openclaw.json"
MEMORY_PATH = HOME / ".openclaw" / "workspace" / "memory"
STATE_PATH = MEMORY_PATH / "model-monitor-state.json"
LOG_PATH = MEMORY_PATH / "model-monitor.log"
ERROR_CACHE_PATH = MEMORY_PATH / "model-monitor-error-cache.json"

class ModelMonitor:
    def __init__(self):
        self.config = self.load_config()
        self.state = self.load_state()
        self.error_cache = self.load_error_cache()
        self.current_model = self.get_current_model()
        self.new_errors_detected = []
        
    def load_config(self) -> Dict[str, Any]:
        """加载OpenClaw配置"""
        try:
            if CONFIG_PATH.exists():
                with open(CONFIG_PATH) as f:
                    return json.load(f)
        except Exception as e:
            self.log(f"Failed to load config: {e}")
        return {}
    
    def load_state(self) -> Dict[str, Any]:
        """加载监控状态"""
        try:
            if STATE_PATH.exists():
                with open(STATE_PATH) as f:
                    return json.load(f)
        except Exception:
            pass
        return {
            "model_errors": {},
            "last_check": None,
            "error_history": []
        }
    
    def load_error_cache(self) -> Dict[str, str]:
        """
        加载错误缓存
        
        格式: { "错误哈希": "首次发现时间" }
        """
        try:
            if ERROR_CACHE_PATH.exists():
                with open(ERROR_CACHE_PATH) as f:
                    return json.load(f)
        except Exception:
            pass
        return {}
    
    def save_error_cache(self):
        """保存错误缓存"""
        try:
            MEMORY_PATH.mkdir(parents=True, exist_ok=True)
            with open(ERROR_CACHE_PATH, "w") as f:
                json.dump(self.error_cache, f)
        except Exception as e:
            self.log(f"Failed to save error cache: {e}")
    
    def cleanup_error_cache(self):
        """清理过期的错误缓存（超过1小时的记录）"""
        now = datetime.now()
        expired_keys = []
        
        for error_hash, timestamp_str in self.error_cache.items():
            try:
                timestamp = datetime.fromisoformat(timestamp_str)
                if (now - timestamp) > timedelta(hours=1):
                    expired_keys.append(error_hash)
            except Exception:
                expired_keys.append(error_hash)
        
        for key in expired_keys:
            del self.error_cache[key]
        
        if expired_keys:
            self.save_error_cache()
    
    def save_state(self):
        """保存监控状态"""
        try:
            MEMORY_PATH.mkdir(parents=True, exist_ok=True)
            self.state["last_check"] = datetime.now().isoformat()
            with open(STATE_PATH, "w") as f:
                json.dump(self.state, f, indent=2)
        except Exception as e:
            self.log(f"Failed to save state: {e}")
    
    def log(self, message: str):
        """记录日志"""
        timestamp = datetime.now().isoformat()
        log_line = f"[{timestamp}] {message}"
        print(log_line, file=sys.stderr)
        try:
            MEMORY_PATH.mkdir(parents=True, exist_ok=True)
            with open(LOG_PATH, "a") as f:
                f.write(log_line + "\n")
        except Exception:
            pass
    
    def get_current_model(self) -> str:
        """获取当前使用的模型"""
        if self.config.get("agents", {}).get("defaults", {}).get("model", {}).get("primary"):
            return self.config["agents"]["defaults"]["model"]["primary"]
        return "bailian/qwen3-coder-plus"
    
    def get_fallback_models(self) -> List[str]:
        """获取备用模型列表"""
        fallbacks = self.config.get("agents", {}).get("defaults", {}).get("model", {}).get("fallbacks", [])
        if not fallbacks:
            fallbacks = [
                "bailian/qwen3-coder-plus",
                "zai/glm-4.5-air",
                "zai/glm-4.7",
                "bailian/qwen3.5-plus"
            ]
        return fallbacks
    
    def compute_error_hash(self, error_message: str, model: str, error_type: str) -> str:
        """
        计算错误的唯一哈希
        
        基于错误内容而非message id，确保相同错误不会被重复报告
        """
        content = f"{model}|{error_type}|{error_message[:100]}"
        return hashlib.md5(content.encode()).hexdigest()[:16]
    
    def is_new_error(self, error_hash: str) -> bool:
        """检查是否是新错误（未被记录过）"""
        return error_hash not in self.error_cache
    
    def record_error_in_cache(self, error_hash: str):
        """将错误记录到缓存"""
        self.error_cache[error_hash] = datetime.now().isoformat()
        self.save_error_cache()
    
    def is_real_api_error(self, data: Dict) -> Optional[Dict[str, Any]]:
        """
        检查是否是真实的API错误响应
        
        只在以下情况认定为真实错误:
        1. errorMessage字段存在且包含真正的错误信息
        2. 错误来自API响应结构，而非消息内容
        """
        message = data.get("message", {})
        
        # 检查errorMessage字段 - 这是真正的API错误
        error_message = message.get("errorMessage")
        if error_message:
            provider = message.get("provider", "unknown")
            model = message.get("model", "unknown")
            full_model = f"{provider}/{model}"
            
            error_type = self.classify_api_error(error_message)
            if error_type:
                # 计算错误哈希
                error_hash = self.compute_error_hash(error_message, full_model, error_type)
                
                # 检查是否是新错误
                if self.is_new_error(error_hash):
                    return {
                        "type": error_type,
                        "message": error_message[:200],
                        "model": full_model,
                        "error_hash": error_hash
                    }
                else:
                    # 已知的错误，不重复报告
                    return None
        
        return None
    
    def classify_api_error(self, error_message: str) -> Optional[str]:
        """
        分类API错误类型
        
        只匹配真正的API错误消息
        """
        if not error_message:
            return None
        
        error_lower = error_message.lower()
        
        # Billing/Quota错误
        billing_indicators = [
            "insufficient credit",
            "run out of credit", 
            "billing",
            "payment required",
            "quota exceeded",
            "credit balance",
            "余额不足",
            "额度不足",
            "无可用资源包",
            "请充值",
            "429"  # Rate limit / quota
        ]
        for indicator in billing_indicators:
            if indicator in error_lower:
                return "billing"
        
        # Auth错误
        auth_indicators = [
            "unauthorized",
            "invalid api key",
            "authentication failed",
            "forbidden",
            "认证失败"
        ]
        for indicator in auth_indicators:
            if indicator in error_lower:
                return "auth"
        
        # Rate limit错误 (非billing相关)
        rate_indicators = [
            "rate limit",
            "too many requests",
            "请求过于频繁",
            "frequency limit"
        ]
        for indicator in rate_indicators:
            if indicator in error_lower:
                return "rate_limit"
        
        # Timeout错误
        timeout_indicators = [
            "timeout",
            "timed out",
            "超时",
            "request timeout"
        ]
        for indicator in timeout_indicators:
            if indicator in timeout_indicators:
                return "timeout"
        
        return None
    
    def check_session_errors(self) -> List[Dict[str, Any]]:
        """
        检查会话日志中的真实API错误
        
        只检查最新的会话文件中的最近消息
        """
        errors = []
        sessions_dir = HOME / ".openclaw" / "agents" / "main" / "sessions"
        
        if not sessions_dir.exists():
            return errors
        
        try:
            # 只检查最新的2个会话文件
            session_files = sorted(
                [f for f in sessions_dir.glob("*.jsonl") 
                 if not '.reset.' in f.name],
                key=lambda p: p.stat().st_mtime,
                reverse=True
            )[:2]
            
            for session_file in session_files:
                try:
                    with open(session_file) as f:
                        # 只读取最后30行
                        lines = f.readlines()[-30:]
                    
                    for line in lines:
                        try:
                            data = json.loads(line)
                            
                            # 只检查type为message的记录
                            if data.get("type") != "message":
                                continue
                            
                            # 检查是否是真正的API错误
                            error = self.is_real_api_error(data)
                            if error:
                                errors.append(error)
                                self.record_error_in_cache(error["error_hash"])
                                
                        except json.JSONDecodeError:
                            continue
                except Exception as e:
                    self.log(f"Error reading session file: {e}")
        except Exception as e:
            self.log(f"Error checking sessions: {e}")
        
        return errors
    
    def switch_model(self, target_model: str) -> bool:
        """切换到指定模型"""
        try:
            result = subprocess.run(
                ["openclaw", "models", "set", target_model],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                self.log(f"✓ Successfully switched to {target_model}")
                self.current_model = target_model
                return True
            else:
                self.log(f"✗ Failed to switch to {target_model}: {result.stderr}")
                return False
        except Exception as e:
            self.log(f"✗ Error switching model: {e}")
            return False
    
    def get_next_available_model(self, exclude_model: Optional[str] = None) -> Optional[str]:
        """获取下一个可用的模型"""
        fallbacks = self.get_fallback_models()
        model_errors = self.state.get("model_errors", {})
        
        for model in fallbacks:
            if model == exclude_model:
                continue
            
            # 检查模型是否有billing错误（30分钟冷却）
            error_info = model_errors.get(model, {})
            if error_info.get("type") == "billing":
                error_time = error_info.get("timestamp")
                if error_time:
                    try:
                        error_dt = datetime.fromisoformat(error_time)
                        if (datetime.now() - error_dt).total_seconds() < 1800:
                            continue
                    except Exception:
                        pass
            
            if model != self.current_model:
                return model
        
        return None
    
    def record_error(self, model: str, error_type: str, message: str):
        """记录错误"""
        self.state.setdefault("model_errors", {})[model] = {
            "type": error_type,
            "message": message[:100],
            "timestamp": datetime.now().isoformat()
        }
        self.state.setdefault("error_history", []).append({
            "model": model,
            "type": error_type,
            "timestamp": datetime.now().isoformat()
        })
        # 只保留最近20条错误
        if len(self.state["error_history"]) > 20:
            self.state["error_history"] = self.state["error_history"][-20:]
        
        self.save_state()
    
    def run(self) -> Dict[str, Any]:
        """运行监控检查"""
        result = {
            "status": "ok",
            "current_model": self.current_model,
            "actions": [],
            "errors": []
        }
        
        # 清理过期的错误缓存
        self.cleanup_error_cache()
        
        # 检查会话中的真实API错误
        errors = self.check_session_errors()
        
        for error in errors:
            result["errors"].append(error)
            error_type = error["type"]
            model = error["model"]
            
            self.log(f"⚠️ Detected {error_type} error in model {model}")
            self.record_error(model, error_type, error["message"])
            
            # 对于billing错误，立即切换（但每个错误只切换一次）
            if error_type == "billing":
                next_model = self.get_next_available_model(exclude_model=model)
                if next_model:
                    if self.switch_model(next_model):
                        result["actions"].append(f"switched to {next_model}")
                        result["current_model"] = next_model
            
            # 对于auth错误，切换模型
            elif error_type == "auth":
                next_model = self.get_next_available_model(exclude_model=model)
                if next_model:
                    if self.switch_model(next_model):
                        result["actions"].append(f"switched to {next_model}")
                        result["current_model"] = next_model
        
        if result["errors"]:
            result["status"] = "errors_detected"
        
        self.save_state()
        return result


def main():
    """主函数"""
    monitor = ModelMonitor()
    result = monitor.run()
    
    # 输出JSON格式结果
    print(json.dumps(result, indent=2))
    
    # 如果有严重错误，返回非零状态码
    if any(e["type"] in ["billing", "auth"] for e in result.get("errors", [])):
        sys.exit(1)
    
    sys.exit(0)


if __name__ == "__main__":
    main()