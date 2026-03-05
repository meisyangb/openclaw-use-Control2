#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
记忆系统 v2.0 - 三级记忆架构

功能:
- 短期记忆 (工作记忆)
- 长期记忆 (持久化)
- 反思记忆 (洞察和模式)
"""

import json
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass, asdict, field
from typing import List, Dict, Any, Optional


@dataclass
class Memory:
    """记忆单元"""
    id: str
    content: str
    memory_type: str
    importance: float
    created_at: str
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    accessed_count: int = 0
    last_accessed: Optional[str] = None
    updated_at: Optional[str] = None  # 向后兼容
    
    def to_dict(self) -> Dict:
        return asdict(self)
    
    def decay(self) -> float:
        """计算时间衰减后的重要性"""
        if not self.last_accessed:
            return self.importance
        last = datetime.fromisoformat(self.last_accessed)
        days_old = (datetime.now() - last).days
        decayed = self.importance * (1 - 0.1) ** days_old
        return max(0.1, decayed)


class ShortTermMemory:
    """短期记忆 (工作记忆)"""
    
    def __init__(self, limit: int = 50):
        self.memories: List[Memory] = []
        self.limit = limit
    
    def add(self, content: str, importance: float = 0.5, tags: List[str] = None) -> Memory:
        """添加记忆"""
        memory = Memory(
            id=f"stm_{datetime.now().timestamp()}",
            content=content,
            memory_type="episodic",
            importance=importance,
            created_at=datetime.now().isoformat(),
            tags=tags or []
        )
        self.memories.append(memory)
        
        # 限制大小
        if len(self.memories) > self.limit:
            self.memories.pop(0)
        
        return memory
    
    def get_recent(self, limit: int = 10) -> List[Memory]:
        """获取最近的记忆"""
        return self.memories[-limit:]
    
    def search(self, query: str) -> List[Memory]:
        """搜索记忆"""
        return [m for m in self.memories if query.lower() in m.content.lower()]


class LongTermMemory:
    """长期记忆"""
    
    def __init__(self, storage_path: Optional[Path] = None):
        self.memories: List[Memory] = []
        self.storage_path = storage_path
        self.load()
    
    def load(self):
        """加载记忆"""
        if self.storage_path and self.storage_path.exists():
            with open(self.storage_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.memories = [Memory(**m) for m in data.get("memories", [])]
    
    def save(self):
        """保存记忆"""
        if self.storage_path:
            self.storage_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.storage_path, "w", encoding="utf-8") as f:
                json.dump({"memories": [m.to_dict() for m in self.memories]}, f, ensure_ascii=False, indent=2)
    
    def add(self, memory: Memory):
        """添加记忆"""
        memory.memory_type = "semantic"
        self.memories.append(memory)
        self.save()
    
    def search(self, query: str, limit: int = 10) -> List[Memory]:
        """搜索记忆"""
        results = []
        for memory in self.memories:
            score = 0
            if query.lower() in memory.content.lower():
                score += 0.5
            if any(tag.lower() == query.lower() for tag in memory.tags):
                score += 0.3
            if memory.decay() > 0.7:
                score += 0.2
            if score > 0.3:
                results.append((score, memory))
        
        results.sort(key=lambda x: x[0], reverse=True)
        return [m for _, m in results[:limit]]


class ReflectionSystem:
    """反思系统"""
    
    def __init__(self, storage_path: Optional[Path] = None):
        self.reflections: List[Dict] = []
        self.storage_path = storage_path
        self.load()
    
    def load(self):
        """加载反思"""
        if self.storage_path and self.storage_path.exists():
            with open(self.storage_path, "r", encoding="utf-8") as f:
                for line in f:
                    self.reflections.append(json.loads(line))
    
    def save(self, reflection: Dict):
        """保存反思"""
        if self.storage_path:
            self.storage_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.storage_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(reflection, ensure_ascii=False) + "\n")
    
    def generate(self, memories: List[Memory]) -> Optional[Dict]:
        """从记忆生成反思"""
        if len(memories) < 3:
            return None
        
        # 分析模式
        categories = {}
        for memory in memories:
            for tag in memory.tags:
                categories[tag] = categories.get(tag, 0) + 1
        
        if not categories:
            return None
        
        top_category = max(categories, key=categories.get)
        reflection = {
            "id": f"reflection_{datetime.now().timestamp()}",
            "timestamp": datetime.now().isoformat(),
            "content": f"观察到模式：{top_category} 出现 {categories[top_category]} 次",
            "category": "pattern",
            "confidence": 0.7,
            "basis_memories": [m.id for m in memories]
        }
        
        self.save(reflection)
        self.reflections.append(reflection)
        return reflection


class MemorySystem:
    """记忆系统主控制器"""
    
    def __init__(self, storage_dir: Optional[Path] = None):
        if storage_dir is None:
            storage_dir = Path.home() / ".openclaw" / "workspace" / "memory"
        
        self.short_term = ShortTermMemory()
        self.long_term = LongTermMemory(storage_dir / "long-term-memory.json")
        self.reflection_system = ReflectionSystem(storage_dir / "reflections.jsonl")
    
    def record(self, content: str, importance: float = 0.5, tags: List[str] = None) -> Memory:
        """记录新记忆"""
        memory = self.short_term.add(content, importance, tags)
        
        # 重要记忆转入长期
        if importance >= 0.7:
            self.long_term.add(memory)
        
        # 高重要性生成反思
        if importance >= 0.8:
            recent = self.short_term.get_recent(10)
            self.reflection_system.generate(recent)
        
        return memory
    
    def retrieve(self, query: str, limit: int = 5) -> Dict:
        """检索记忆"""
        stm_results = self.short_term.search(query)
        ltm_results = self.long_term.search(query, limit)
        reflections = self.reflection_system.reflections[-3:]
        
        return {
            "short_term": [m.to_dict() for m in stm_results[:limit]],
            "long_term": [m.to_dict() for m in ltm_results],
            "reflections": reflections,
            "summary": f"找到 {len(stm_results)} 个短期记忆，{len(ltm_results)} 个长期记忆"
        }
    
    def get_status(self) -> Dict:
        """获取状态"""
        return {
            "version": "2.0.0",
            "timestamp": datetime.now().isoformat(),
            "short_term_count": len(self.short_term.memories),
            "long_term_count": len(self.long_term.memories),
            "reflections_count": len(self.reflection_system.reflections)
        }


# 快速测试
if __name__ == "__main__":
    memory = MemorySystem()
    
    # 测试记录
    memory.record("用户喜欢详细的代码解释", importance=0.8, tags=["preference", "coding"])
    memory.record("完成了记忆系统 v2.0", importance=0.7, tags=["achievement"])
    
    # 测试检索
    result = memory.retrieve("coding")
    print(f"检索结果：{result['summary']}")
    
    # 测试状态
    status = memory.get_status()
    print(f"状态：{status}")
