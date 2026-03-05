#!/usr/bin/env python3
"""
================================================================================
OpenClaw Memory Weight Manager - 记忆权重与有效性评估系统
================================================================================
作者：OpenClaw Assistant
版本：1.0.0
更新日期：2026-03-05
位置：~/.openclaw/workspace/scripts/memory_weight_manager.py

功能说明:
-----------
1. 记忆使用频率追踪（访问次数越多权重越高）
2. 记忆有效性评估（基于相关性、引用率、时效性）
3. 动态权重调整（自动加强/减弱记忆）
4. 记忆重要性评分（综合多维度评估）
5. 记忆清理建议（识别低价值记忆）
6. 与 OpenClaw memory_search 集成

架构设计:
-----------
- MemoryTracker: 记忆使用追踪器
- EffectivenessEvaluator: 有效性评估器
- WeightAdjuster: 权重调整器
- ImportanceScorer: 重要性评分器
- MemoryManager: 记忆管理器（主协调器）

使用方法:
-----------
# 基本检查
python3 ~/.openclaw/workspace/scripts/memory_weight_manager.py

# 详细模式
python3 ~/.openclaw/workspace/scripts/memory_weight_manager.py --verbose

# 评估特定记忆文件
python3 ~/.openclaw/workspace/scripts/memory_weight_manager.py --evaluate MEMORY.md

# 调整权重
python3 ~/.openclaw/workspace/scripts/memory_weight_manager.py --adjust

# 查看统计
python3 ~/.openclaw/workspace/scripts/memory_weight_manager.py --stats

================================================================================
"""

import argparse
import json
import os
import re
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Optional, Dict, List, Any, Tuple
from collections import defaultdict
import hashlib
import threading

# ==============================================================================
# 配置常量
# ==============================================================================

class Config:
    """系统配置常量"""
    # 路径配置
    HOME = Path.home()
    WORKSPACE_PATH = HOME / ".openclaw" / "workspace"
    MEMORY_PATH = WORKSPACE_PATH / "memory"
    MEMORY_MD = WORKSPACE_PATH / "MEMORY.md"
    STATE_PATH = MEMORY_PATH / "memory-weight-state.json"
    LOG_PATH = MEMORY_PATH / "memory-weight.log"
    HISTORY_PATH = MEMORY_PATH / "memory-weight-history.jsonl"
    
    # 权重配置
    INITIAL_WEIGHT = 1.0           # 初始权重
    MIN_WEIGHT = 0.1               # 最小权重
    MAX_WEIGHT = 10.0              # 最大权重
    
    # 使用频率权重
    ACCESS_WEIGHT_FACTOR = 0.1     # 每次访问增加的权重
    MAX_ACCESS_WEIGHT = 5.0        # 访问权重上限
    
    # 时间衰减配置
    DECAY_FACTOR = 0.01            # 每日衰减因子
    HALF_LIFE_DAYS = 30            # 半衰期（30 天）
    
    # 有效性评估权重
    RELEVANCE_WEIGHT = 0.4         # 相关性权重
    RECENCY_WEIGHT = 0.3           # 时效性权重
    IMPORTANCE_WEIGHT = 0.3        # 重要性权重
    
    # 重要性评分阈值
    HIGH_IMPORTANCE_THRESHOLD = 0.8    # 高重要性阈值
    LOW_IMPORTANCE_THRESHOLD = 0.3     # 低重要性阈值
    
    # 清理配置
    MIN_ACCESS_COUNT = 3           # 最小访问次数（低于此值可能被清理）
    MAX_AGE_DAYS = 180             # 最大年龄（天）
    
    # 日志配置
    MAX_LOG_ENTRIES = 1000         # 最大日志条目数
    MAX_HISTORY_ENTRIES = 500      # 最大历史记录数

# ==============================================================================
# 枚举定义
# ==============================================================================

class ImportanceLevel(Enum):
    """重要性等级"""
    CRITICAL = "critical"      # 关键记忆（必须保留）
    HIGH = "high"             # 高重要性
    MEDIUM = "medium"         # 中等重要性
    LOW = "low"               # 低重要性
    TRIVIAL = "trivial"       # 可清理

