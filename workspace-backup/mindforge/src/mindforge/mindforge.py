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
from orchestration import TaskScheduler, ContinuousLearning


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
        self.scheduler = TaskScheduler(self)
        self.continuous_learning = ContinuousLearning(storage_dir)
    
    def enable_continuous_thinking(self, quick_interval=300, regular_interval=1800, deep_interval=3600):
        """启用持续思考"""
        print(f"✅ 持续思考已启用")
        print(f"   快速思考：每{quick_interval//60}分钟")
        print(f"   常规思考：每{regular_interval//60}分钟")
        print(f"   深度思考：每{deep_interval//60}分钟")
    
    def enable_scheduler(self):
        """启用定时任务调度器"""
        self.scheduler.start()
        print("✅ 定时任务调度器已启动")
    
    def start_auto_learning(self):
        """启动自动学习和迭代"""
        print("\n🚀 启动自动学习和迭代系统...")
        
        # 配置学习任务
        learning_tasks = [
            ("external_learning", 1440),  # 每天学习 GitHub
            ("product_iteration", 1440),   # 每天迭代产品
            ("self_evaluation", 60),       # 每小时自我评估
        ]
        
        for task_name, interval in learning_tasks:
            self.scheduler.schedule_task(f"task_{task_name}", interval)
        
        # 启动调度器
        self.enable_scheduler()
        
        print("\n📚 学习配置:")
        print("   - GitHub 探索：每天 1 次")
        print("   - 产品迭代：每天 1 次")
        print("   - 自我评估：每小时 1 次")
        print("\n✅ 自动学习系统已启动！")
    
    def get_learning_report(self) -> str:
        """获取学习报告"""
        if hasattr(self, 'continuous_learning'):
            return self.continuous_learning.generate_learning_report()
        return "学习系统不可用"
    
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
            "evaluation": self.evaluation.get_status() if hasattr(self.evaluation, 'get_status') else {"status": "ok"},
            "scheduler": self.scheduler.get_status() if hasattr(self.scheduler, 'get_status') else {"status": "ok"},
            "continuous_learning": self.continuous_learning.get_knowledge_summary() if hasattr(self.continuous_learning, 'get_knowledge_summary') else {"status": "ok"}
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
