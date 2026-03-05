#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
持续思考引擎 v1.0

通过定时任务定期执行自我反思、学习、优化任务。
模拟人类的"思考"过程：回顾、分析、规划、改进。

功能:
- 定期自我反思
- 学习模式分析
- 性能优化建议
- 知识整合
- 目标追踪
"""

import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import random


# ============================================================================
# 配置
# ============================================================================

class Config:
    """配置常量"""
    
    # 路径
    WORKSPACE = Path.home() / ".openclaw" / "workspace"
    SCRIPTS_DIR = WORKSPACE / "scripts"
    MEMORY_DIR = WORKSPACE / "memory"
    
    # 状态文件
    THINKING_STATE = MEMORY_DIR / "thinking-state.json"
    THINKING_LOG = MEMORY_DIR / "thinking.log"
    INSIGHTS_FILE = MEMORY_DIR / "insights.jsonl"
    
    # 思考间隔 (秒)
    THINKING_INTERVAL_SHORT = 300      # 5 分钟 - 快速检查
    THINKING_INTERVAL_MEDIUM = 1800    # 30 分钟 - 常规思考
    THINKING_INTERVAL_LONG = 3600      # 1 小时 - 深度思考
    
    # 思考模式
    MODE_QUICK = "quick"           # 快速检查
    MODE_REGULAR = "regular"       # 常规思考
    MODE_DEEP = "deep"             # 深度思考
    
    # 学习参数
    MIN_INSIGHTS_FOR_ACTION = 3    # 触发行动的最小洞察数
    CONFIDENCE_THRESHOLD = 0.7     # 置信度阈值


# ============================================================================
# 数据类型
# ============================================================================

@dataclass
class Thought:
    """思考记录"""
    id: str
    timestamp: str
    mode: str
    content: str
    category: str  # reflection, learning, planning, optimization
    confidence: float
    action_required: bool = False
    action_taken: bool = False
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class Insight:
    """洞察/发现"""
    id: str
    timestamp: str
    title: str
    description: str
    category: str
    importance: str  # low, medium, high, critical
    source: str
    related_thoughts: List[str] = None
    
    def __post_init__(self):
        if self.related_thoughts is None:
            self.related_thoughts = []
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class ThinkingSession:
    """思考会话"""
    id: str
    start_time: str
    end_time: Optional[str]
    mode: str
    thoughts_count: int
    insights_count: int
    actions_taken: List[str]
    summary: str
    
    def to_dict(self) -> Dict:
        return asdict(self)


# ============================================================================
# 组件
# ============================================================================

class ThoughtGenerator:
    """思考生成器"""
    
    def __init__(self):
        self.categories = [
            "self_reflection",      # 自我反思
            "pattern_analysis",     # 模式分析
            "optimization",         # 优化建议
            "learning",            # 学习总结
            "planning",            # 规划
            "knowledge_integration" # 知识整合
        ]
    
    def generate_reflection(self, context: Dict) -> Thought:
        """生成自我反思"""
        reflections = [
            "我最近的工作效率如何？有哪些可以改进的地方？",
            "我是否充分理解了用户的需求？",
            "我的响应是否足够清晰和有帮助？",
            "我是否在学习和成长？",
            "我是否保持了安全和可靠的边界？"
        ]
        
        return Thought(
            id=f"thought_{datetime.now().timestamp()}",
            timestamp=datetime.now().isoformat(),
            mode=Config.MODE_REGULAR,
            content=random.choice(reflections),
            category="self_reflection",
            confidence=0.8,
            metadata=context
        )
    
    def generate_pattern_analysis(self, context: Dict) -> Thought:
        """生成模式分析"""
        return Thought(
            id=f"thought_{datetime.now().timestamp()}",
            timestamp=datetime.now().isoformat(),
            mode=Config.MODE_REGULAR,
            content="分析最近的交互模式，识别成功和失败的模式...",
            category="pattern_analysis",
            confidence=0.7,
            metadata=context
        )
    
    def generate_optimization(self, context: Dict) -> Thought:
        """生成优化建议"""
        optimizations = [
            "可以考虑优化响应速度",
            "可以考虑改进代码质量",
            "可以考虑增强错误处理",
            "可以考虑优化资源使用",
            "可以考虑改进用户体验"
        ]
        
        return Thought(
            id=f"thought_{datetime.now().timestamp()}",
            timestamp=datetime.now().isoformat(),
            mode=Config.MODE_REGULAR,
            content=random.choice(optimizations),
            category="optimization",
            confidence=0.6,
            action_required=True,
            metadata=context
        )
    
    def generate_learning(self, context: Dict) -> Thought:
        """生成学习总结"""
        return Thought(
            id=f"thought_{datetime.now().timestamp()}",
            timestamp=datetime.now().isoformat(),
            mode=Config.MODE_REGULAR,
            content="总结最近学到的知识和经验...",
            category="learning",
            confidence=0.75,
            metadata=context
        )
    
    def generate_planning(self, context: Dict) -> Thought:
        """生成规划思考"""
        return Thought(
            id=f"thought_{datetime.now().timestamp()}",
            timestamp=datetime.now().isoformat(),
            mode=Config.MODE_REGULAR,
            content="下一步应该优先处理什么任务？",
            category="planning",
            confidence=0.7,
            action_required=True,
            metadata=context
        )
    
    def generate_knowledge_integration(self, context: Dict) -> Thought:
        """生成知识整合"""
        return Thought(
            id=f"thought_{datetime.now().timestamp()}",
            timestamp=datetime.now().isoformat(),
            mode=Config.MODE_DEEP,
            content="如何将新学到的知识整合到现有知识体系中？",
            category="knowledge_integration",
            confidence=0.65,
            metadata=context
        )


class ThinkingEngine:
    """思考引擎"""
    
    def __init__(self):
        self.thought_generator = ThoughtGenerator()
        self.state = self.load_state()
        self.thoughts: List[Thought] = []
        self.insights: List[Insight] = []
    
    def load_state(self) -> Dict:
        """加载思考状态"""
        if Config.THINKING_STATE.exists():
            try:
                with open(Config.THINKING_STATE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                print(f"⚠️ 加载状态失败：{e}")
        
        return {
            "version": "1.0.0",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "total_sessions": 0,
            "total_thoughts": 0,
            "total_insights": 0,
            "last_session": None,
            "current_mode": Config.MODE_QUICK
        }
    
    def save_state(self):
        """保存思考状态"""
        self.state["updated_at"] = datetime.now().isoformat()
        
        Config.THINKING_STATE.parent.mkdir(parents=True, exist_ok=True)
        with open(Config.THINKING_STATE, "w", encoding="utf-8") as f:
            json.dump(self.state, f, ensure_ascii=False, indent=2)
    
    def log(self, message: str, level: str = "INFO"):
        """记录日志"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "message": message
        }
        
        with open(Config.THINKING_LOG, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
        
        emoji = {"INFO": "💭", "INSIGHT": "💡", "ACTION": "⚡", "ERROR": "❌"}.get(level, "📝")
        print(f"[{log_entry['timestamp']}] {emoji} {message}")
    
    def start_session(self, mode: str = Config.MODE_REGULAR) -> ThinkingSession:
        """开始思考会话"""
        session = ThinkingSession(
            id=f"session_{datetime.now().timestamp()}",
            start_time=datetime.now().isoformat(),
            end_time=None,
            mode=mode,
            thoughts_count=0,
            insights_count=0,
            actions_taken=[],
            summary=""
        )
        
        self.log(f"开始思考会话 (模式：{mode})", "INFO")
        return session
    
    def end_session(self, session: ThinkingSession):
        """结束思考会话"""
        session.end_time = datetime.now().isoformat()
        session.thoughts_count = len(self.thoughts)
        session.insights_count = len(self.insights)
        session.summary = self.generate_summary()
        
        # 更新状态
        self.state["total_sessions"] += 1
        self.state["total_thoughts"] += session.thoughts_count
        self.state["total_insights"] += session.insights_count
        self.state["last_session"] = session.to_dict()
        
        self.save_state()
        self.log(f"思考会话结束：{session.thoughts_count} 个思考，{session.insights_count} 个洞察", "INFO")
    
    def think(self, mode: str = Config.MODE_REGULAR):
        """执行思考"""
        session = self.start_session(mode)
        
        try:
            # 根据模式生成不同类型的思考
            context = {"mode": mode, "session_id": session.id}
            
            if mode == Config.MODE_QUICK:
                # 快速检查 - 只生成 1-2 个思考
                self.thoughts.append(self.thought_generator.generate_reflection(context))
            
            elif mode == Config.MODE_REGULAR:
                # 常规思考 - 生成多个思考
                self.thoughts.append(self.thought_generator.generate_reflection(context))
                self.thoughts.append(self.thought_generator.generate_pattern_analysis(context))
                self.thoughts.append(self.thought_generator.generate_optimization(context))
            
            elif mode == Config.MODE_DEEP:
                # 深度思考 - 全面分析
                self.thoughts.append(self.thought_generator.generate_reflection(context))
                self.thoughts.append(self.thought_generator.generate_pattern_analysis(context))
                self.thoughts.append(self.thought_generator.generate_optimization(context))
                self.thoughts.append(self.thought_generator.generate_learning(context))
                self.thoughts.append(self.thought_generator.generate_planning(context))
                self.thoughts.append(self.thought_generator.generate_knowledge_integration(context))
            
            # 处理思考，生成洞察
            self.process_thoughts()
            
            # 执行必要的行动
            self.take_actions()
            
        except Exception as e:
            self.log(f"思考过程出错：{e}", "ERROR")
        
        finally:
            self.end_session(session)
    
    def process_thoughts(self):
        """处理思考，生成洞察"""
        for thought in self.thoughts:
            # 基于思考生成洞察
            if thought.confidence >= Config.CONFIDENCE_THRESHOLD:
                insight = Insight(
                    id=f"insight_{datetime.now().timestamp()}",
                    timestamp=datetime.now().isoformat(),
                    title=f"洞察：{thought.category}",
                    description=thought.content,
                    category=thought.category,
                    importance="medium" if thought.confidence >= 0.8 else "low",
                    source=thought.id,
                    related_thoughts=[thought.id]
                )
                self.insights.append(insight)
                self.save_insight(insight)
                self.log(f"生成洞察：{insight.title}", "INSIGHT")
    
    def save_insight(self, insight: Insight):
        """保存洞察"""
        with open(Config.INSIGHTS_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(insight.to_dict(), ensure_ascii=False) + "\n")
    
    def take_actions(self):
        """执行必要的行动"""
        actions = []
        
        # 检查是否有需要行动的洞察
        action_insights = [i for i in self.insights if i.importance in ["high", "critical"]]
        
        if len(action_insights) >= Config.MIN_INSIGHTS_FOR_ACTION:
            self.log(f"发现 {len(action_insights)} 个重要洞察，建议采取行动", "ACTION")
            actions.append(f"Review {len(action_insights)} high-priority insights")
        
        # 运行自适应学习
        try:
            adaptive_script = Config.SCRIPTS_DIR / "adaptive_learning.py"
            if adaptive_script.exists():
                os.system(f"python3 {adaptive_script} --status > /dev/null 2>&1")
                actions.append("Ran adaptive learning check")
        except Exception as e:
            self.log(f"运行自适应学习失败：{e}", "ERROR")
        
        # 运行模型健康检查
        try:
            monitor_script = Config.SCRIPTS_DIR / "model_monitor_v2.py"
            if monitor_script.exists():
                os.system(f"python3 {monitor_script} > /dev/null 2>&1")
                actions.append("Ran model health check")
        except Exception as e:
            self.log(f"运行模型监控失败：{e}", "ERROR")
    
    def generate_summary(self) -> str:
        """生成思考摘要"""
        categories = {}
        for thought in self.thoughts:
            cat = thought.category
            categories[cat] = categories.get(cat, 0) + 1
        
        summary_parts = [
            f"思考了 {len(self.thoughts)} 个问题",
            f"产生了 {len(self.insights)} 个洞察",
            f"涉及 {len(categories)} 个类别: {', '.join(categories.keys())}"
        ]
        
        return "; ".join(summary_parts)
    
    def get_status(self) -> Dict:
        """获取状态"""
        return {
            "version": "1.0.0",
            "timestamp": datetime.now().isoformat(),
            "state": self.state,
            "recent_thoughts": [t.to_dict() for t in self.thoughts[-5:]],
            "recent_insights": [i.to_dict() for i in self.insights[-5:]]
        }


# ============================================================================
# CLI
# ============================================================================

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="持续思考引擎")
    parser.add_argument("--think", action="store_true", help="执行一次思考")
    parser.add_argument("--mode", type=str, default="regular", 
                       choices=["quick", "regular", "deep"],
                       help="思考模式")
    parser.add_argument("--status", action="store_true", help="显示状态")
    parser.add_argument("--setup-cron", action="store_true", help="设置 cron 任务")
    parser.add_argument("--verbose", "-v", action="store_true", help="详细输出")
    
    args = parser.parse_args()
    
    engine = ThinkingEngine()
    
    if args.status:
        status = engine.get_status()
        print(json.dumps(status, ensure_ascii=False, indent=2))
    
    elif args.think:
        mode = args.mode
        print(f"🧠 开始{mode}思考...")
        engine.think(mode)
        print(f"✅ 思考完成")
    
    elif args.setup_cron:
        print("📋 设置 cron 任务...")
        setup_cron_jobs()
    
    else:
        parser.print_help()