class MemoryType(Enum):
    """记忆类型"""
    DECISION = "decision"          # 决策记录
    PREFERENCE = "preference"      # 用户偏好
    CONTEXT = "context"           # 上下文信息
    TODO = "todo"                 # 待办事项
    LESSON = "lesson"             # 经验教训
    FACT = "fact"                 # 事实信息
    UNKNOWN = "unknown"           # 未知类型

# ==============================================================================
# 数据类定义
# ==============================================================================

@dataclass
class MemorySnippet:
    """记忆片段"""
    id: str
    path: str
    start_line: int
    end_line: int
    content: str
    memory_type: MemoryType = MemoryType.UNKNOWN
    created_at: Optional[datetime] = None
    accessed_at: Optional[datetime] = None
    access_count: int = 0
    weight: float = Config.INITIAL_WEIGHT
    importance_score: float = 0.0
    last_modified: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "path": self.path,
            "start_line": self.start_line,
            "end_line": self.end_line,
            "content": self.content[:200],  # 限制长度
            "memory_type": self.memory_type.value,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "accessed_at": self.accessed_at.isoformat() if self.accessed_at else None,
            "access_count": self.access_count,
            "weight": self.weight,
            "importance_score": self.importance_score,
            "last_modified": self.last_modified.isoformat() if self.last_modified else None
        }

@dataclass
class AccessRecord:
    """访问记录"""
    timestamp: str
    memory_id: str
    query: str
    relevance_score: float
    was_useful: bool

@dataclass
class WeightAdjustment:
    """权重调整记录"""
    timestamp: str
    memory_id: str
    old_weight: float
    new_weight: float
    reason: str
    delta: float

@dataclass
class MemoryState:
    """记忆状态"""
    version: str = "1.0.0"
    last_update: Optional[str] = None
    memories: Dict[str, MemorySnippet] = field(default_factory=dict)
    access_history: List[AccessRecord] = field(default_factory=list)
    weight_adjustments: List[WeightAdjustment] = field(default_factory=list)
    stats: Dict[str, Any] = field(default_factory=lambda: {
        "total_memories": 0,
        "total_accesses": 0,
        "total_adjustments": 0,
        "start_time": datetime.now().isoformat()
    })

# ==============================================================================
# 日志系统
# ==============================================================================

class StructuredLogger:
    """结构化日志记录器"""
    
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
        
        log_entry = {
            "timestamp": timestamp,
            "level": level,
            "component": component,
            "message": message,
            **kwargs
        }
        
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
        
        if self.verbose or level in ["WARNING", "ERROR", "CRITICAL"]:
            print(formatted, file=sys.stderr)
        
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
# 记忆类型分类器
# ==============================================================================

class MemoryTypeClassifier:
    """记忆类型分类器"""
    
    PATTERNS = {
        MemoryType.DECISION: [
            r"决策", r"决定", r"选择", r"decision", r"chose", r"decided",
            r"关键决策", r"重要决定"
        ],
        MemoryType.PREFERENCE: [
            r"偏好", r"喜欢", r"倾向", r"preference", r"prefer", r"like",
            r"习惯", r"常用"
        ],
        MemoryType.CONTEXT: [
            r"上下文", r"背景", r"环境", r"context", r"background",
            r"项目背景", r"工作环境"
        ],
        MemoryType.TODO: [
            r"待办", r"TODO", r"todo", r"计划", r"下一步",
            r"需要", r"应该", r"必须"
        ],
        MemoryType.LESSON: [
            r"教训", r"经验", r"学习", r"lesson", r"learned",
            r"学到", r"心得", r"体会"
        ],
        MemoryType.FACT: [
            r"事实", r"信息", r"数据", r"fact", r"information",
            r"配置", r"设置"
        ]
    }
    
    @classmethod
    def classify(cls, content: str) -> MemoryType:
        """分类记忆内容"""
        content_lower = content.lower()
        
        scores = {}
        for memory_type, patterns in cls.PATTERNS.items():
            score = sum(1 for pattern in patterns if re.search(pattern, content_lower, re.IGNORECASE))
            scores[memory_type] = score
        
        if max(scores.values()) == 0:
            return MemoryType.UNKNOWN
        
        return max(scores.items(), key=lambda x: x[1])[0]

# ==============================================================================
# 记忆追踪器
# ==============================================================================

