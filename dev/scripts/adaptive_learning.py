#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自适应学习框架 v1.0

基于 adaptive-agent skill 和现代 AI 架构模式，实现自我学习和进化能力。

功能:
- 从交互中学习模式
- 优化响应策略
- 适应用户偏好
- 持续自我改进
"""

import json
import os
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional, Any
from enum import Enum


# ============================================================================
# 配置
# ============================================================================

class Config:
    """配置常量"""
    
    # 路径
    WORKSPACE = Path.home() / ".openclaw" / "workspace"
    MEMORY_DIR = WORKSPACE / "memory"
    STATE_FILE = MEMORY_DIR / "adaptive-agent-state.json"
    LEARNING_LOG = MEMORY_DIR / "adaptive-learning.log"
    
    # 学习参数
    LEARNING_RATE = 0.1  # 学习率
    MEMORY_SIZE = 1000   # 最大记忆条目
    CONFIDENCE_THRESHOLD = 0.7  # 置信度阈值
    
    # 评估参数
    SUCCESS_THRESHOLD = 0.8  # 成功阈值
    MIN_SAMPLES = 5  # 最小样本数
    
    # 日志
    LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR


# ============================================================================
# 数据类型
# ============================================================================

class LearningType(str, Enum):
    """学习类型"""
    PATTERN = "pattern"           # 模式学习
    PREFERENCE = "preference"     # 偏好学习
    OPTIMIZATION = "optimization" # 优化学习
    CORRECTION = "correction"     # 纠正学习
    FEEDBACK = "feedback"         # 反馈学习


class ImportanceLevel(str, Enum):
    """重要性级别"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class Learning:
    """学习记录"""
    id: str
    timestamp: str
    type: str
    content: str
    confidence: float
    importance: str
    source: str
    applied: bool = False
    verified: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class Pattern:
    """模式记录"""
    id: str
    name: str
    description: str
    occurrences: int = 1
    success_rate: float = 0.0
    last_used: Optional[str] = None
    context: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class Metric:
    """性能指标"""
    timestamp: str
    metric_type: str
    value: float
    delta: Optional[float] = None
    context: Dict[str, Any] = field(default_factory=dict)


# ============================================================================
# 组件
# ============================================================================

