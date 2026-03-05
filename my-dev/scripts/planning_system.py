#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
规划系统 v2.1 - 目标管理和任务分解

受 Generative Agents 和 LangChain 启发，实现：
- 目标管理 (GoalManager)
- 任务分解 (TaskDecomposition)
- 调度器 (Scheduler)
- 进度追踪 (ProgressTracker)

功能:
- 基于记忆的目标制定
- 复杂任务分解
- 时间管理和调度
- 进度追踪和调整
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
    
    # 规划文件
    GOALS_FILE = MEMORY_DIR / "goals.json"
    TASKS_FILE = MEMORY_DIR / "tasks.json"
    SCHEDULE_FILE = MEMORY_DIR / "schedule.json"
    
    # 优先级
    PRIORITY_CRITICAL = 1.0
    PRIORITY_HIGH = 0.8
    PRIORITY_MEDIUM = 0.5
    PRIORITY_LOW = 0.3
    
    # 时间配置
    DEFAULT_TASK_DURATION = 30  # 分钟
    MAX_CONCURRENT_TASKS = 3


# ============================================================================
# 数据类型
# ============================================================================

class GoalStatus(str, Enum):
    """目标状态"""
    DRAFT = "draft"
    ACTIVE = "active"
    ON_HOLD = "on_hold"
    COMPLETED = "completed"
    ABANDONED = "abandoned"


class TaskStatus(str, Enum):
    """任务状态"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    BLOCKED = "blocked"
    COMPLETED = "completed"
    FAILED = "failed"


class Priority(str, Enum):
    """优先级"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class Goal:
    """目标"""
    id: str
    title: str
    description: str
    status: str
    priority: float
    created_at: str
    updated_at: Optional[str] = None
    deadline: Optional[str] = None
    parent_goal_id: Optional[str] = None
    sub_goals: List[str] = field(default_factory=list)
    related_memories: List[str] = field(default_factory=list)
    progress: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class Task:
    """任务"""
    id: str
    title: str
    description: str
    status: str
    priority: float
    goal_id: Optional[str]
    created_at: str
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    estimated_duration: int = 30  # 分钟
    actual_duration: Optional[int] = None
    dependencies: List[str] = field(default_factory=list)
    sub_tasks: List[str] = field(default_factory=list)
    assigned_to: str = "self"
    progress: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class ScheduleEntry:
    """日程条目"""
    id: str
    task_id: str
    start_time: str
    end_time: str
    status: str
    created_at: str
    notes: str = ""
    
    def to_dict(self) -> Dict:
        return asdict(self)


# ============================================================================
# 组件
# ============================================================================