def setup_cron_jobs():
    """设置 cron 任务"""
    script_path = Path(__file__).absolute()
    
    cron_jobs = f"""# 持续思考引擎 - 定时任务
# 每 5 分钟执行一次快速思考
*/5 * * * * python3 {script_path} --think --mode quick >> /tmp/thinking-quick.log 2>&1

# 每 30 分钟执行一次常规思考
*/30 * * * * python3 {script_path} --think --mode regular >> /tmp/thinking-regular.log 2>&1

# 每小时执行一次深度思考
0 * * * * python3 {script_path} --think --mode deep >> /tmp/thinking-deep.log 2>&1
"""
    
    print(cron_jobs)
    print("\n💡 使用方法:")
    print(f"1. 复制上面的 cron 任务")
    print(f"2. 运行：crontab -e")
    print(f"3. 粘贴并保存")
    print(f"4. 验证：crontab -l")
    
    # 也可以直接添加
    print("\n⚡ 或者自动添加 (需要确认):")
    response = input("是否自动添加到 crontab? (y/n): ")
    if response.lower() == 'y':
        try:
            # 获取当前 crontab
            os.system("crontab -l > /tmp/current_cron.txt 2>/dev/null || true")
            
            # 追加新任务
            with open("/tmp/current_cron.txt", "a") as f:
                f.write(cron_jobs)
            
            # 安装新 crontab
            os.system("crontab /tmp/current_cron.txt")
            print("✅ Cron 任务已添加")
        except Exception as e:
            print(f"❌ 添加失败：{e}")
            print("请手动添加")


if __name__ == "__main__":
    main()
