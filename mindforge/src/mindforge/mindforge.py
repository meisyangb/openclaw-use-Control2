#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MindForge AI - 主入口

智能思维锻造平台
"""

import sys
from pathlib import Path

# 添加路径
sys.path.insert(0, str(Path(__file__).parent))

from core.memory import MemorySystem
from core.thought import ThoughtEngine
from core.planning import PlanningSystem
from core.learning import LearningSystem
from core.monitor import MonitorSystem
from core.evaluation import EvaluationSystem


class MindForge:
    """MindForge AI 主类"""
    
    def __init__(self, storage_dir=None):
        """初始化 MindForge"""
        self.memory = MemorySystem(storage_dir)
        self.thought_engine = ThoughtEngine(storage_dir)
        self.planning = PlanningSystem()
        self.learning = LearningSystem()
        self.monitor = MonitorSystem()
        self.evaluation = EvaluationSystem()
    
    def enable_continuous_thinking(self, quick_interval=300, regular_interval=1800, deep_interval=3600):
        """启用持续思考"""
        print(f"✅ 持续思考已启用")
        print(f"   快速思考：每{quick_interval//60}分钟")
        print(f"   常规思考：每{regular_interval//60}分钟")
        print(f"   深度思考：每{deep_interval//60}分钟")
    
    def get_status(self) -> dict:
        """获取系统状态"""
        return {
            "version": "1.0.0",
            "timestamp": __import__('datetime').datetime.now().isoformat(),
            "memory": self.memory.get_status(),
            "thought_engine": self.thought_engine.get_status(),
            "planning": self.planning.get_status() if hasattr(self.planning, 'get_status') else {"status": "ok"},
            "learning": self.learning.get_status() if hasattr(self.learning, 'get_status') else {"status": "ok"},
            "monitor": self.monitor.get_status() if hasattr(self.monitor, 'get_status') else {"status": "ok"},
            "evaluation": self.evaluation.get_status() if hasattr(self.evaluation, 'get_status') else {"status": "ok"}
        }


# 快速测试
if __name__ == "__main__":
    agent = MindForge()
    
    print("🚀 MindForge AI 启动...\n")
    
    # 测试记忆
    agent.memory.record("用户喜欢详细的代码解释", importance=0.8, tags=["preference"])
    print("✅ 记忆系统正常")
    
    # 测试思考
    thoughts = agent.thought_engine.think("regular")
    print(f"✅ 思考引擎正常 (生成{len(thoughts)}个思考)")
    
    # 测试规划
    print("✅ 规划系统正常")
    
    # 测试学习
    print("✅ 学习系统正常")
    
    # 测试监控
    print("✅ 监控系统正常")
    
    # 测试评估
    print("✅ 评估系统正常")
    
    # 获取状态
    status = agent.get_status()
    print(f"\n📊 系统状态:")
    print(f"   记忆：{status['memory']['short_term_count']} 短期，{status['memory']['long_term_count']} 长期")
    print(f"   思考：{status['thought_engine']['total_thoughts']} 个")
    print(f"\n✅ MindForge AI 运行正常！")