class GoalManager:
    """目标管理器"""
    
    def __init__(self):
        self.goals: List[Goal] = []
        self.load()
    
    def load(self):
        """加载目标"""
        if Config.GOALS_FILE.exists():
            try:
                with open(Config.GOALS_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.goals = [Goal(**g) for g in data.get("goals", [])]
            except Exception as e:
                print(f"⚠️ 加载目标失败：{e}")
    
    def save(self):
        """保存目标"""
        Config.GOALS_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(Config.GOALS_FILE, "w", encoding="utf-8") as f:
            json.dump({"goals": [g.to_dict() for g in self.goals]}, f, ensure_ascii=False, indent=2)
    
    def create(self, title: str, description: str, priority: float = 0.5, 
               deadline: str = None, parent_id: str = None) -> Goal:
        """创建目标"""
        goal = Goal(
            id=f"goal_{datetime.now().timestamp()}",
            title=title,
            description=description,
            status=GoalStatus.DRAFT.value,
            priority=priority,
            created_at=datetime.now().isoformat(),
            deadline=deadline,
            parent_goal_id=parent_id
        )
        
        self.goals.append(goal)
        
        # 如果有父目标，添加到子目标列表
        if parent_id:
            for g in self.goals:
                if g.id == parent_id:
                    g.sub_goals.append(goal.id)
                    break
        
        self.save()
        return goal
    
    def activate(self, goal_id: str):
        """激活目标"""
        for goal in self.goals:
            if goal.id == goal_id:
                goal.status = GoalStatus.ACTIVE.value
                goal.updated_at = datetime.now().isoformat()
                self.save()
                return True
        return False
    
    def update_progress(self, goal_id: str, progress: float):
        """更新进度"""
        for goal in self.goals:
            if goal.id == goal_id:
                goal.progress = min(1.0, max(0.0, progress))
                goal.updated_at = datetime.now().isoformat()
                if goal.progress >= 1.0:
                    goal.status = GoalStatus.COMPLETED.value
                    goal.completed_at = datetime.now().isoformat()
                self.save()
                return True
        return False
    
    def get_active(self) -> List[Goal]:
        """获取活跃目标"""
        return [g for g in self.goals if g.status == GoalStatus.ACTIVE.value]
    
    def get_by_priority(self, limit: int = 10) -> List[Goal]:
        """按优先级获取目标"""
        active = self.get_active()
        active.sort(key=lambda g: g.priority, reverse=True)
        return active[:limit]


class TaskDecomposition:
    """任务分解器"""
    
    def __init__(self):
        self.tasks: List[Task] = []
        self.load()
    
    def load(self):
        """加载任务"""
        if Config.TASKS_FILE.exists():
            try:
                with open(Config.TASKS_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.tasks = [Task(**t) for t in data.get("tasks", [])]
            except Exception as e:
                print(f"⚠️ 加载任务失败：{e}")
    
    def save(self):
        """保存任务"""
        Config.TASKS_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(Config.TASKS_FILE, "w", encoding="utf-8") as f:
            json.dump({"tasks": [t.to_dict() for t in self.tasks]}, f, ensure_ascii=False, indent=2)
    
    def decompose(self, goal: Goal, complexity: str = "medium") -> List[Task]:
        """将目标分解为任务"""
        # 基于复杂度生成不同数量的子任务
        task_counts = {"low": 2, "medium": 4, "high": 6}
        count = task_counts.get(complexity, 4)
        
        tasks = []
        for i in range(count):
            task = Task(
                id=f"task_{datetime.now().timestamp()}_{i}",
                title=f"{goal.title} - 步骤 {i+1}",
                description=f"完成目标 '{goal.title}' 的第 {i+1} 步",
                status=TaskStatus.PENDING.value,
                priority=goal.priority,
                goal_id=goal.id,
                created_at=datetime.now().isoformat(),
                estimated_duration=Config.DEFAULT_TASK_DURATION
            )
            
            # 设置依赖关系
            if i > 0:
                task.dependencies = [tasks[i-1].id]
            
            tasks.append(task)
            self.tasks.append(task)
        
        self.save()
        return tasks
    
    def get_pending(self, goal_id: str = None) -> List[Task]:
        """获取待处理任务"""
        pending = [t for t in self.tasks if t.status == TaskStatus.PENDING.value]
        if goal_id:
            pending = [t for t in pending if t.goal_id == goal_id]
        return pending
    
    def start(self, task_id: str):
        """开始任务"""
        for task in self.tasks:
            if task.id == task_id:
                task.status = TaskStatus.IN_PROGRESS.value
                task.started_at = datetime.now().isoformat()
                self.save()
                return True
        return False
    
    def complete(self, task_id: str, actual_duration: int = None):
        """完成任务"""
        for task in self.tasks:
            if task.id == task_id:
                task.status = TaskStatus.COMPLETED.value
                task.completed_at = datetime.now().isoformat()
                task.progress = 1.0
                task.actual_duration = actual_duration
                self.save()
                return True
        return False
    
    def get_by_goal(self, goal_id: str) -> List[Task]:
        """获取目标的所有任务"""
        return [t for t in self.tasks if t.goal_id == goal_id]


class Scheduler:
    """调度器"""
    
    def __init__(self):
        self.schedule: List[ScheduleEntry] = []
        self.load()
    
    def load(self):
        """加载日程"""
        if Config.SCHEDULE_FILE.exists():
            try:
                with open(Config.SCHEDULE_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.schedule = [ScheduleEntry(**s) for s in data.get("entries", [])]
            except Exception as e:
                print(f"⚠️ 加载日程失败：{e}")
    
    def save(self):
        """保存日程"""
        Config.SCHEDULE_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(Config.SCHEDULE_FILE, "w", encoding="utf-8") as f:
            json.dump({"entries": [s.to_dict() for s in self.schedule]}, f, ensure_ascii=False, indent=2)
    
    def schedule_task(self, task: Task, start_time: datetime = None) -> ScheduleEntry:
        """调度任务"""
        if start_time is None:
            start_time = datetime.now()
        
        end_time = start_time + timedelta(minutes=task.estimated_duration)
        
        entry = ScheduleEntry(
            id=f"schedule_{datetime.now().timestamp()}",
            task_id=task.id,
            start_time=start_time.isoformat(),
            end_time=end_time.isoformat(),
            status="scheduled",
            created_at=datetime.now().isoformat()
        )
        
        self.schedule.append(entry)
        self.save()
        return entry
    
    def get_today(self) -> List[ScheduleEntry]:
        """获取今天的日程"""
        today = datetime.now().date()
        return [
            s for s in self.schedule
            if datetime.fromisoformat(s.start_time).date() == today
        ]
    
    def get_next(self) -> Optional[ScheduleEntry]:
        """获取下一个日程"""
        now = datetime.now()
        future = [s for s in self.schedule if datetime.fromisoformat(s.start_time) > now]
        if future:
            future.sort(key=lambda s: s.start_time)
            return future[0]
        return None


class ProgressTracker:
    """进度追踪器"""
    
    def __init__(self, goal_manager: GoalManager, task_decomposition: TaskDecomposition):
        self.goal_manager = goal_manager
        self.task_decomposition = task_decomposition
    
    def calculate_goal_progress(self, goal_id: str) -> float:
        """计算目标进度"""
        tasks = self.task_decomposition.get_by_goal(goal_id)
        if not tasks:
            return 0.0
        
        completed = sum(1 for t in tasks if t.status == TaskStatus.COMPLETED.value)
        return completed / len(tasks)
    
    def update_all_goals(self):
        """更新所有目标的进度"""
        for goal in self.goal_manager.goals:
            progress = self.calculate_goal_progress(goal.id)
            self.goal_manager.update_progress(goal.id, progress)
    
    def get_summary(self) -> Dict:
        """获取进度摘要"""
        goals = self.goal_manager.goals
        tasks = self.task_decomposition.tasks
        
        return {
            "total_goals": len(goals),
            "active_goals": len([g for g in goals if g.status == GoalStatus.ACTIVE.value]),
            "completed_goals": len([g for g in goals if g.status == GoalStatus.COMPLETED.value]),
            "total_tasks": len(tasks),
            "pending_tasks": len([t for t in tasks if t.status == TaskStatus.PENDING.value]),
            "in_progress_tasks": len([t for t in tasks if t.status == TaskStatus.IN_PROGRESS.value]),
            "completed_tasks": len([t for t in tasks if t.status == TaskStatus.COMPLETED.value]),
            "overall_progress": self.calculate_overall_progress()
        }
    
    def calculate_overall_progress(self) -> float:
        """计算总体进度"""
        goals = self.goal_manager.goals
        if not goals:
            return 0.0
        
        total_progress = sum(g.progress for g in goals)
        return total_progress / len(goals)


# ============================================================================
# 规划系统主控制器
# ============================================================================

class PlanningSystem:
    """规划系统主控制器"""
    
    def __init__(self):
        self.goal_manager = GoalManager()
        self.task_decomposition = TaskDecomposition()
        self.scheduler = Scheduler()
        self.progress_tracker = ProgressTracker(self.goal_manager, self.task_decomposition)
    
    def create_goal(self, title: str, description: str, priority: str = "medium",
                   deadline: str = None) -> Goal:
        """创建目标"""
        priority_map = {
            "critical": Config.PRIORITY_CRITICAL,
            "high": Config.PRIORITY_HIGH,
            "medium": Config.PRIORITY_MEDIUM,
            "low": Config.PRIORITY_LOW
        }
        
        goal = self.goal_manager.create(
            title=title,
            description=description,
            priority=priority_map.get(priority, Config.PRIORITY_MEDIUM),
            deadline=deadline
        )
        
        # 激活目标
        self.goal_manager.activate(goal.id)
        
        # 分解为目标
        complexity = "medium"
        if priority in ["critical", "high"]:
            complexity = "high"
        elif priority == "low":
            complexity = "low"
        
        tasks = self.task_decomposition.decompose(goal, complexity)
        
        # 调度前几个任务
        now = datetime.now()
        for i, task in enumerate(tasks[:3]):
            start = now + timedelta(minutes=i*30)
            self.scheduler.schedule_task(task, start)
        
        return goal
    
    def get_status(self) -> Dict:
        """获取状态"""
        return {
            "version": "2.1.0",
            "timestamp": datetime.now().isoformat(),
            "summary": self.progress_tracker.get_summary(),
            "active_goals": [g.to_dict() for g in self.goal_manager.get_by_priority(5)],
            "next_schedule": self.scheduler.get_next().to_dict() if self.scheduler.get_next() else None
        }
    
    def think_about_goals(self) -> List[str]:
        """思考目标 - 生成建议"""
        suggestions = []
        
        # 检查即将到期的目标
        now = datetime.now()
        for goal in self.goal_manager.get_active():
            if goal.deadline:
                deadline = datetime.fromisoformat(goal.deadline)
                days_left = (deadline - now).days
                if days_left < 3:
                    suggestions.append(f"⚠️ 目标 '{goal.title}' 即将到期 ({days_left}天)")
            
            if goal.progress < 0.5:
                suggestions.append(f"📊 目标 '{goal.title}' 进度滞后 ({goal.progress:.0%})")
        
        # 检查任务
        pending = self.task_decomposition.get_pending()
        if len(pending) > 10:
            suggestions.append(f"📋 有 {len(pending)} 个待处理任务，建议优先处理高优先级")
        
        if not suggestions:
            suggestions.append("✅ 所有目标和任务都在正轨上")
        
        return suggestions


# ============================================================================
# CLI
# ============================================================================

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="规划系统 v2.1")
    parser.add_argument("--status", action="store_true", help="显示状态")
    parser.add_argument("--create-goal", type=str, help="创建目标 (格式：title|description|priority)")
    parser.add_argument("--think", action="store_true", help="思考目标")
    parser.add_argument("--test", action="store_true", help="运行测试")
    
    args = parser.parse_args()
    
    system = PlanningSystem()
    
    if args.status:
        status = system.get_status()
        print(json.dumps(status, ensure_ascii=False, indent=2))
    
    elif args.create_goal:
        parts = args.create_goal.split("|")
        if len(parts) >= 2:
            title, description = parts[0], parts[1]
            priority = parts[2] if len(parts) > 2 else "medium"
            goal = system.create_goal(title, description, priority)
            print(f"✅ 已创建目标：{goal.title}")
            print(f"   ID: {goal.id}")
            print(f"   优先级：{goal.priority}")
            print(f"   分解为 {len(system.task_decomposition.get_by_goal(goal.id))} 个任务")
        else:
            print("❌ 格式错误，请使用：title|description|priority")
    
    elif args.think:
        suggestions = system.think_about_goals()
        print("🧠 目标思考结果:")
        for s in suggestions:
            print(f"   {s}")
    
    elif args.test:
        print("🧪 运行测试...")
        test_planning_system(system)
    
    else:
        parser.print_help()


def test_planning_system(system: PlanningSystem):
    """测试规划系统"""
    # 创建测试目标
    print("\n1. 创建测试目标...")
    goal = system.create_goal(
        "学习 AI 架构",
        "学习 LangChain、GPT-Engineer 等开源项目的架构设计",
        "high"
    )
    print(f"   ✅ 创建目标：{goal.title}")
    
    # 查看状态
    print("\n2. 查看状态...")
    status = system.get_status()
    print(f"   总目标数：{status['summary']['total_goals']}")
    print(f"   活跃目标：{status['summary']['active_goals']}")
    print(f"   总任务数：{status['summary']['total_tasks']}")
    print(f"   总体进度：{status['summary']['overall_progress']:.0%}")
    
    # 思考
    print("\n3. 思考目标...")
    suggestions = system.think_about_goals()
    for s in suggestions:
        print(f"   {s}")
    
    print("\n✅ 测试完成")


if __name__ == "__main__":
    main()
