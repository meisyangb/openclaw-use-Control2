#!/usr/bin/env python3
"""
================================================================================
OpenClaw Model Monitor v2.0 - 自主模型健康监控与自动切换系统
================================================================================
作者: OpenClaw Assistant
版本: 2.0.0
更新日期: 2026-03-04
位置: ~/.openclaw/workspace/scripts/model_monitor_v2.py

功能说明:
-----------
1. 实时监控模型API错误（billing/rate_limit/auth/timeout）
2. 自动检测并切换到备用模型
3. 智能冷却机制防止频繁切换
4. 详细日志记录和状态持久化
5. 支持heartbeat/cron集成

架构设计:
-----------
- ErrorClassifier: 错误分类器，识别错误类型
- ModelRegistry: 模型注册表，管理模型状态和fallback链
- CooldownManager: 冷却管理器，防止频繁切换
- HealthChecker: 健康检查器，主动探测模型状态
- AutoSwitcher: 自动切换器，执行模型切换操作
- Logger: 日志记录器，结构化日志输出

使用方法:
-----------
# 基本检查
python3 ~/.openclaw/workspace/scripts/model_monitor_v2.py

# 详细模式
python3 ~/.openclaw/workspace/scripts/model_monitor_v2.py --verbose

# 强制检查所有模型
python3 ~/.openclaw/workspace/scripts/model_monitor_v2.py --check-all

# 测试模式（不实际切换）
python3 ~/.openclaw/workspace/scripts/model_monitor_v2.py --dry-run

================================================================================
"""

import argparse
import json
import os
import re
import subprocess
import sys
import time
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Optional, Dict, List, Any, Set, Tuple
from collections import defaultdict
import threading
import hashlib

# ==============================================================================
# 配置常量
# ==============================================================================

class Config:
    """系统配置常量"""
    # 路径配置
    HOME = Path.home()
    CONFIG_PATH = HOME / ".openclaw" / "openclaw.json"
    MEMORY_PATH = HOME / ".openclaw" / "workspace" / "memory"
    STATE_PATH = MEMORY_PATH / "model-monitor-v2-state.json"
    LOG_PATH = MEMORY_PATH / "model-monitor-v2.log"
    HISTORY_PATH = MEMORY_PATH / "model-switch-history.jsonl"
    
    # 会话日志路径
    SESSIONS_DIR = HOME / ".openclaw" / "agents" / "main" / "sessions"
    GATEWAY_LOG_DIR = HOME / ".openclaw" / "logs"
    
    # 冷却时间配置（秒）
    COOLDOWN_BILLING = 1800      # billing错误冷却30分钟
    COOLDOWN_AUTH = 900          # auth错误冷却15分钟
    COOLDOWN_RATE_LIMIT = 300    # rate limit冷却5分钟
    COOLDOWN_TIMEOUT = 60        # timeout冷却1分钟
    COOLDOWN_SWITCH = 30         # 切换间隔最小30秒
    
    # 检查配置
    MAX_SESSION_FILES = 5        # 最多检查5个会话文件
    MAX_LINES_PER_FILE = 50      # 每个文件检查最后50行
    MAX_ERROR_HISTORY = 100      # 保留最近100条错误记录
    MAX_SWITCH_HISTORY = 50      # 保留最近50次切换记录
    
    # 默认fallback链
    DEFAULT_FALLBACKS = [
        "bailian/qwen3-coder-plus",
        "zai/glm-4.5-air",
        "zai/glm-4.7",
        "bailian/qwen3.5-plus",
        "bailian/kimi-k2.5"
    ]

# ==============================================================================
# 枚举定义
# ==============================================================================

class ErrorType(Enum):
    """错误类型枚举"""
    BILLING = "billing"           # 额度不足/billing错误
    RATE_LIMIT = "rate_limit"     # 速率限制
    AUTH = "auth"                 # 认证失败
    TIMEOUT = "timeout"           # 超时错误
    NETWORK = "network"           # 网络错误
    UNKNOWN = "unknown"           # 未知错误
    
    def get_cooldown(self) -> int:
        """获取该错误类型的冷却时间"""
        cooldowns = {
            ErrorType.BILLING: Config.COOLDOWN_BILLING,
            ErrorType.RATE_LIMIT: Config.COOLDOWN_RATE_LIMIT,
            ErrorType.AUTH: Config.COOLDOWN_AUTH,
            ErrorType.TIMEOUT: Config.COOLDOWN_TIMEOUT,
            ErrorType.NETWORK: Config.COOLDOWN_TIMEOUT,
            ErrorType.UNKNOWN: Config.COOLDOWN_TIMEOUT,
        }
        return cooldowns.get(self, Config.COOLDOWN_TIMEOUT)

