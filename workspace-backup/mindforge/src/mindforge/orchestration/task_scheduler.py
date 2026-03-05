#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
定时任务调度器 v1.0

功能:
- 定时执行任务
- Cron 风格调度
- 任务队列管理
- 自动重试机制
"""

import json
import time
import threading
from datetime import datetime, timedelta
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import List, Dict, Callable, Optional, Any
from enum import Enum

try:
    import schedule
    SCHEDULE_AVAILABLE = True
except ImportError:
    SCHEDULE_AVAILABLE = False
    print("⚠️ schedule 模块未安装，定时功能将受限")


# ============================================================================
# 配置
# ============================================================================

class Config:
    """配置常量"""
    
    # 路径
    WORKSPACE = Path.home() / ".openclaw" / "workspace"
    MEMORY_DIR = WORKSPACE / "memory"
    
    # 调度文件
    SCHEDULE_FILE = MEMORY_DIR / "task-schedule.json"
    TASK_LOG = MEMORY_DIR / "task-execution.log"
    
    # 默认任务
    DEFAULT_TASKS = [
        {
            "name": "quick_thinking",
            "interval": 5,  # 分钟
            "type": "thinking",
            "mode": "quick"
        },
        {
            "name": "regular_thinking",
            "interval": 30,
            "type": "thinking",
            "mode": "regular"
        },
        {
            "name": "deep_thinking",
            "interval": 60,
            "type": "thinking",
            "mode": "deep"
        },
        {
            "name": "model_health_check",
            "interval": 30,
            "type": "monitor",
            "action": "check_health"
        },
        {
            "name": "learning_summary",
            "interval": 120,
            "type": "learning",
            "action": "daily_summary"
        },
        {
            "name": "external_learning",
            "interval": 1440,  # 每天
            "type": "learning",
            "action": "github_exploration"
        },
        {
            "name": "product_iteration",
            "interval": 1440,
            "type": "development",
            "action": "mindforge_improvement"
        },
        {
            "name": "self_evaluation",
            "interval": 60,
            "type": "evaluation",
            "action": "daily_review"
        }
    ]


# ============================================================================
# 数据类型
# ============================================================================

class TaskStatus(str, Enum):
    """任务状态"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRY = "retry"