class MemoryTracker:
    """记忆使用追踪器"""
    
    def __init__(self, logger: StructuredLogger):
        self.logger = logger
        self.access_counts: Dict[str, int] = defaultdict(int)
        self.last_access: Dict[str, datetime] = {}
        self.access_history: List[AccessRecord] = []
    
    def record_access(self, memory_id: str, query: str, relevance_score: float, 
                     was_useful: bool = True):
        """记录记忆访问"""
        timestamp = datetime.now().isoformat()
        
        self.access_counts[memory_id] += 1
        self.last_access[memory_id] = datetime.now()
        
        record = AccessRecord(
            timestamp=timestamp,
            memory_id=memory_id,
            query=query,
            relevance_score=relevance_score,
            was_useful=was_useful
        )
        self.access_history.append(record)
        
        self.logger.debug("MemoryTracker",
                         f"Recorded access for {memory_id}",
                         query=query,
                         relevance=relevance_score,
                         useful=was_useful)
    
    def get_access_count(self, memory_id: str) -> int:
        """获取访问次数"""
        return self.access_counts.get(memory_id, 0)
    
    def get_last_access(self, memory_id: str) -> Optional[datetime]:
        """获取最后访问时间"""
        return self.last_access.get(memory_id)
    
    def get_most_accessed(self, limit: int = 10) -> List[Tuple[str, int]]:
        """获取最常访问的记忆"""
        sorted_memories = sorted(
            self.access_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )
        return sorted_memories[:limit]

# ==============================================================================
# 有效性评估器
# ==============================================================================

class EffectivenessEvaluator:
    """记忆有效性评估器"""
    
    def __init__(self, logger: StructuredLogger):
        self.logger = logger
    
    def evaluate(self, memory: MemorySnippet, 
                tracker: MemoryTracker) -> Dict[str, Any]:
        """评估记忆有效性"""
        # 1. 相关性评分（基于访问历史）
        relevance_score = self._calculate_relevance(memory, tracker)
        
        # 2. 时效性评分（基于时间衰减）
        recency_score = self._calculate_recency(memory)
        
        # 3. 重要性评分（基于内容分析）
        importance_score = self._calculate_importance(memory)
        
        # 4. 综合评分
        overall_score = (
            relevance_score * Config.RELEVANCE_WEIGHT +
            recency_score * Config.RECENCY_WEIGHT +
            importance_score * Config.IMPORTANCE_WEIGHT
        )
        
        result = {
            "memory_id": memory.id,
            "relevance_score": relevance_score,
            "recency_score": recency_score,
            "importance_score": importance_score,
            "overall_score": overall_score,
            "importance_level": self._get_importance_level(overall_score).value,
            "recommendation": self._get_recommendation(overall_score, memory)
        }
        
        self.logger.info("EffectivenessEvaluator",
                        f"Evaluated memory {memory.id}",
                        scores=result)
        
        return result
    
    def _calculate_relevance(self, memory: MemorySnippet, 
                            tracker: MemoryTracker) -> float:
        """计算相关性评分"""
        access_count = tracker.get_access_count(memory.id)
        
        if access_count == 0:
            return 0.5  # 默认中等评分
        
        # 使用对数缩放，避免访问次数过多导致评分过高
        import math
        log_access = math.log2(access_count + 1)
        
        # 归一化到 0-1 范围（假设最大有效访问次数为 100）
        relevance = min(1.0, log_access / math.log2(101))
        
        return relevance
    
    def _calculate_recency(self, memory: MemorySnippet) -> float:
        """计算时效性评分"""
        if not memory.last_modified:
            return 0.5
        
        age_days = (datetime.now() - memory.last_modified).days
        
        # 指数衰减
        decay = Config.DECAY_FACTOR
        recency = 2 ** (-decay * age_days)
        
        return recency
    
    def _calculate_importance(self, memory: MemorySnippet) -> float:
        """计算重要性评分"""
        score = 0.5  # 基础分
        
        # 基于记忆类型加分
        type_scores = {
            MemoryType.DECISION: 0.2,
            MemoryType.PREFERENCE: 0.15,
            MemoryType.LESSON: 0.2,
            MemoryType.CONTEXT: 0.1,
            MemoryType.TODO: 0.05,
            MemoryType.FACT: 0.1
        }
        score += type_scores.get(memory.memory_type, 0)
        
        # 基于内容长度（适中的长度更好）
        content_length = len(memory.content)
        if 100 <= content_length <= 1000:
            score += 0.1
        elif content_length > 1000:
            score += 0.05
        
        # 基于关键词
        important_keywords = [
            "重要", "关键", "必须", "critical", "important",
            "always", "never", "core", "essential"
        ]
        content_lower = memory.content.lower()
        keyword_matches = sum(1 for kw in important_keywords 
                            if kw in content_lower)
        score += min(0.2, keyword_matches * 0.05)
        
        return min(1.0, score)
    
    def _get_importance_level(self, score: float) -> ImportanceLevel:
        """获取重要性等级"""
        if score >= Config.HIGH_IMPORTANCE_THRESHOLD:
            return ImportanceLevel.HIGH
        elif score >= Config.LOW_IMPORTANCE_THRESHOLD:
            return ImportanceLevel.MEDIUM
        else:
            return ImportanceLevel.LOW
    
    def _get_recommendation(self, score: float, 
                           memory: MemorySnippet) -> str:
        """获取建议"""
        if score >= 0.8:
            return "KEEP_AND_STRENGTHEN"  # 保留并加强
        elif score >= 0.6:
            return "KEEP"  # 保留
        elif score >= 0.4:
            return "MONITOR"  # 观察
        elif score >= 0.2:
            return "CONSIDER_REMOVAL"  # 考虑移除
        else:
            return "REMOVE"  # 移除