class ModelStatus(Enum):
    """模型状态枚举"""
    HEALTHY = "healthy"           # 健康
    DEGRADED = "degraded"         # 降级（有错误但可用）
    UNHEALTHY = "unhealthy"       # 不健康（需要切换）
    COOLDOWN = "cooldown"         # 冷却中
    UNKNOWN = "unknown"           # 未知

class SwitchReason(Enum):
    """切换原因枚举"""
    BILLING_ERROR = "billing_error"
    RATE_LIMIT = "rate_limit"
    AUTH_ERROR = "auth_error"
    TIMEOUT = "timeout"
    MANUAL = "manual"
    SCHEDULED = "scheduled"
    HEALTH_CHECK = "health_check"
    FALLBACK_TEST = "fallback_test"

# ==============================================================================
# 数据类定义
# ==============================================================================

@dataclass
class ErrorRecord:
    """错误记录"""
    timestamp: str
    model: str
    error_type: ErrorType
    message: str
    source: str = "session_log"
    count: int = 1
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "model": self.model,
            "error_type": self.error_type.value,
            "message": self.message,
            "source": self.source,
            "count": self.count
        }

@dataclass
class ModelInfo:
    """模型信息"""
    id: str
    provider: str
    name: str
    status: ModelStatus = ModelStatus.UNKNOWN
    last_error: Optional[ErrorRecord] = None
    last_used: Optional[str] = None
    error_count: int = 0
    success_count: int = 0
    cooldown_until: Optional[str] = None
    
    def is_in_cooldown(self) -> bool:
        """检查是否在冷却期"""
        if not self.cooldown_until:
            return False
        try:
            until = datetime.fromisoformat(self.cooldown_until)
            return datetime.now() < until
        except:
            return False
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "provider": self.provider,
            "name": self.name,
            "status": self.status.value,
            "last_error": self.last_error.to_dict() if self.last_error else None,
            "last_used": self.last_used,
            "error_count": self.error_count,
            "success_count": self.success_count,
            "cooldown_until": self.cooldown_until
        }

@dataclass
class SwitchRecord:
    """切换记录"""
    timestamp: str
    from_model: str
    to_model: str
    reason: SwitchReason
    success: bool
    duration_ms: int
    error_message: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "from_model": self.from_model,
            "to_model": self.to_model,
            "reason": self.reason.value,
            "success": self.success,
            "duration_ms": self.duration_ms,
            "error_message": self.error_message
        }

@dataclass
class MonitorState:
    """监控状态"""
    version: str = "2.0.0"
    last_check: Optional[str] = None
    current_model: Optional[str] = None
    models: Dict[str, ModelInfo] = field(default_factory=dict)
    error_history: List[ErrorRecord] = field(default_factory=list)
    switch_history: List[SwitchRecord] = field(default_factory=list)
    stats: Dict[str, Any] = field(default_factory=lambda: {
        "total_checks": 0,
        "total_switches": 0,
        "total_errors": 0,
        "start_time": datetime.now().isoformat()
    })

# ==============================================================================
# 日志系统
# ==============================================================================

class StructuredLogger:
    """结构化日志记录器"""
    
    LEVELS = {
        "DEBUG": 0,
        "INFO": 1,
        "WARNING": 2,
        "ERROR": 3,
        "CRITICAL": 4
    }
    
    def __init__(self, log_path: Path, verbose: bool = False):
        self.log_path = log_path
        self.verbose = verbose
        self.memory_path = log_path.parent
        self._lock = threading.Lock()
        self._ensure_directory()
    
    def _ensure_directory(self):
        """确保日志目录存在"""
        self.memory_path.mkdir(parents=True, exist_ok=True)
    
    def _write(self, level: str, component: str, message: str, **kwargs):
        """写入日志"""
        timestamp = datetime.now().isoformat()
        
        # 构建日志条目
        log_entry = {
            "timestamp": timestamp,
            "level": level,
            "component": component,
            "message": message,
            **kwargs
        }
        
        # 格式化输出
        level_emoji = {
            "DEBUG": "🔍",
            "INFO": "ℹ️",
            "WARNING": "⚠️",
            "ERROR": "❌",
            "CRITICAL": "🚨"
        }.get(level, "📝")
        
        formatted = f"[{timestamp}] {level_emoji} [{component}] {message}"
        if kwargs:
            formatted += f" | {json.dumps(kwargs, default=str)}"
        
        # 控制台输出
        if self.verbose or self.LEVELS[level] >= self.LEVELS["INFO"]:
            print(formatted, file=sys.stderr)
        
        # 文件写入
        with self._lock:
            try:
                with open(self.log_path, "a", encoding="utf-8") as f:
                    f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
            except Exception as e:
                print(f"Failed to write log: {e}", file=sys.stderr)
    
    def debug(self, component: str, message: str, **kwargs):
        self._write("DEBUG", component, message, **kwargs)
    
    def info(self, component: str, message: str, **kwargs):
        self._write("INFO", component, message, **kwargs)
    
    def warning(self, component: str, message: str, **kwargs):
        self._write("WARNING", component, message, **kwargs)
    
    def error(self, component: str, message: str, **kwargs):
        self._write("ERROR", component, message, **kwargs)
    
    def critical(self, component: str, message: str, **kwargs):
        self._write("CRITICAL", component, message, **kwargs)