class StructuredLogger:
    """结构化日志器"""
    
    def __init__(self, log_file: Path):
        self.log_file = log_file
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
    
    def log(self, level: str, component: str, message: str, data: Optional[Dict] = None):
        """记录日志"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "component": component,
            "message": message,
            "data": data or {}
        }
        
        # 写入文件
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        
        # 控制台输出
        emoji = {"DEBUG": "🔍", "INFO": "ℹ️", "WARNING": "⚠️", "ERROR": "❌"}.get(level, "📝")
        print(f"[{entry['timestamp']}] {emoji} [{component}] {message}")
    
    def debug(self, component: str, message: str, data: Optional[Dict] = None):
        self.log("DEBUG", component, message, data)
    
    def info(self, component: str, message: str, data: Optional[Dict] = None):
        self.log("INFO", component, message, data)
    
    def warning(self, component: str, message: str, data: Optional[Dict] = None):
        self.log("WARNING", component, message, data)
    
    def error(self, component: str, message: str, data: Optional[Dict] = None):
        self.log("ERROR", component, message, data)


class PatternRecognizer:
    """模式识别器"""
    
    def __init__(self, logger: StructuredLogger):
        self.logger = logger
        self.patterns: Dict[str, Pattern] = {}
    
    def record_pattern(self, name: str, description: str, context: Dict, success: bool):
        """记录模式"""
        pattern_id = f"pattern_{name}_{len(self.patterns)}"
        
        if pattern_id in self.patterns:
            pattern = self.patterns[pattern_id]
            pattern.occurrences += 1
            # 更新成功率
            total = pattern.occurrences
            successes = int(pattern.success_rate * (total - 1)) + (1 if success else 0)
            pattern.success_rate = successes / total
            pattern.last_used = datetime.now().isoformat()
        else:
            pattern = Pattern(
                id=pattern_id,
                name=name,
                description=description,
                occurrences=1,
                success_rate=1.0 if success else 0.0,
                last_used=datetime.now().isoformat(),
                context=context
            )
            self.patterns[pattern_id] = pattern
        
        self.logger.info(
            "PatternRecognizer",
            f"Recorded pattern: {name}",
            {"success": success, "occurrences": pattern.occurrences}
        )
        
        return pattern
    
    def get_successful_patterns(self, min_success_rate: float = 0.7) -> List[Pattern]:
        """获取成功模式"""
        return [
            p for p in self.patterns.values()
            if p.occurrences >= Config.MIN_SAMPLES and p.success_rate >= min_success_rate
        ]
    
    def analyze_patterns(self) -> Dict:
        """分析模式"""
        if not self.patterns:
            return {"total": 0, "successful": 0, "average_success_rate": 0.0}
        
        successful = self.get_successful_patterns()
        avg_success_rate = sum(p.success_rate for p in self.patterns.values()) / len(self.patterns)
        
        return {
            "total": len(self.patterns),
            "successful": len(successful),
            "average_success_rate": round(avg_success_rate, 3),
            "top_patterns": [
                {"name": p.name, "success_rate": p.success_rate, "occurrences": p.occurrences}
                for p in sorted(self.patterns.values(), key=lambda x: x.success_rate, reverse=True)[:5]
            ]
        }


class PreferenceLearner:
    """偏好学习器"""
    
    def __init__(self, logger: StructuredLogger):
        self.logger = logger
        self.preferences: Dict[str, Any] = {}
        self.confidence: Dict[str, float] = {}
    
    def learn_preference(self, key: str, value: Any, confidence_delta: float = 0.1):
        """学习偏好"""
        old_value = self.preferences.get(key)
        old_confidence = self.confidence.get(key, 0.0)
        
        # 更新偏好
        self.preferences[key] = value
        new_confidence = min(1.0, old_confidence + confidence_delta)
        self.confidence[key] = new_confidence
        
        self.logger.info(
            "PreferenceLearner",
            f"Learned preference: {key} = {value}",
            {"confidence": new_confidence, "old_value": old_value}
        )
    
    def get_preference(self, key: str, default: Any = None) -> Any:
        """获取偏好"""
        confidence = self.confidence.get(key, 0.0)
        if confidence < Config.CONFIDENCE_THRESHOLD:
            return default
        return self.preferences.get(key, default)
    
    def get_all_preferences(self) -> Dict:
        """获取所有偏好"""
        return {
            key: {
                "value": value,
                "confidence": self.confidence.get(key, 0.0)
            }
            for key, value in self.preferences.items()
            if self.confidence.get(key, 0.0) >= Config.CONFIDENCE_THRESHOLD
        }


class PerformanceOptimizer:
    """性能优化器"""
    
    def __init__(self, logger: StructuredLogger):
        self.logger = logger
        self.metrics: List[Metric] = []
        self.baselines: Dict[str, float] = {}
    
    def record_metric(self, metric_type: str, value: float, context: Optional[Dict] = None):
        """记录指标"""
        # 计算变化
        baseline = self.baselines.get(metric_type)
        delta = (value - baseline) if baseline else None
        
        metric = Metric(
            timestamp=datetime.now().isoformat(),
            metric_type=metric_type,
            value=value,
            delta=delta,
            context=context or {}
        )
        self.metrics.append(metric)
        
        # 更新基线
        if baseline:
            # 移动平均
            self.baselines[metric_type] = baseline * 0.9 + value * 0.1
        else:
            self.baselines[metric_type] = value
        
        self.logger.info(
            "PerformanceOptimizer",
            f"Recorded metric: {metric_type} = {value}",
            {"delta": delta, "baseline": baseline}
        )
    
    def get_metrics_summary(self) -> Dict:
        """获取指标摘要"""
        if not self.metrics:
            return {}
        
        by_type = {}
        for metric in self.metrics:
            if metric.metric_type not in by_type:
                by_type[metric.metric_type] = []
            by_type[metric.metric_type].append(metric.value)
        
        return {
            metric_type: {
                "count": len(values),
                "average": sum(values) / len(values),
                "min": min(values),
                "max": max(values),
                "latest": values[-1],
                "baseline": self.baselines.get(metric_type)
            }
            for metric_type, values in by_type.items()
        }


class StateManager:
    """状态管理器"""
    
    def __init__(self, state_file: Path, logger: StructuredLogger):
        self.state_file = state_file
        self.logger = logger
        self.state = self.load()
    
    def load(self) -> Dict:
        """加载状态"""
        if self.state_file.exists():
            try:
                with open(self.state_file, "r", encoding="utf-8") as f:
                    state = json.load(f)
                self.logger.info("StateManager", "Loaded state", {"file": str(self.state_file)})
                return state
            except Exception as e:
                self.logger.error("StateManager", f"Failed to load state: {e}")
        
        # 默认状态
        return {
            "version": "1.0.0",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "learnings": [],
            "patterns": {},
            "preferences": {},
            "metrics": [],
            "stats": {
                "total_learnings": 0,
                "total_patterns": 0,
                "total_optimizations": 0
            }
        }
    
    def save(self):
        """保存状态"""
        self.state["updated_at"] = datetime.now().isoformat()
        
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.state_file, "w", encoding="utf-8") as f:
            json.dump(self.state, f, ensure_ascii=False, indent=2)
        
        self.logger.info("StateManager", "Saved state", {"file": str(self.state_file)})
    
    def add_learning(self, learning: Learning):
        """添加学习"""
        self.state["learnings"].append(learning.to_dict())
        self.state["stats"]["total_learnings"] += 1
        
        # 限制大小
        if len(self.state["learnings"]) > Config.MEMORY_SIZE:
            self.state["learnings"] = self.state["learnings"][-Config.MEMORY_SIZE:]
    
    def update_patterns(self, patterns: Dict[str, Pattern]):
        """更新模式"""
        self.state["patterns"] = {k: v.to_dict() for k, v in patterns.items()}
        self.state["stats"]["total_patterns"] = len(patterns)
    
    def update_preferences(self, preferences: Dict):
        """更新偏好"""
        self.state["preferences"] = preferences
    
    def get_stats(self) -> Dict:
        """获取统计"""
        return self.state["stats"]


# ============================================================================
# 主控制器
# ============================================================================

class AdaptiveAgent:
    """自适应代理"""
    
    def __init__(self):
        self.logger = StructuredLogger(Config.LEARNING_LOG)
        self.pattern_recognizer = PatternRecognizer(self.logger)
        self.preference_learner = PreferenceLearner(self.logger)
        self.performance_optimizer = PerformanceOptimizer(self.logger)
        self.state_manager = StateManager(Config.STATE_FILE, self.logger)
        
        self.logger.info("AdaptiveAgent", "Initialized adaptive learning framework")
    
    def learn_from_interaction(self, interaction_type: str, success: bool, context: Dict):
        """从交互中学习"""
        # 记录模式
        pattern_name = f"interaction_{interaction_type}"
        self.pattern_recognizer.record_pattern(
            name=pattern_name,
            description=f"Interaction pattern for {interaction_type}",
            context=context,
            success=success
        )
        
        # 记录指标
        self.performance_optimizer.record_metric(
            metric_type=f"success_rate_{interaction_type}",
            value=1.0 if success else 0.0,
            context=context
        )
        
        # 创建学习记录
        learning = Learning(
            id=f"learning_{datetime.now().timestamp()}",
            timestamp=datetime.now().isoformat(),
            type=LearningType.PATTERN.value,
            content=f"Learned from {interaction_type} interaction",
            confidence=0.8 if success else 0.3,
            importance=ImportanceLevel.MEDIUM.value,
            source="interaction",
            metadata=context
        )
        self.state_manager.add_learning(learning)
        
        # 保存状态
        self.state_manager.update_patterns(self.pattern_recognizer.patterns)
        self.state_manager.save()
    
    def learn_preference(self, key: str, value: Any, confidence: float = 0.1):
        """学习偏好"""
        self.preference_learner.learn_preference(key, value, confidence)
        self.state_manager.update_preferences(self.preference_learner.get_all_preferences())
        self.state_manager.save()
    
    def get_recommendations(self) -> List[str]:
        """获取优化建议"""
        recommendations = []
        
        # 基于模式分析
        pattern_analysis = self.pattern_recognizer.analyze_patterns()
        if pattern_analysis["total"] > 0:
            recommendations.append(
                f"已识别 {pattern_analysis['successful']}/{pattern_analysis['total']} "
                f"个成功模式 (成功率：{pattern_analysis['average_success_rate']:.1%})"
            )
        
        # 基于偏好
        preferences = self.preference_learner.get_all_preferences()
        if preferences:
            recommendations.append(f"已学习 {len(preferences)} 个用户偏好")
        
        # 基于性能
        metrics = self.performance_optimizer.get_metrics_summary()
        if metrics:
            for metric_type, data in metrics.items():
                if data.get("delta", 0) > 0:
                    recommendations.append(f"{metric_type} 提升了 {data['delta']:.2f}")
        
        return recommendations
    
    def get_status(self) -> Dict:
        """获取状态"""
        return {
            "version": "1.0.0",
            "timestamp": datetime.now().isoformat(),
            "stats": self.state_manager.get_stats(),
            "pattern_analysis": self.pattern_recognizer.analyze_patterns(),
            "preferences": self.preference_learner.get_all_preferences(),
            "metrics": self.performance_optimizer.get_metrics_summary(),
            "recommendations": self.get_recommendations()
        }


# ============================================================================
# CLI
# ============================================================================

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="自适应学习框架")
    parser.add_argument("--status", action="store_true", help="显示状态")
    parser.add_argument("--learn", type=str, help="学习偏好 (格式：key=value)")
    parser.add_argument("--simulate", action="store_true", help="模拟交互学习")
    parser.add_argument("--verbose", "-v", action="store_true", help="详细输出")
    
    args = parser.parse_args()
    
    agent = AdaptiveAgent()
    
    if args.status:
        status = agent.get_status()
        print(json.dumps(status, ensure_ascii=False, indent=2))
    
    elif args.learn:
        if "=" in args.learn:
            key, value = args.learn.split("=", 1)
            agent.learn_preference(key.strip(), value.strip())
            print(f"✓ 已学习偏好：{key} = {value}")
        else:
            print("❌ 格式错误，请使用 key=value 格式")
    
    elif args.simulate:
        print("📝 模拟交互学习...")
        for i in range(5):
            success = i % 2 == 0  # 交替成功/失败
            agent.learn_from_interaction(
                interaction_type="coding_task",
                success=success,
                context={"iteration": i, "complexity": "medium"}
            )
        
        # 学习一些偏好
        agent.learn_preference("response_style", "detailed", 0.2)
        agent.learn_preference("code_comments", "true", 0.3)
        agent.learn_preference("preferred_model", "bailian/qwen3.5-plus", 0.5)
        
        print("\n📊 当前状态:")
        status = agent.get_status()
        print(f"  总学习数：{status['stats']['total_learnings']}")
        print(f"  总模式数：{status['stats']['total_patterns']}")
        print(f"  已学习偏好：{len(status['preferences'])}")
        print(f"\n💡 建议:")
        for rec in status["recommendations"]:
            print(f"  - {rec}")
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