# ==============================================================================
# 权重调整器
# ==============================================================================

class WeightAdjuster:
    """权重调整器"""
    
    def __init__(self, logger: StructuredLogger):
        self.logger = logger
        self.adjustment_history: List[WeightAdjustment] = []
    
    def adjust_weight(self, memory: MemorySnippet, 
                     effectiveness: Dict[str, Any],
                     tracker: MemoryTracker) -> float:
        """调整记忆权重"""
        old_weight = memory.weight
        
        # 1. 基于访问频率调整
        access_count = tracker.get_access_count(memory.id)
        access_bonus = min(
            Config.MAX_ACCESS_WEIGHT,
            access_count * Config.ACCESS_WEIGHT_FACTOR
        )
        
        # 2. 基于有效性评分调整
        effectiveness_score = effectiveness.get("overall_score", 0.5)
        effectiveness_bonus = (effectiveness_score - 0.5) * 2  # 归一化到 -1 到 1
        
        # 3. 基于时间衰减调整
        if memory.last_modified:
            age_days = (datetime.now() - memory.last_modified).days
            decay_penalty = age_days * Config.DECAY_FACTOR
        else:
            decay_penalty = 0
        
        # 4. 计算新权重
        delta = access_bonus + effectiveness_bonus - decay_penalty
        new_weight = old_weight + delta
        
        # 5. 应用边界限制
        new_weight = max(Config.MIN_WEIGHT, min(Config.MAX_WEIGHT, new_weight))
        
        # 6. 记录调整
        if abs(new_weight - old_weight) > 0.01:  # 只有显著变化才记录
            adjustment = WeightAdjustment(
                timestamp=datetime.now().isoformat(),
                memory_id=memory.id,
                old_weight=old_weight,
                new_weight=new_weight,
                reason=f"access:{access_count}, effectiveness:{effectiveness_score:.2f}, age:{age_days if memory.last_modified else 0}d",
                delta=new_weight - old_weight
            )
            self.adjustment_history.append(adjustment)
            
            self.logger.info("WeightAdjuster",
                           f"Adjusted weight for {memory.id}",
                           old=old_weight,
                           new=new_weight,
                           delta=delta)
        
        memory.weight = new_weight
        return new_weight
    
    def get_adjustment_history(self, limit: int = 50) -> List[WeightAdjustment]:
        """获取调整历史"""
        return self.adjustment_history[-limit:]

# ==============================================================================
# 记忆管理器
# ==============================================================================