# ==============================================================================
# 错误分类器
# ==============================================================================

class ErrorClassifier:
    """错误分类器 - 识别和分类API错误"""
    
    # 错误模式定义
    PATTERNS = {
        ErrorType.BILLING: [
            r"billing",
            r"insufficient.*credit",
            r"payment.*required",
            r"credit.*balance",
            r"quota.*exceeded",
            r"402\b",
            r"run out of credit",
            r"余额不足",
            r"额度不足",
            r"欠费",
            r"account.*disabled",
            r"subscription.*expired"
        ],
        ErrorType.RATE_LIMIT: [
            r"rate.?limit",
            r"too.*many.*request",
            r"429\b",
            r"throttl",
            r"请求过于频繁",
            r"频率限制",
            r"limit.*exceeded"
        ],
        ErrorType.AUTH: [
            r"unauthorized",
            r"invalid.*api.*key",
            r"401\b",
            r"403\b",
            r"认证失败",
            r"密钥无效",
            r"authentication.*failed",
            r"access.*denied"
        ],
        ErrorType.TIMEOUT: [
            r"timeout",
            r"timed.?out",
            r"502\b",
            r"503\b",
            r"504\b",
            r"超时",
            r"服务不可用",
            r"service.*unavailable",
            r"gateway.*timeout"
        ],
        ErrorType.NETWORK: [
            r"network",
            r"connection",
            r"refused",
            r"reset",
            r"unreachable",
            r"dns",
            r"socket",
            r"econnrefused",
            r"enotfound"
        ]
    }
    
    @classmethod
    def classify(cls, message: str) -> Optional[ErrorType]:
        """分类错误消息"""
        if not message:
            return None
        
        message_lower = message.lower()
        
        for error_type, patterns in cls.PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, message_lower, re.IGNORECASE):
                    return error_type
        
        return ErrorType.UNKNOWN
    
    @classmethod
    def extract_error_details(cls, message: str) -> Dict[str, Any]:
        """提取错误详情"""
        details = {
            "original_message": message[:500],  # 限制长度
            "error_type": None,
            "http_code": None,
            "provider": None
        }
        
        # 提取HTTP状态码
        http_codes = re.findall(r'\b(401|402|403|429|502|503|504)\b', message)
        if http_codes:
            details["http_code"] = int(http_codes[0])
        
        # 提取provider信息
        providers = re.findall(r'(bailian|zai|openai|anthropic|google|moonshot|minimax)', message, re.IGNORECASE)
        if providers:
            details["provider"] = providers[0].lower()
        
        # 分类错误
        error_type = cls.classify(message)
        if error_type:
            details["error_type"] = error_type.value
        
        return details

# ==============================================================================
# 模型注册表
# ==============================================================================

