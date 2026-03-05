#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
记忆系统 v2.0 - 三级记忆架构

受 Generative Agents 和 LangChain 启发，实现：
- 短期记忆 (工作记忆)
- 长期记忆 (持久化)
- 反思记忆 (洞察和模式)

功能:
- 记忆存储和检索
- 重要性评分
- 记忆压缩
- 反思生成
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from dataclasses import dataclass, asdict, field
from typing import List, Dict, Any, Optional
from enum import Enum
import random


# ============================================================================
# 配置
# ============================================================================

class Config:
    """配置常量"""
    
    # 路径
    WORKSPACE = Path.home() / ".openclaw" / "workspace"
    MEMORY_DIR = WORKSPACE / "memory"
    
    # 记忆文件
    SHORT_TERM_FILE = MEMORY_DIR / "short-term-memory.json"
    LONG_TERM_FILE = MEMORY_DIR / "long-term-memory.json"
    REFLECTION_FILE = MEMORY_DIR / "reflections.jsonl"
    
    # 记忆限制
    SHORT_TERM_LIMIT = 50       # 短期记忆最大条目
    WORKING_MEMORY_LIMIT = 10   # 工作记忆最大条目
    
    # 重要性阈值
    IMPORTANCE_THRESHOLD = 0.7  # 转入长期记忆的阈值
    REFLECTION_THRESHOLD = 0.8  # 生成反思的阈值
    
    # 时间衰减
    DECAY_RATE = 0.1  # 每天衰减率


# ============================================================================
# 数据类型
# ============================================================================

class MemoryType(str, Enum):
    """记忆类型"""
    EPISODIC = "episodic"     # 事件记忆
    SEMANTIC = "semantic"     # 知识记忆
    PROCEDURAL = "procedural" # 技能记忆
    REFLECTION = "reflection" # 反思记忆


class ImportanceLevel(str, Enum):
    """重要性级别"""
    TRIVIAL = "trivial"       # 0.0-0.3
    LOW = "low"               # 0.3-0.5
    MEDIUM = "medium"         # 0.5-0.7
    HIGH = "high"             # 0.7-0.9
    CRITICAL = "critical"     # 0.9-1.0


@dataclass
class Memory:
    """记忆单元"""
    id: str
    content: str
    memory_type: str
    importance: float
    created_at: str
    updated_at: Optional[str] = None
    accessed_count: int = 0
    last_accessed: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return asdict(self)
    
    def decay(self) -> float:
        """计算时间衰减后的重要性"""
        if not self.last_accessed:
            return self.importance
        
        last = datetime.fromisoformat(self.last_accessed)
        days_old = (datetime.now() - last).days
        decayed = self.importance * (1 - Config.DECAY_RATE) ** days_old
        return max(0.1, decayed)


@dataclass
class Reflection:
    """反思记录"""
    id: str
    content: str
    basis_memories: List[str]  # 基于的记忆 ID
    created_at: str
    category: str  # pattern, insight, lesson, belief
    confidence: float
    applications: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        return asdict(self)


# ============================================================================
# 记忆系统组件
# ============================================================================