class MemoryManager:
    """记忆管理器 - 主协调器"""
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.logger = StructuredLogger(Config.LOG_PATH, verbose)
        self.tracker = MemoryTracker(self.logger)
        self.evaluator = EffectivenessEvaluator(self.logger)
        self.adjuster = WeightAdjuster(self.logger)
        self.memories: Dict[str, MemorySnippet] = {}
        self.state = MemoryState()
        
        self._load_state()
        self._scan_memories()
        
        self.logger.info("MemoryManager", 
                        "Memory Weight Manager v1.0 initialized",
                        verbose=verbose)
    
    def _load_state(self):
        """加载状态"""
        try:
            if Config.STATE_PATH.exists():
                with open(Config.STATE_PATH, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                self.state.version = data.get("version", "1.0.0")
                self.state.last_update = data.get("last_update")
                self.state.stats = data.get("stats", self.state.stats)
                
                # 加载记忆信息
                for memory_id, memory_data in data.get("memories", {}).items():
                    self.memories[memory_id] = MemorySnippet(
                        id=memory_data["id"],
                        path=memory_data["path"],
                        start_line=memory_data["start_line"],
                        end_line=memory_data["end_line"],
                        content=memory_data["content"],
                        memory_type=MemoryType(memory_data.get("memory_type", "unknown")),
                        weight=memory_data.get("weight", Config.INITIAL_WEIGHT),
                        access_count=memory_data.get("access_count", 0),
                        importance_score=memory_data.get("importance_score", 0.0)
                    )
                
                self.logger.debug("MemoryManager", 
                                f"Loaded state with {len(self.memories)} memories")
        
        except Exception as e:
            self.logger.error("MemoryManager", f"Failed to load state: {e}")
    
    def _save_state(self):
        """保存状态"""
        try:
            Config.STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
            
            data = {
                "version": self.state.version,
                "last_update": datetime.now().isoformat(),
                "memories": {k: v.to_dict() for k, v in self.memories.items()},
                "stats": self.state.stats
            }
            
            with open(Config.STATE_PATH, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            self.logger.debug("MemoryManager", "State saved successfully")
        
        except Exception as e:
            self.logger.error("MemoryManager", f"Failed to save state: {e}")
    
    def _scan_memories(self):
        """扫描记忆文件"""
        self.logger.info("MemoryManager", "Scanning memory files...")
        
        files_to_scan = []
        
        # 添加 MEMORY.md
        if Config.MEMORY_MD.exists():
            files_to_scan.append(Config.MEMORY_MD)
        
        # 添加 memory/*.md 文件
        if Config.MEMORY_PATH.exists():
            for md_file in Config.MEMORY_PATH.glob("*.md"):
                if md_file.name not in ["memory-weight-state.json"]:
                    files_to_scan.append(md_file)
        
        # 扫描每个文件
        for file_path in files_to_scan:
            self._scan_file(file_path)
        
        self.state.stats["total_memories"] = len(self.memories)
        self.logger.info("MemoryManager", 
                        f"Scanned {len(files_to_scan)} files, found {len(self.memories)} memories")
    
    def _scan_file(self, file_path: Path):
        """扫描单个文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # 简单的分块逻辑（按空行或标题分块）
            current_chunk = []
            current_start = 1
            
            for i, line in enumerate(lines, start=1):
                # 检测新块开始（标题或空行后）
                if line.startswith('#') or (line.strip() == '' and current_chunk):
                    if current_chunk:
                        self._process_chunk(file_path, current_chunk, current_start, i - 1)
                    current_chunk = []
                    current_start = i
                
                current_chunk.append(line)
            
            # 处理最后一个块
            if current_chunk:
                self._process_chunk(file_path, current_chunk, current_start, len(lines))
        
        except Exception as e:
            self.logger.error("MemoryManager", 
                            f"Failed to scan file {file_path}: {e}")
    
    def _process_chunk(self, file_path: Path, lines: List[str], 
                      start_line: int, end_line: int):
        """处理文本块"""
        content = ''.join(lines).strip()
        
        # 跳过太短或太长的块
        if len(content) < 50 or len(content) > 5000:
            return
        
        # 生成唯一 ID
        content_hash = hashlib.md5(content.encode()).hexdigest()[:12]
        memory_id = f"{file_path.stem}:{start_line}:{content_hash}"
        
        # 创建记忆片段
        memory = MemorySnippet(
            id=memory_id,
            path=str(file_path),
            start_line=start_line,
            end_line=end_line,
            content=content,
            memory_type=MemoryTypeClassifier.classify(content),
            last_modified=datetime.fromtimestamp(file_path.stat().st_mtime)
        )
        
        # 如果已存在，保留历史数据
        if memory_id in self.memories:
            old_memory = self.memories[memory_id]
            memory.access_count = old_memory.access_count
            memory.weight = old_memory.weight
        
        self.memories[memory_id] = memory
    
    def record_access(self, memory_path: str, line_number: int, 
                     query: str, relevance_score: float):
        """记录记忆访问"""
        # 查找对应的记忆
        memory_id = None
        for mid, memory in self.memories.items():
            if memory.path.endswith(memory_path) and \
               memory.start_line <= line_number <= memory.end_line:
                memory_id = mid
                break
        
        if memory_id:
            memory = self.memories[memory_id]
            memory.access_count += 1
            memory.accessed_at = datetime.now()
            
            self.tracker.record_access(memory_id, query, relevance_score)
            
            self.logger.info("MemoryManager",
                           f"Recorded access for {memory_path}:{line_number}",
                           query=query,
                           relevance=relevance_score)
        else:
            self.logger.debug("MemoryManager",
                            f"Memory not found: {memory_path}:{line_number}")
    
    def evaluate_all(self) -> Dict[str, Any]:
        """评估所有记忆"""
        self.logger.info("MemoryManager", "Evaluating all memories...")
        
        results = []
        for memory in self.memories.values():
            evaluation = self.evaluator.evaluate(memory, self.tracker)
            results.append(evaluation)
        
        # 统计
        stats = {
            "total": len(results),
            "high_importance": sum(1 for r in results if r["importance_level"] == ImportanceLevel.HIGH),
            "medium_importance": sum(1 for r in results if r["importance_level"] == ImportanceLevel.MEDIUM),
            "low_importance": sum(1 for r in results if r["importance_level"] == ImportanceLevel.LOW),
            "average_score": sum(r["overall_score"] for r in results) / len(results) if results else 0
        }
        
        self.logger.info("MemoryManager", 
                        f"Evaluation complete: {stats}")
        
        return {
            "evaluations": results,
            "stats": stats
        }
    
    def adjust_all_weights(self) -> Dict[str, Any]:
        """调整所有记忆权重"""
        self.logger.info("MemoryManager", "Adjusting all weights...")
        
        adjustments = []
        for memory in self.memories.values():
            evaluation = self.evaluator.evaluate(memory, self.tracker)
            new_weight = self.adjuster.adjust_weight(memory, evaluation, self.tracker)
            
            adjustments.append({
                "memory_id": memory.id,
                "old_weight": evaluation.get("old_weight", Config.INITIAL_WEIGHT),
                "new_weight": new_weight,
                "importance": evaluation["importance_level"].value
            })
        
        # 保存状态
        self._save_state()
        
        self.logger.info("MemoryManager", 
                        f"Adjusted {len(adjustments)} weights")
        
        return {
            "adjustments": adjustments,
            "total_adjusted": len(adjustments)
        }
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取统计信息"""
        weights = [m.weight for m in self.memories.values()]
        access_counts = [m.access_count for m in self.memories.values()]
        
        return {
            "total_memories": len(self.memories),
            "total_accesses": sum(access_counts),
            "average_weight": sum(weights) / len(weights) if weights else 0,
            "max_weight": max(weights) if weights else 0,
            "min_weight": min(weights) if weights else 0,
            "average_access_count": sum(access_counts) / len(access_counts) if access_counts else 0,
            "memories_by_type": self._count_by_type(),
            "top_accessed": self.tracker.get_most_accessed(10)
        }
    
    def _count_by_type(self) -> Dict[str, int]:
        """按类型统计"""
        counts = defaultdict(int)
        for memory in self.memories.values():
            counts[memory.memory_type.value] += 1
        return dict(counts)
    
    def get_cleanup_suggestions(self) -> List[Dict[str, Any]]:
        """获取清理建议"""
        suggestions = []
        
        for memory in self.memories.values():
            evaluation = self.evaluator.evaluate(memory, self.tracker)
            
            if evaluation["recommendation"] in ["REMOVE", "CONSIDER_REMOVAL"]:
                suggestions.append({
                    "memory_id": memory.id,
                    "path": memory.path,
                    "lines": f"{memory.start_line}-{memory.end_line}",
                    "importance": evaluation["importance_level"].value,
                    "score": evaluation["overall_score"],
                    "access_count": memory.access_count,
                    "recommendation": evaluation["recommendation"],
                    "content_preview": memory.content[:100]
                })
        
        # 按评分排序
        suggestions.sort(key=lambda x: x["score"])
        
        return suggestions

# ==============================================================================
# 命令行接口
# ==============================================================================

def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="OpenClaw Memory Weight Manager - 记忆权重与有效性评估系统",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  # 基本检查
  python3 memory_weight_manager.py
  
  # 详细模式
  python3 memory_weight_manager.py --verbose
  
  # 评估所有记忆
  python3 memory_weight_manager.py --evaluate
  
  # 调整权重
  python3 memory_weight_manager.py --adjust
  
  # 查看统计
  python3 memory_weight_manager.py --stats
  
  # 获取清理建议
  python3 memory_weight_manager.py --cleanup
        """
    )
    
    parser.add_argument("-v", "--verbose", 
                       action="store_true",
                       help="启用详细日志输出")
    parser.add_argument("-e", "--evaluate",
                       action="store_true", 
                       help="评估所有记忆的有效性")
    parser.add_argument("-a", "--adjust",
                       action="store_true",
                       help="调整所有记忆权重")
    parser.add_argument("-s", "--stats",
                       action="store_true",
                       help="显示统计信息")
    parser.add_argument("-c", "--cleanup",
                       action="store_true",
                       help="获取清理建议")
    parser.add_argument("--scan",
                       action="store_true",
                       help="重新扫描记忆文件")
    
    args = parser.parse_args()
    
    # 创建管理器
    manager = MemoryManager(verbose=args.verbose)
    
    # 执行请求的操作
    if args.evaluate:
        result = manager.evaluate_all()
        print(json.dumps(result, indent=2, ensure_ascii=False))
    
    elif args.adjust:
        result = manager.adjust_all_weights()
        print(json.dumps(result, indent=2, ensure_ascii=False))
    
    elif args.stats:
        result = manager.get_statistics()
        print(json.dumps(result, indent=2, ensure_ascii=False))
    
    elif args.cleanup:
        result = manager.get_cleanup_suggestions()
        print(json.dumps({"suggestions": result}, indent=2, ensure_ascii=False))
    
    elif args.scan:
        manager._scan_memories()
        manager._save_state()
        print(f"✓ Scanned {len(manager.memories)} memories")
    
    else:
        # 默认：运行完整检查
        print("Running full memory weight analysis...\n")
        
        # 1. 统计
        stats = manager.get_statistics()
        print("📊 Statistics:")
        print(f"  Total memories: {stats['total_memories']}")
        print(f"  Total accesses: {stats['total_accesses']}")
        print(f"  Average weight: {stats['average_weight']:.2f}")
        print(f"  Average access count: {stats['average_access_count']:.1f}")
        print()
        
        # 2. 评估
        print("📈 Evaluating memories...")
        evaluation = manager.evaluate_all()
        print(f"  High importance: {evaluation['stats']['high_importance']}")
        print(f"  Medium importance: {evaluation['stats']['medium_importance']}")
        print(f"  Low importance: {evaluation['stats']['low_importance']}")
        print(f"  Average score: {evaluation['stats']['average_score']:.2f}")
        print()
        
        # 3. 调整权重
        print("⚖️  Adjusting weights...")
        adjustments = manager.adjust_all_weights()
        print(f"  Adjusted {adjustments['total_adjusted']} memories")
        print()
        
        # 4. 清理建议
        cleanup = manager.get_cleanup_suggestions()
        if cleanup:
            print(f"🗑️  Cleanup suggestions: {len(cleanup)} memories")
            for suggestion in cleanup[:5]:  # 只显示前 5 个
                print(f"  - {suggestion['path']}:{suggestion['lines']} "
                      f"(score: {suggestion['score']:.2f}, "
                      f"accesses: {suggestion['access_count']})")
        else:
            print("✓ No cleanup suggestions")
        
        print("\n✓ Analysis complete!")
    
    sys.exit(0)

if __name__ == "__main__":
    main()