class ModelRegistry:
    """模型注册表 - 管理模型信息和fallback链"""
    
    def __init__(self, config_path: Path, logger: StructuredLogger):
        self.config_path = config_path
        self.logger = logger
        self.config = self._load_config()
        self.models: Dict[str, ModelInfo] = {}
        self.fallback_chain: List[str] = []
        self.current_model: Optional[str] = None
        self._initialize()
    
    def _load_config(self) -> Dict[str, Any]:
        """加载OpenClaw配置"""
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            self.logger.error("ModelRegistry", f"Failed to load config: {e}")
        return {}
    
    def _initialize(self):
        """初始化模型信息"""
        # 获取fallback链
        agents_config = self.config.get("agents", {}).get("defaults", {})
        model_config = agents_config.get("model", {})
        
        self.fallback_chain = model_config.get("fallbacks", Config.DEFAULT_FALLBACKS)
        self.current_model = model_config.get("primary")
        
        if not self.current_model and self.fallback_chain:
            self.current_model = self.fallback_chain[0]
        
        # 初始化模型信息
        for model_id in self.fallback_chain:
            provider, name = self._parse_model_id(model_id)
            self.models[model_id] = ModelInfo(
                id=model_id,
                provider=provider,
                name=name
            )
        
        self.logger.info("ModelRegistry", 
                        f"Initialized with {len(self.fallback_chain)} models",
                        current=self.current_model,
                        fallbacks=self.fallback_chain)
    
    def _parse_model_id(self, model_id: str) -> Tuple[str, str]:
        """解析模型ID为provider和name"""
        parts = model_id.split("/", 1)
        if len(parts) == 2:
            return parts[0], parts[1]
        return "unknown", model_id
    
    def get_current_model(self) -> Optional[str]:
        """获取当前模型"""
        return self.current_model
    
    def get_fallback_chain(self) -> List[str]:
        """获取fallback链"""
        return self.fallback_chain.copy()
    
    def get_model_info(self, model_id: str) -> Optional[ModelInfo]:
        """获取模型信息"""
        return self.models.get(model_id)
    
    def update_model_status(self, model_id: str, status: ModelStatus, 
                           error: Optional[ErrorRecord] = None):
        """更新模型状态"""
        if model_id not in self.models:
            provider, name = self._parse_model_id(model_id)
            self.models[model_id] = ModelInfo(id=model_id, provider=provider, name=name)
        
        model = self.models[model_id]
        model.status = status
        model.last_used = datetime.now().isoformat()
        
        if error:
            model.last_error = error
            model.error_count += 1
        else:
            model.success_count += 1
        
        self.logger.debug("ModelRegistry", 
                         f"Updated model status: {model_id} -> {status.value}",
                         error_count=model.error_count,
                         success_count=model.success_count)
    
    def set_cooldown(self, model_id: str, error_type: ErrorType):
        """设置模型冷却"""
        if model_id not in self.models:
            return
        
        cooldown_seconds = error_type.get_cooldown()
        cooldown_until = datetime.now() + timedelta(seconds=cooldown_seconds)
        
        self.models[model_id].cooldown_until = cooldown_until.isoformat()
        self.models[model_id].status = ModelStatus.COOLDOWN
        
        self.logger.info("ModelRegistry",
                        f"Set cooldown for {model_id}: {cooldown_seconds}s",
                        until=cooldown_until.isoformat())
    
    def get_available_models(self) -> List[str]:
        """获取可用模型列表（按优先级排序）"""
        available = []
        
        for model_id in self.fallback_chain:
            model = self.models.get(model_id)
            if not model:
                available.append(model_id)
                continue
            
            if model.is_in_cooldown():
                self.logger.debug("ModelRegistry", 
                                f"Skipping {model_id} (in cooldown)")
                continue
            
            if model.status == ModelStatus.UNHEALTHY:
                continue
            
            available.append(model_id)
        
        return available
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "current_model": self.current_model,
            "fallback_chain": self.fallback_chain,
            "models": {k: v.to_dict() for k, v in self.models.items()}
        }

# ==============================================================================
# 健康检查器
# ==============================================================================