class ShortTermMemory:
    """短期记忆 (工作记忆)"""
    
    def __init__(self):
        self.memories: List[Memory] = []
        self.load()
    
    def load(self):
        """加载短期记忆"""
        if Config.SHORT_TERM_FILE.exists():
            try:
                with open(Config.SHORT_TERM_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.memories = [Memory(**m) for m in data.get("memories", [])]
            except Exception as e:
                print(f"⚠️ 加载短期记忆失败：{e}")
    
    def save(self):
        """保存短期记忆"""
        Config.SHORT_TERM_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(Config.SHORT_TERM_FILE, "w", encoding="utf-8") as f:
            json.dump({"memories": [m.to_dict() for m in self.memories]}, f, ensure_ascii=False, indent=2)
    
    def add(self, content: str, importance: float = 0.5, tags: List[str] = None, metadata: Dict = None):
        """添加记忆"""
        memory = Memory(
            id=f"stm_{datetime.now().timestamp()}",
            content=content,
            memory_type=MemoryType.EPISODIC.value,
            importance=importance,
            created_at=datetime.now().isoformat(),
            tags=tags or [],
            metadata=metadata or {}
        )
        
        self.memories.append(memory)
        
        # 限制大小
        if len(self.memories) > Config.SHORT_TERM_LIMIT:
            # 移除最不重要的
            self.memories.sort(key=lambda m: m.decay())
            self.memories.pop(0)
        
        self.save()
        return memory
    
    def get_recent(self, limit: int = 10) -> List[Memory]:
        """获取最近的记忆"""
        return self.memories[-limit:]
    
    def search(self, query: str) -> List[Memory]:
        """搜索记忆"""
        results = []
        for memory in self.memories:
            if query.lower() in memory.content.lower():
                results.append(memory)
        return results
    
    def clear(self):
        """清空短期记忆"""
        self.memories = []
        self.save()


class LongTermMemory:
    """长期记忆"""
    
    def __init__(self):
        self.memories: List[Memory] = []
        self.load()
    
    def load(self):
        """加载长期记忆"""
        if Config.LONG_TERM_FILE.exists():
            try:
                with open(Config.LONG_TERM_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.memories = [Memory(**m) for m in data.get("memories", [])]
            except Exception as e:
                print(f"⚠️ 加载长期记忆失败：{e}")
    
    def save(self):
        """保存长期记忆"""
        Config.LONG_TERM_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(Config.LONG_TERM_FILE, "w", encoding="utf-8") as f:
            json.dump({"memories": [m.to_dict() for m in self.memories]}, f, ensure_ascii=False, indent=2)
    
    def add(self, memory: Memory):
        """添加记忆"""
        memory.memory_type = MemoryType.SEMANTIC.value
        memory.updated_at = datetime.now().isoformat()
        self.memories.append(memory)
        self.save()
    
    def consolidate(self, short_term_memories: List[Memory]):
        """从短期记忆整合到长期记忆"""
        for stm in short_term_memories:
            if stm.importance >= Config.IMPORTANCE_THRESHOLD:
                # 复制重要记忆到长期
                ltm = Memory(
                    id=f"ltm_{datetime.now().timestamp()}",
                    content=stm.content,
                    memory_type=MemoryType.SEMANTIC.value,
                    importance=stm.importance,
                    created_at=datetime.now().isoformat(),
                    tags=stm.tags,
                    metadata=stm.metadata
                )
                self.add(ltm)
    
    def search(self, query: str, limit: int = 10) -> List[Memory]:
        """搜索长期记忆"""
        results = []
        for memory in self.memories:
            score = 0
            if query.lower() in memory.content.lower():
                score += 0.5
            if any(tag.lower() == query.lower() for tag in memory.tags):
                score += 0.3
            if memory.decay() > Config.IMPORTANCE_THRESHOLD:
                score += 0.2
            
            if score > 0.3:
                results.append((score, memory))
        
        results.sort(key=lambda x: x[0], reverse=True)
        return [m for _, m in results[:limit]]
    
    def get_by_type(self, memory_type: MemoryType) -> List[Memory]:
        """按类型获取记忆"""
        return [m for m in self.memories if m.memory_type == memory_type.value]


class ReflectionSystem:
    """反思系统"""
    
    def __init__(self):
        self.reflections: List[Reflection] = []
        self.load()
    
    def load(self):
        """加载反思"""
        if Config.REFLECTION_FILE.exists():
            try:
                with open(Config.REFLECTION_FILE, "r", encoding="utf-8") as f:
                    for line in f:
                        data = json.loads(line)
                        self.reflections.append(Reflection(**data))
            except Exception as e:
                print(f"⚠️ 加载反思失败：{e}")
    
    def save(self, reflection: Reflection):
        """保存反思"""
        Config.REFLECTION_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(Config.REFLECTION_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(reflection.to_dict(), ensure_ascii=False) + "\n")
    
    def generate(self, memories: List[Memory]) -> Optional[Reflection]:
        """从记忆生成反思"""
        if len(memories) < 3:
            return None
        
        # 分析记忆模式
        categories = {}
        for memory in memories:
            for tag in memory.tags:
                categories[tag] = categories.get(tag, 0) + 1
        
        if not categories:
            return None
        
        # 生成反思
        top_category = max(categories, key=categories.get)
        reflection_content = f"观察到模式：{top_category} 出现 {categories[top_category]} 次"
        
        reflection = Reflection(
            id=f"reflection_{datetime.now().timestamp()}",
            content=reflection_content,
            basis_memories=[m.id for m in memories],
            created_at=datetime.now().isoformat(),
            category="pattern",
            confidence=0.7,
            applications=[]
        )
        
        self.save(reflection)
        self.reflections.append(reflection)
        return reflection
    
    def get_recent(self, limit: int = 5) -> List[Reflection]:
        """获取最近的反思"""
        return self.reflections[-limit:]


# ============================================================================
# 记忆系统主控制器
# ============================================================================

class MemorySystem:
    """记忆系统主控制器"""
    
    def __init__(self):
        self.short_term = ShortTermMemory()
        self.long_term = LongTermMemory()
        self.reflection_system = ReflectionSystem()
    
    def record(self, content: str, importance: float = 0.5, tags: List[str] = None):
        """记录新记忆"""
        memory = self.short_term.add(content, importance, tags)
        
        # 检查是否需要整合到长期记忆
        if importance >= Config.IMPORTANCE_THRESHOLD:
            self.long_term.add(memory)
        
        # 检查是否需要生成反思
        if importance >= Config.REFLECTION_THRESHOLD:
            recent = self.short_term.get_recent(10)
            self.reflection_system.generate(recent)
        
        return memory
    
    def think(self, query: str) -> Dict:
        """思考 - 检索相关记忆"""
        # 从短期记忆检索
        stm_results = self.short_term.search(query)
        
        # 从长期记忆检索
        ltm_results = self.long_term.search(query)
        
        # 获取最近反思
        reflections = self.reflection_system.get_recent(3)
        
        return {
            "short_term": [m.to_dict() for m in stm_results],
            "long_term": [m.to_dict() for m in ltm_results],
            "reflections": [r.to_dict() for r in reflections],
            "summary": f"找到 {len(stm_results)} 个短期记忆，{len(ltm_results)} 个长期记忆，{len(reflections)} 个反思"
        }
    
    def consolidate(self):
        """整合记忆"""
        recent = self.short_term.get_recent(20)
        self.long_term.consolidate(recent)
    
    def get_status(self) -> Dict:
        """获取状态"""
        return {
            "version": "2.0.0",
            "timestamp": datetime.now().isoformat(),
            "short_term_count": len(self.short_term.memories),
            "long_term_count": len(self.long_term.memories),
            "reflections_count": len(self.reflection_system.reflections),
            "recent_memories": [m.to_dict() for m in self.short_term.get_recent(5)],
            "recent_reflections": [r.to_dict() for r in self.reflection_system.get_recent(3)]
        }


# ============================================================================
# CLI
# ============================================================================

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="记忆系统 v2.0")
    parser.add_argument("--status", action="store_true", help="显示状态")
    parser.add_argument("--record", type=str, help="记录记忆")
    parser.add_argument("--think", type=str, help="思考/检索")
    parser.add_argument("--consolidate", action="store_true", help="整合记忆")
    parser.add_argument("--test", action="store_true", help="运行测试")
    
    args = parser.parse_args()
    
    system = MemorySystem()
    
    if args.status:
        status = system.get_status()
        print(json.dumps(status, ensure_ascii=False, indent=2))
    
    elif args.record:
        memory = system.record(args.record, importance=0.7, tags=["manual"])
        print(f"✅ 已记录记忆：{memory.content}")
    
    elif args.think:
        result = system.think(args.think)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    
    elif args.consolidate:
        system.consolidate()
        print("✅ 记忆整合完成")
    
    elif args.test:
        print("🧪 运行测试...")
        test_memory_system(system)
    
    else:
        parser.print_help()


def test_memory_system(system: MemorySystem):
    """测试记忆系统"""
    # 添加一些测试记忆
    print("\n1. 添加测试记忆...")
    system.record("用户喜欢详细的代码解释", importance=0.8, tags=["preference", "coding"])
    system.record("完成了模型监控系统", importance=0.7, tags=["achievement", "coding"])
    system.record("学习了 LangChain 架构", importance=0.6, tags=["learning", "architecture"])
    system.record("思考引擎运行正常", importance=0.5, tags=["status", "thinking"])
    
    # 检索
    print("\n2. 检索记忆...")
    result = system.think("coding")
    print(f"   找到：{result['summary']}")
    
    # 整合
    print("\n3. 整合记忆...")
    system.consolidate()
    
    # 状态
    print("\n4. 最终状态:")
    status = system.get_status()
    print(f"   短期记忆：{status['short_term_count']}")
    print(f"   长期记忆：{status['long_term_count']}")
    print(f"   反思：{status['reflections_count']}")
    
    print("\n✅ 测试完成")


if __name__ == "__main__":
    main()