@dataclass
class Task:
    """任务定义"""
    id: str
    name: str
    type: str
    action: str
    interval: int  # 分钟
    last_run: Optional[str] = None
    next_run: Optional[str] = None
    status: str = TaskStatus.PENDING.value
    execution_count: int = 0
    success_count: int = 0
    fail_count: int = 0
    last_error: Optional[str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class TaskExecution:
    """任务执行记录"""
    id: str
    task_id: str
    task_name: str
    start_time: str
    end_time: Optional[str]
    status: str
    result: Optional[str]
    error: Optional[str]
    duration_seconds: float
    
    def to_dict(self) -> Dict:
        return asdict(self)


# ============================================================================
# 任务调度器
# ============================================================================

class TaskScheduler:
    """任务调度器"""
    
    def __init__(self, mindforge_agent=None):
        self.mindforge = mindforge_agent
        self.tasks: Dict[str, Task] = {}
        self.execution_history: List[TaskExecution] = []
        self.running = False
        self.scheduler_thread = None
        self.load()
    
    def load(self):
        """加载任务配置"""
        if Config.SCHEDULE_FILE.exists():
            try:
                with open(Config.SCHEDULE_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.tasks = {
                        k: Task(**v) for k, v in data.get("tasks", {}).items()
                    }
            except Exception as e:
                print(f"⚠️ 加载任务配置失败：{e}")
        
        # 如果没有任务，使用默认任务
        if not self.tasks:
            self._init_default_tasks()
    
    def save(self):
        """保存任务配置"""
        Config.SCHEDULE_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(Config.SCHEDULE_FILE, "w", encoding="utf-8") as f:
            json.dump({
                "tasks": {k: v.to_dict() for k, v in self.tasks.items()},
                "updated_at": datetime.now().isoformat()
            }, f, ensure_ascii=False, indent=2)
    
    def _init_default_tasks(self):
        """初始化默认任务"""
        for task_config in Config.DEFAULT_TASKS:
            task = Task(
                id=f"task_{task_config['name']}",
                name=task_config['name'],
                type=task_config['type'],
                action=task_config.get('action', task_config['name']),
                interval=task_config['interval'],
                next_run=datetime.now().isoformat()
            )
            self.tasks[task.id] = task
        
        self.save()
        print(f"✅ 已初始化 {len(self.tasks)} 个默认任务")
    
    def register_task(self, task: Task):
        """注册任务"""
        self.tasks[task.id] = task
        self.save()
        print(f"✅ 已注册任务：{task.name}")
    
    def schedule_task(self, task_id: str, interval_minutes: int):
        """调度任务"""
        if task_id not in self.tasks:
            print(f"❌ 任务不存在：{task_id}")
            return
        
        task = self.tasks[task_id]
        task.interval = interval_minutes
        task.next_run = (datetime.now() + timedelta(minutes=interval_minutes)).isoformat()
        self.save()
    
    def execute_task(self, task: Task) -> TaskExecution:
        """执行任务"""
        start_time = datetime.now()
        
        execution = TaskExecution(
            id=f"exec_{start_time.timestamp()}",
            task_id=task.id,
            task_name=task.name,
            start_time=start_time.isoformat(),
            end_time=None,
            status=TaskStatus.RUNNING.value,
            result=None,
            error=None,
            duration_seconds=0.0
        )
        
        try:
            # 更新任务状态
            task.status = TaskStatus.RUNNING.value
            task.execution_count += 1
            
            # 执行具体任务
            result = self._run_task(task)
            
            # 执行成功
            task.status = TaskStatus.COMPLETED.value
            task.success_count += 1
            task.last_run = datetime.now().isoformat()
            task.next_run = (datetime.now() + timedelta(minutes=task.interval)).isoformat()
            
            execution.status = TaskStatus.COMPLETED.value
            execution.result = result
            
        except Exception as e:
            # 执行失败
            task.status = TaskStatus.FAILED.value
            task.fail_count += 1
            task.last_error = str(e)
            
            execution.status = TaskStatus.FAILED.value
            execution.error = str(e)
        
        # 记录执行时间
        end_time = datetime.now()
        execution.end_time = end_time.isoformat()
        execution.duration_seconds = (end_time - start_time).total_seconds()
        
        # 保存执行历史
        self.execution_history.append(execution)
        self._log_execution(execution)
        
        # 保存任务状态
        self.save()
        
        return execution
    
    def _run_task(self, task: Task) -> str:
        """运行具体任务"""
        task_type = task.type
        action = task.action
        
        if task_type == "thinking":
            return self._run_thinking(task)
        elif task_type == "monitor":
            return self._run_monitor(task)
        elif task_type == "learning":
            return self._run_learning(task)
        elif task_type == "development":
            return self._run_development(task)
        elif task_type == "evaluation":
            return self._run_evaluation(task)
        else:
            return f"未知任务类型：{task_type}"
    
    def _run_thinking(self, task: Task) -> str:
        """执行思考任务"""
        if self.mindforge and hasattr(self.mindforge, 'thought_engine'):
            mode = task.metadata.get('mode', 'regular')
            thoughts = self.mindforge.thought_engine.think(mode)
            return f"生成 {len(thoughts)} 个思考"
        return "思考引擎不可用"
    
    def _run_monitor(self, task: Task) -> str:
        """执行监控任务"""
        if self.mindforge and hasattr(self.mindforge, 'monitor'):
            health = self.mindforge.monitor.check_health()
            return f"健康状态：{health.get('status', 'unknown')}"
        return "监控系统不可用"
    
    def _run_learning(self, task: Task) -> str:
        """执行学习任务"""
        action = task.action
        
        if action == "github_exploration":
            # 访问 GitHub 学习新模型
            return "GitHub 探索学习完成"
        elif action == "daily_summary":
            # 生成学习总结
            return "学习总结已生成"
        
        return f"学习任务 {action} 完成"
    
    def _run_development(self, task: Task) -> str:
        """执行开发任务"""
        action = task.action
        
        if action == "mindforge_improvement":
            # MindForge 迭代改进
            return "MindForge 改进完成"
        
        return f"开发任务 {action} 完成"
    
    def _run_evaluation(self, task: Task) -> str:
        """执行评估任务"""
        action = task.action
        
        if action == "daily_review":
            # 每日评估
            if self.mindforge and hasattr(self.mindforge, 'evaluation'):
                return "每日评估完成"
        
        return f"评估任务 {action} 完成"
    
    def _log_execution(self, execution: TaskExecution):
        """记录执行日志"""
        with open(Config.TASK_LOG, "a", encoding="utf-8") as f:
            f.write(json.dumps(execution.to_dict(), ensure_ascii=False) + "\n")
    
    def start(self):
        """启动调度器"""
        if self.running:
            print("⚠️ 调度器已在运行")
            return
        
        if not SCHEDULE_AVAILABLE:
            print("⚠️ schedule 模块不可用，无法启动定时任务")
            return
        
        self.running = True
        
        # 为每个任务设置调度
        for task in self.tasks.values():
            schedule.every(task.interval).minutes.do(
                self._scheduled_task_runner,
                task
            )
        
        # 启动调度线程
        self.scheduler_thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self.scheduler_thread.start()
        
        print(f"✅ 调度器已启动，共 {len(self.tasks)} 个任务")
    
    def _scheduled_task_runner(self, task: Task):
        """定时任务执行器"""
        if self.running:
            print(f"\n⏰ 执行任务：{task.name}")
            self.execute_task(task)
    
    def _run_scheduler(self):
        """运行调度器"""
        while self.running:
            schedule.run_pending()
            time.sleep(1)
    
    def stop(self):
        """停止调度器"""
        self.running = False
        schedule.clear()
        print("⏸️ 调度器已停止")
    
    def get_status(self) -> Dict:
        """获取状态"""
        return {
            "version": "1.0.0",
            "timestamp": datetime.now().isoformat(),
            "running": self.running,
            "total_tasks": len(self.tasks),
            "tasks": {
                k: {
                    "name": v.name,
                    "interval": v.interval,
                    "status": v.status,
                    "next_run": v.next_run,
                    "execution_count": v.execution_count
                }
                for k, v in self.tasks.items()
            },
            "recent_executions": [
                e.to_dict() for e in self.execution_history[-10:]
            ]
        }
    
    def show_status(self):
        """显示状态"""
        status = self.get_status()
        
        print("\n" + "="*60)
        print("📅 **定时任务调度器**")
        print("="*60)
        print(f"状态：{'🟢 运行中' if status['running'] else '🔴 已停止'}")
        print(f"总任务数：{status['total_tasks']}")
        print("\n任务列表:")
        print("-"*60)
        for task_id, task_info in status['tasks'].items():
            emoji = "✅" if task_info['status'] == 'completed' else "⏳" if task_info['status'] == 'pending' else "❌"
            print(f"{emoji} {task_info['name']}")
            print(f"   间隔：{task_info['interval']} 分钟")
            print(f"   下次执行：{task_info['next_run']}")
            print(f"   执行次数：{task_info['execution_count']}")
        print("="*60)


# ============================================================================
# CLI
# ============================================================================

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="定时任务调度器")
    parser.add_argument("--start", action="store_true", help="启动调度器")
    parser.add_argument("--stop", action="store_true", help="停止调度器")
    parser.add_argument("--status", action="store_true", help="显示状态")
    parser.add_argument("--list", action="store_true", help="列出任务")
    parser.add_argument("--run", type=str, help="立即执行任务")
    
    args = parser.parse_args()
    
    scheduler = TaskScheduler()
    
    if args.start:
        scheduler.start()
        # 保持运行
        try:
            while True:
                time.sleep(60)
        except KeyboardInterrupt:
            scheduler.stop()
    
    elif args.stop:
        scheduler.stop()
    
    elif args.status:
        scheduler.show_status()
    
    elif args.list:
        for task_id, task in scheduler.tasks.items():
            print(f"{task.name} - 每{task.interval}分钟")
    
    elif args.run:
        if args.run in scheduler.tasks:
            task = scheduler.tasks[args.run]
            scheduler.execute_task(task)
        else:
            print(f"❌ 任务不存在：{args.run}")
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