class HealthChecker:
    """健康检查器 - 主动和被动检查模型健康状态"""
    
    def __init__(self, registry: ModelRegistry, logger: StructuredLogger):
        self.registry = registry
        self.logger = logger
        self.errors_found: List[ErrorRecord] = []
    
    def check_session_logs(self) -> List[ErrorRecord]:
        """检查会话日志中的错误"""
        errors = []
        
        if not Config.SESSIONS_DIR.exists():
            self.logger.debug("HealthChecker", "Sessions directory not found")
            return errors
        
        try:
            # 获取最新的会话文件
            session_files = sorted(
                Config.SESSIONS_DIR.glob("*.jsonl"),
                key=lambda p: p.stat().st_mtime,
                reverse=True
            )[:Config.MAX_SESSION_FILES]
            
            self.logger.debug("HealthChecker", 
                            f"Checking {len(session_files)} session files")
            
            for session_file in session_files:
                try:
                    file_errors = self._check_single_session(session_file)
                    errors.extend(file_errors)
                except Exception as e:
                    self.logger.error("HealthChecker", 
                                    f"Error checking session file {session_file}: {e}")
        
        except Exception as e:
            self.logger.error("HealthChecker", f"Error checking sessions: {e}")
        
        self.errors_found = errors
        return errors
    
    def _check_single_session(self, session_file: Path) -> List[ErrorRecord]:
        """检查单个会话文件"""
        errors = []
        
        try:
            with open(session_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # 只检查最后N行
            lines_to_check = lines[-Config.MAX_LINES_PER_FILE:]
            
            for line_num, line in enumerate(lines_to_check, start=len(lines)-len(lines_to_check)+1):
                try:
                    data = json.loads(line)
                    
                    # 检查toolResult中的错误
                    if data.get("message", {}).get("role") == "toolResult":
                        content = data.get("message", {}).get("content", [])
                        model = data.get("message", {}).get("model", "unknown")
                        
                        for item in content:
                            if item.get("type") == "text":
                                text = item.get("text", "")
                                error_type = ErrorClassifier.classify(text)
                                
                                if error_type:
                                    error = ErrorRecord(
                                        timestamp=datetime.now().isoformat(),
                                        model=model,
                                        error_type=error_type,
                                        message=text[:300],
                                        source=f"{session_file.name}:{line_num}"
                                    )
                                    errors.append(error)
                                    
                                    self.logger.warning("HealthChecker",
                                                      f"Found {error_type.value} error in {model}",
                                                      file=session_file.name,
                                                      line=line_num,
                                                      message_preview=text[:100])
                
                except json.JSONDecodeError:
                    continue
                except Exception as e:
                    self.logger.debug("HealthChecker", 
                                    f"Error parsing line in {session_file.name}:{line_num}: {e}")
        
        except Exception as e:
            self.logger.error("HealthChecker", 
                            f"Error reading session file {session_file}: {e}")
        
        return errors
    
    def check_gateway_logs(self) -> List[ErrorRecord]:
        """检查gateway日志中的错误"""
        errors = []
        
        # 使用openclaw logs命令获取日志
        try:
            result = subprocess.run(
                ["openclaw", "logs", "--limit", "100", "--plain"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                self.logger.debug("HealthChecker", 
                                f"Failed to get gateway logs: {result.stderr}")
                return errors
            
            # 分析日志内容
            for line in result.stdout.split("\n"):
                error_type = ErrorClassifier.classify(line)
                if error_type:
                    # 尝试提取模型信息
                    model_match = re.search(r'model[=:](\S+)', line)
                    model = model_match.group(1) if model_match else "unknown"
                    
                    error = ErrorRecord(
                        timestamp=datetime.now().isoformat(),
                        model=model,
                        error_type=error_type,
                        message=line[:300],
                        source="gateway_log"
                    )
                    errors.append(error)
                    
                    self.logger.warning("HealthChecker",
                                      f"Found {error_type.value} error in gateway logs",
                                      model=model)
        
        except Exception as e:
            self.logger.error("HealthChecker", f"Error checking gateway logs: {e}")
        
        return errors
    
    def perform_health_check(self, model_id: Optional[str] = None) -> bool:
        """执行主动健康检查"""
        target_model = model_id or self.registry.get_current_model()
        
        if not target_model:
            return False
        
        self.logger.info("HealthChecker", 
                        f"Performing health check for {target_model}")
        
        try:
            # 使用openclaw models status检查
            result = subprocess.run(
                ["openclaw", "models", "status", "--check"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            is_healthy = result.returncode == 0
            
            if is_healthy:
                self.registry.update_model_status(target_model, ModelStatus.HEALTHY)
                self.logger.info("HealthChecker", 
                               f"Health check passed for {target_model}")
            else:
                self.registry.update_model_status(target_model, ModelStatus.UNHEALTHY)
                self.logger.warning("HealthChecker", 
                                  f"Health check failed for {target_model}",
                                  stderr=result.stderr[:200])
            
            return is_healthy
        
        except Exception as e:
            self.logger.error("HealthChecker", 
                            f"Error during health check for {target_model}: {e}")
            return False

# ==============================================================================
# 自动切换器
# ==============================================================================

class AutoSwitcher:
    """自动切换器 - 执行模型切换操作"""
    
    def __init__(self, registry: ModelRegistry, logger: StructuredLogger):
        self.registry = registry
        self.logger = logger
        self.last_switch_time: Optional[datetime] = None
        self.switch_history: List[SwitchRecord] = []
    
    def can_switch(self) -> bool:
        """检查是否可以切换（冷却检查）"""
        if not self.last_switch_time:
            return True
        
        elapsed = (datetime.now() - self.last_switch_time).total_seconds()
        can_switch = elapsed >= Config.COOLDOWN_SWITCH
        
        if not can_switch:
            self.logger.debug("AutoSwitcher", 
                            f"Switch cooldown active: {Config.COOLDOWN_SWITCH - elapsed:.1f}s remaining")
        
        return can_switch
    
    def switch_model(self, target_model: str, reason: SwitchReason, 
                    dry_run: bool = False) -> Tuple[bool, Optional[str]]:
        """切换到指定模型"""
        current_model = self.registry.get_current_model()
        
        if current_model == target_model:
            return True, None
        
        if not self.can_switch():
            return False, "Switch cooldown active"
        
        self.logger.info("AutoSwitcher",
                        f"Initiating switch from {current_model} to {target_model}",
                        reason=reason.value,
                        dry_run=dry_run)
        
        if dry_run:
            # 测试模式，不实际切换
            record = SwitchRecord(
                timestamp=datetime.now().isoformat(),
                from_model=current_model or "unknown",
                to_model=target_model,
                reason=reason,
                success=True,
                duration_ms=0,
                error_message="DRY RUN - No actual switch performed"
            )
            self.switch_history.append(record)
            return True, None
        
        # 执行实际切换
        start_time = time.time()
        
        try:
            result = subprocess.run(
                ["openclaw", "models", "set", target_model],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            duration_ms = int((time.time() - start_time) * 1000)
            success = result.returncode == 0
            
            record = SwitchRecord(
                timestamp=datetime.now().isoformat(),
                from_model=current_model or "unknown",
                to_model=target_model,
                reason=reason,
                success=success,
                duration_ms=duration_ms,
                error_message=result.stderr[:500] if not success else None
            )
            self.switch_history.append(record)
            
            if success:
                self.last_switch_time = datetime.now()
                self.registry.current_model = target_model
                self.registry.update_model_status(target_model, ModelStatus.HEALTHY)
                
                self.logger.info("AutoSwitcher",
                               f"✓ Successfully switched to {target_model}",
                               duration_ms=duration_ms)
            else:
                self.logger.error("AutoSwitcher",
                                f"✗ Failed to switch to {target_model}",
                                stderr=result.stderr[:200])
            
            return success, result.stderr if not success else None
        
        except Exception as e:
            duration_ms = int((time.time() - start_time) * 1000)
            
            record = SwitchRecord(
                timestamp=datetime.now().isoformat(),
                from_model=current_model or "unknown",
                to_model=target_model,
                reason=reason,
                success=False,
                duration_ms=duration_ms,
                error_message=str(e)[:500]
            )
            self.switch_history.append(record)
            
            self.logger.error("AutoSwitcher", 
                            f"Exception during switch to {target_model}: {e}")
            return False, str(e)
    
    def auto_switch_on_error(self, error: ErrorRecord, 
                            dry_run: bool = False) -> Tuple[bool, Optional[str]]:
        """根据错误自动切换模型"""
        error_model = error.model
        error_type = error.error_type
        
        # 设置错误模型的冷却
        self.registry.set_cooldown(error_model, error_type)
        self.registry.update_model_status(error_model, ModelStatus.UNHEALTHY)
        
        # 获取可用模型
        available = self.registry.get_available_models()
        
        if not available:
            self.logger.critical("AutoSwitcher",
                               "No available models for fallback!")
            return False, "No available models"
        
        # 选择最佳fallback模型
        target_model = None
        for model in available:
            if model != error_model:
                target_model = model
                break
        
        if not target_model:
            self.logger.warning("AutoSwitcher",
                              "All models unavailable, using first in chain")
            target_model = self.registry.fallback_chain[0]
        
        # 确定切换原因
        reason_map = {
            ErrorType.BILLING: SwitchReason.BILLING_ERROR,
            ErrorType.RATE_LIMIT: SwitchReason.RATE_LIMIT,
            ErrorType.AUTH: SwitchReason.AUTH_ERROR,
            ErrorType.TIMEOUT: SwitchReason.TIMEOUT,
            ErrorType.NETWORK: SwitchReason.TIMEOUT,
            ErrorType.UNKNOWN: SwitchReason.HEALTH_CHECK
        }
        reason = reason_map.get(error_type, SwitchReason.HEALTH_CHECK)
        
        return self.switch_model(target_model, reason, dry_run)
    
    def get_switch_history(self) -> List[SwitchRecord]:
        """获取切换历史"""
        return self.switch_history.copy()

# ==============================================================================
# 状态管理器
# ==============================================================================

class StateManager:
    """状态管理器 - 持久化和恢复监控状态"""
    
    def __init__(self, state_path: Path, history_path: Path, logger: StructuredLogger):
        self.state_path = state_path
        self.history_path = history_path
        self.logger = logger
        self.state = MonitorState()
        self._load()
    
    def _load(self):
        """加载状态"""
        try:
            if self.state_path.exists():
                with open(self.state_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                self.state.version = data.get("version", "2.0.0")
                self.state.last_check = data.get("last_check")
                self.state.current_model = data.get("current_model")
                self.state.stats = data.get("stats", self.state.stats)
                
                # 加载模型信息
                for model_id, model_data in data.get("models", {}).items():
                    self.state.models[model_id] = ModelInfo(
                        id=model_data["id"],
                        provider=model_data["provider"],
                        name=model_data["name"],
                        status=ModelStatus(model_data["status"]),
                        error_count=model_data.get("error_count", 0),
                        success_count=model_data.get("success_count", 0),
                        cooldown_until=model_data.get("cooldown_until"),
                        last_used=model_data.get("last_used")
                    )
                
                self.logger.debug("StateManager", 
                                f"Loaded state with {len(self.state.models)} models")
        
        except Exception as e:
            self.logger.error("StateManager", f"Failed to load state: {e}")
    
    def save(self):
        """保存状态"""
        try:
            self.state_path.parent.mkdir(parents=True, exist_ok=True)
            
            data = {
                "version": self.state.version,
                "last_check": datetime.now().isoformat(),
                "current_model": self.state.current_model,
                "models": {k: v.to_dict() for k, v in self.state.models.items()},
                "stats": self.state.stats
            }
            
            with open(self.state_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            self.logger.debug("StateManager", "State saved successfully")
        
        except Exception as e:
            self.logger.error("StateManager", f"Failed to save state: {e}")
    
    def append_error(self, error: ErrorRecord):
        """追加错误记录"""
        self.state.error_history.append(error)
        
        # 限制历史记录数量
        if len(self.state.error_history) > Config.MAX_ERROR_HISTORY:
            self.state.error_history = self.state.error_history[-Config.MAX_ERROR_HISTORY:]
        
        self.state.stats["total_errors"] += 1
    
    def append_switch(self, record: SwitchRecord):
        """追加切换记录"""
        try:
            self.history_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.history_path, 'a', encoding='utf-8') as f:
                f.write(json.dumps(record.to_dict(), ensure_ascii=False) + "\n")
            
            self.state.stats["total_switches"] += 1
        
        except Exception as e:
            self.logger.error("StateManager", f"Failed to append switch record: {e}")
    
    def increment_check_count(self):
        """增加检查计数"""
        self.state.stats["total_checks"] += 1
    
    def update_current_model(self, model_id: str):
        """更新当前模型"""
        self.state.current_model = model_id

# ==============================================================================
# 主监控器
# ==============================================================================

class ModelMonitor:
    """主监控器 - 协调所有组件"""
    
    def __init__(self, verbose: bool = False, dry_run: bool = False):
        self.verbose = verbose
        self.dry_run = dry_run
        
        # 初始化组件
        self.logger = StructuredLogger(Config.LOG_PATH, verbose)
        self.state_manager = StateManager(Config.STATE_PATH, Config.HISTORY_PATH, self.logger)
        self.registry = ModelRegistry(Config.CONFIG_PATH, self.logger)
        self.checker = HealthChecker(self.registry, self.logger)
        self.switcher = AutoSwitcher(self.registry, self.logger)
        
        # 恢复状态
        self._restore_state()
        
        self.logger.info("ModelMonitor", 
                        "Model Monitor v2.0 initialized",
                        dry_run=dry_run,
                        verbose=verbose)
    
    def _restore_state(self):
        """从状态文件恢复"""
        # 恢复模型状态
        for model_id, model_info in self.state_manager.state.models.items():
            if model_id in self.registry.models:
                self.registry.models[model_id] = model_info
        
        # 恢复当前模型
        if self.state_manager.state.current_model:
            self.registry.current_model = self.state_manager.state.current_model
    
    def run(self, check_all: bool = False) -> Dict[str, Any]:
        """运行监控检查"""
        self.state_manager.increment_check_count()
        
        result = {
            "status": "ok",
            "timestamp": datetime.now().isoformat(),
            "current_model": self.registry.get_current_model(),
            "actions": [],
            "errors_detected": [],
            "switches_performed": [],
            "models_status": {}
        }
        
        self.logger.info("ModelMonitor", "Starting monitoring cycle")
        
        # 1. 检查会话日志错误
        session_errors = self.checker.check_session_logs()
        
        # 2. 检查gateway日志错误
        gateway_errors = self.checker.check_gateway_logs()
        
        # 合并所有错误
        all_errors = session_errors + gateway_errors
        
        # 去重（基于模型和错误类型）
        seen = set()
        unique_errors = []
        for error in all_errors:
            key = (error.model, error.error_type.value)
            if key not in seen:
                seen.add(key)
                unique_errors.append(error)
        
        # 3. 处理错误
        critical_errors = []
        for error in unique_errors:
            result["errors_detected"].append(error.to_dict())
            self.state_manager.append_error(error)
            
            self.logger.warning("ModelMonitor",
                              f"Detected {error.error_type.value} error",
                              model=error.model,
                              source=error.source)
            
            # billing和auth错误需要立即切换
            if error.error_type in [ErrorType.BILLING, ErrorType.AUTH]:
                critical_errors.append(error)
        
        # 4. 处理关键错误（自动切换）
        for error in critical_errors:
            self.logger.info("ModelMonitor",
                           f"Processing critical error: {error.error_type.value}")
            
            success, error_msg = self.switcher.auto_switch_on_error(error, self.dry_run)
            
            if success:
                action = f"Auto-switched due to {error.error_type.value}"
                result["actions"].append(action)
                result["switches_performed"].append({
                    "from": error.model,
                    "reason": error.error_type.value,
                    "dry_run": self.dry_run
                })
                
                # 更新当前模型
                result["current_model"] = self.registry.get_current_model()
                self.state_manager.update_current_model(result["current_model"])
            else:
                self.logger.error("ModelMonitor",
                                f"Failed to auto-switch: {error_msg}")
        
        # 5. 主动健康检查（如果配置了check_all）
        if check_all:
            self.logger.info("ModelMonitor", "Performing health checks on all models")
            for model_id in self.registry.fallback_chain:
                if model_id != self.registry.get_current_model():
                    self.checker.perform_health_check(model_id)
        
        # 6. 收集模型状态
        for model_id, model_info in self.registry.models.items():
            result["models_status"][model_id] = model_info.to_dict()
        
        # 7. 保存状态
        self.state_manager.save()
        
        # 8. 保存切换历史
        for record in self.switcher.get_switch_history():
            self.state_manager.append_switch(record)
        
        # 9. 确定最终状态
        if critical_errors and not result["switches_performed"]:
            result["status"] = "critical_errors_unresolved"
        elif result["errors_detected"]:
            result["status"] = "errors_detected"
        
        self.logger.info("ModelMonitor",
                        f"Monitoring cycle completed: {result['status']}",
                        errors=len(result["errors_detected"]),
                        switches=len(result["switches_performed"]))
        
        return result
    
    def get_status_report(self) -> Dict[str, Any]:
        """获取状态报告"""
        return {
            "version": "2.0.0",
            "timestamp": datetime.now().isoformat(),
            "current_model": self.registry.get_current_model(),
            "fallback_chain": self.registry.get_fallback_chain(),
            "models": {k: v.to_dict() for k, v in self.registry.models.items()},
            "stats": self.state_manager.state.stats,
            "recent_errors": [e.to_dict() for e in self.state_manager.state.error_history[-10:]],
            "config": {
                "cooldown_billing": Config.COOLDOWN_BILLING,
                "cooldown_auth": Config.COOLDOWN_AUTH,
                "cooldown_rate_limit": Config.COOLDOWN_RATE_LIMIT,
                "cooldown_switch": Config.COOLDOWN_SWITCH
            }
        }

# ==============================================================================
# 命令行接口
# ==============================================================================

def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="OpenClaw Model Monitor v2.0 - 自主模型健康监控与自动切换系统",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  # 基本检查
  python3 model_monitor_v2.py
  
  # 详细模式
  python3 model_monitor_v2.py --verbose
  
  # 检查所有模型
  python3 model_monitor_v2.py --check-all
  
  # 测试模式（不实际切换）
  python3 model_monitor_v2.py --dry-run
  
  # 获取状态报告
  python3 model_monitor_v2.py --status
  
  # 查看帮助
  python3 model_monitor_v2.py --help
        """
    )
    
    parser.add_argument("-v", "--verbose", 
                       action="store_true",
                       help="启用详细日志输出")
    parser.add_argument("-c", "--check-all",
                       action="store_true", 
                       help="检查所有模型，不只是当前模型")
    parser.add_argument("-d", "--dry-run",
                       action="store_true",
                       help="测试模式，不实际执行切换")
    parser.add_argument("-s", "--status",
                       action="store_true",
                       help="显示状态报告并退出")
    parser.add_argument("--version",
                       action="version",
                       version="%(prog)s 2.0.0")
    
    args = parser.parse_args()
    
    # 创建监控器
    monitor = ModelMonitor(verbose=args.verbose, dry_run=args.dry_run)
    
    # 显示状态报告
    if args.status:
        report = monitor.get_status_report()
        print(json.dumps(report, indent=2, ensure_ascii=False))
        sys.exit(0)
    
    # 运行监控
    result = monitor.run(check_all=args.check_all)
    
    # 输出结果
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    # 根据结果设置退出码
    if result["status"] == "critical_errors_unresolved":
        sys.exit(2)
    elif result["status"] == "errors_detected":
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == "__main__":
    main()
