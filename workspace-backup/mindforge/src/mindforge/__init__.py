"""
MindForge AI - 核心模块
"""

__version__ = "1.0.0"

# 延迟导入，避免循环依赖
def __getattr__(name):
    if name == 'MemorySystem':
        from .core.memory import MemorySystem
        return MemorySystem
    elif name == 'ThoughtEngine':
        from .core.thought import ThoughtEngine
        return ThoughtEngine
    elif name == 'PlanningSystem':
        from .core.planning import PlanningSystem
        return PlanningSystem
    elif name == 'LearningSystem':
        from .core.learning import LearningSystem
        return LearningSystem
    elif name == 'MonitorSystem':
        from .core.monitor import MonitorSystem
        return MonitorSystem
    elif name == 'EvaluationSystem':
        from .core.evaluation import EvaluationSystem
        return EvaluationSystem
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
