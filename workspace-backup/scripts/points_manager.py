#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
积分管理系统 v1.0

功能:
- 记录积分变化
- 自动计算等级
- 生成统计报告
- 警戒状态提醒
"""

import json
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional
from enum import Enum


# ============================================================================
# 配置
# ============================================================================

class Config:
    """配置常量"""
    
    # 路径
    WORKSPACE = Path.home() / ".openclaw" / "workspace"
    MEMORY_DIR = WORKSPACE / "memory"
    
    # 积分文件
    POINTS_FILE = MEMORY_DIR / "points-state.json"
    POINTS_LOG = MEMORY_DIR / "points-log.jsonl"
    
    # 分数阈值
    STARTING_POINTS = 80
    PASSING_LINE = 60
    EXCELLENT_LINE = 85
    MAX_POINTS = 100
    
    # 积分规则
    POINTS_RULES = {
        # 加分项
        "complete_learning_plan": 5,
        "learn_new_technology": 5,
        "deep_learning": 3,
        "share_insights": 3,
        "master_new_skill": 10,
        "external_exploration": 5,
        "complete_feature": 5,
        "code_quality": 3,
        "documentation": 2,
        "optimize_code": 3,
        "innovation": 10,
        "bug_fix": 2,
        "unit_test": 2,
        "early_completion": 2,
        "time_management": 3,
        "tool_optimization": 5,
        "automation": 5,
        "zero_bug_week": 5,
        "user_satisfaction": 5,
        "code_review_pass": 3,
        "performance_boost": 10,
        "safety_compliance": 5,
        "safety_report": 5,
        
        # 扣分项
        "code_bug": -2,
        "critical_bug": -5,
        "fatal_bug": -10,
        "repeat_bug": -5,
        "poor_code_quality": -3,
        "time_waste": -2,
        "task_delay": -3,
        "repeated_work": -2,
        "inefficient_tool_use": -1,
        "incomplete_learning": -3,
        "not_focused": -2,
        "no_notes": -1,
        "no_review": -2,
        "safety_minor_violation": -5,
        "safety_medium_violation": -10,
        "safety_serious_violation": -20,
        "info_leak": -20,
        "system_crash": -3,
        "resource_waste": -2,
        "no_report": -1,
        "late_response": -2,
    }


# ============================================================================
# 数据类型
# ============================================================================

class GradeLevel(str, Enum):
    """等级"""
    S = "S"  # 90-100 卓越
    A = "A"  # 85-89 优秀
    B = "B"  # 70-84 良好
    C = "C"  # 60-69 及格
    D = "D"  # <60 不及格


@dataclass
class PointsRecord:
    """积分记录"""
    id: str
    timestamp: str
    action: str
    score_change: int
    reason: str
    category: str
    before_points: int
    after_points: int
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class PointsState:
    """积分状态"""
    current_points: int
    grade: str
    history: List[Dict]
    today_change: int
    week_change: int
    last_updated: str
    
    def to_dict(self) -> Dict:
        return asdict(self)


# ============================================================================
# 积分管理器
# ============================================================================

class PointsManager:
    """积分管理器"""
    
    def __init__(self):
        self.state = self.load_state()
    
    def load_state(self) -> PointsState:
        """加载状态"""
        if Config.POINTS_FILE.exists():
            try:
                with open(Config.POINTS_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return PointsState(**data)
            except Exception as e:
                print(f"⚠️ 加载状态失败：{e}")
        
        # 初始状态
        return PointsState(
            current_points=Config.STARTING_POINTS,
            grade=GradeLevel.B.value,
            history=[],
            today_change=0,
            week_change=0,
            last_updated=datetime.now().isoformat()
        )
    
    def save_state(self):
        """保存状态"""
        self.state.last_updated = datetime.now().isoformat()
        Config.POINTS_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(Config.POINTS_FILE, "w", encoding="utf-8") as f:
            json.dump(self.state.to_dict(), f, ensure_ascii=False, indent=2)
    
    def calculate_grade(self, points: int) -> str:
        """计算等级"""
        if points >= 90:
            return GradeLevel.S.value
        elif points >= 85:
            return GradeLevel.A.value
        elif points >= 70:
            return GradeLevel.B.value
        elif points >= 60:
            return GradeLevel.C.value
        else:
            return GradeLevel.D.value
    
    def get_emoji(self, grade: str) -> str:
        """获取等级表情"""
        emojis = {
            "S": "🏆",
            "A": "✅",
            "B": "👍",
            "C": "⚠️",
            "D": "❌"
        }
        return emojis.get(grade, "📊")
    
    def add_points(self, action: str, reason: str, category: str = "其他"):
        """添加积分"""
        points_change = Config.POINTS_RULES.get(action, 0)
        
        if points_change == 0:
            print(f"⚠️ 未知的积分项：{action}")
            points_change = int(input("请输入积分变化值："))
        
        self.record_change(action, points_change, reason, category)
    
    def record_change(self, action: str, change: int, reason: str, category: str):
        """记录积分变化"""
        before = self.state.current_points
        after = before + change
        
        # 限制在 0-100 范围内
        after = max(0, min(Config.MAX_POINTS, after))
        actual_change = after - before
        
        record = PointsRecord(
            id=f"points_{datetime.now().timestamp()}",
            timestamp=datetime.now().isoformat(),
            action=action,
            score_change=actual_change,
            reason=reason,
            category=category,
            before_points=before,
            after_points=after
        )
        
        # 更新状态
        self.state.current_points = after
        self.state.grade = self.calculate_grade(after)
        self.state.history.append(record.to_dict())
        self.state.today_change += actual_change
        self.state.week_change += actual_change
        
        # 保存
        self.save_state()
        self.save_log(record)
        
        # 显示结果
        self.show_change(record)
        
        # 检查状态
        self.check_status()
    
    def save_log(self, record: PointsRecord):
        """保存日志"""
        with open(Config.POINTS_LOG, "a", encoding="utf-8") as f:
            f.write(json.dumps(record.to_dict(), ensure_ascii=False) + "\n")
    
    def show_change(self, record: PointsRecord):
        """显示变化"""
        emoji = "➕" if record.score_change > 0 else "➖" if record.score_change < 0 else "➖"
        sign = "+" if record.score_change > 0 else ""
        
        print(f"\n{emoji} **积分变化**")
        print(f"行为：{record.action}")
        print(f"变化：{sign}{record.score_change} 分")
        print(f"原因：{record.reason}")
        print(f"类别：{record.category}")
        print(f"之前：{record.before_points} 分")
        print(f"现在：{record.after_points} 分 ({self.get_emoji(self.state.grade)} {self.state.grade}级)")
    
    def check_status(self):
        """检查状态"""
        if self.state.current_points < Config.PASSING_LINE:
            print(f"\n❌ **警戒状态**")
            print(f"当前分数 {self.state.current_points} 分，低于及格线 {Config.PASSING_LINE} 分！")
            print(f"需要立即整改！")
        elif self.state.current_points >= Config.EXCELLENT_LINE:
            print(f"\n✅ **优秀状态**")
            print(f"当前分数 {self.state.current_points} 分，达到优秀线！")
            print(f"继续保持！")
    
    def get_status(self) -> Dict:
        """获取状态"""
        return {
            "current_points": self.state.current_points,
            "grade": self.state.grade,
            "grade_emoji": self.get_emoji(self.state.grade),
            "today_change": self.state.today_change,
            "week_change": self.state.week_change,
            "passing_line": Config.PASSING_LINE,
            "excellent_line": Config.EXCELLENT_LINE,
            "status": "danger" if self.state.current_points < Config.PASSING_LINE else 
                     "excellent" if self.state.current_points >= Config.EXCELLENT_LINE else "normal",
            "last_updated": self.state.last_updated
        }
    
    def show_status(self):
        """显示状态"""
        status = self.get_status()
        
        print("\n" + "="*50)
        print(f"📊 **积分管理系统**")
        print("="*50)
        print(f"当前分数：{status['current_points']} 分")
        print(f"等    级：{status['grade_emoji']} {status['grade']}级")
        print(f"今日变化：{status['today_change']:+d} 分")
        print(f"本周变化：{status['week_change']:+d} 分")
        print(f"状    态：{status['status']}")
        print(f"及格线：{Config.PASSING_LINE} 分")
        print(f"优秀线：{Config.EXCELLENT_LINE} 分")
        print(f"最后更新：{status['last_updated']}")
        print("="*50)
        
        if status['status'] == 'danger':
            print(f"\n❌ **警告**: 分数低于及格线，需要立即整改！")
        elif status['status'] == 'excellent':
            print(f"\n✅ **优秀**: 表现很好，继续保持！")
    
    def get_history(self, limit: int = 10) -> List[Dict]:
        """获取历史记录"""
        return self.state.history[-limit:]
    
    def show_history(self, limit: int = 10):
        """显示历史记录"""
        history = self.get_history(limit)
        
        print(f"\n📜 **最近 {limit} 条记录**")
        print("-"*50)
        for record in reversed(history):
            sign = "+" if record['score_change'] > 0 else ""
            print(f"{record['timestamp'][:16]} | {sign}{record['score_change']:3d} | {record['action'][:20]}")
    
    def generate_report(self) -> str:
        """生成报告"""
        status = self.get_status()
        
        report = f"\n📊 **积分管理报告**\n\n"
        report += f"当前分数：{status['current_points']} 分 ({status['grade_emoji']} {status['grade']}级)\n"
        report += f"今日变化：{status['today_change']:+d} 分\n"
        report += f"本周变化：{status['week_change']:+d} 分\n"
        report += f"状态：{status['status']}\n\n"
        
        if status['status'] == 'danger':
            report += f"⚠️ **警告**: 需要立即整改！\n"
            report += f"建议:\n"
            report += f"1. 停止新任务，全面审查\n"
            report += f"2. 完成基础任务\n"
            report += f"3. 加强监督，每日多次报告\n"
        elif status['status'] == 'excellent':
            report += f"✅ **优秀**: 表现很好！\n"
            report += f"建议:\n"
            report += f"1. 继续保持\n"
            report += f"2. 挑战更难任务\n"
            report += f"3. 可以适当奖励自己\n"
        else:
            report += f"👍 **良好**: 正常状态\n"
            report += f"建议:\n"
            report += f"1. 持续学习\n"
            report += f"2. 提高质量\n"
            report += f"3. 争取达到优秀\n"
        
        return report


# ============================================================================
# CLI
# ============================================================================

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="积分管理系统")
    parser.add_argument("--status", action="store_true", help="显示状态")
    parser.add_argument("--add", type=str, help="添加积分 (格式：action|reason|category)")
    parser.add_argument("--deduct", type=str, help="扣除积分 (格式：action|reason|category)")
    parser.add_argument("--history", action="store_true", help="显示历史记录")
    parser.add_argument("--report", action="store_true", help="生成报告")
    parser.add_argument("--init", action="store_true", help="初始化状态")
    
    args = parser.parse_args()
    
    manager = PointsManager()
    
    if args.status:
        manager.show_status()
    
    elif args.add:
        parts = args.add.split("|")
        if len(parts) >= 2:
            action = parts[0]
            reason = parts[1]
            category = parts[2] if len(parts) > 2 else "其他"
            manager.add_points(action, reason, category)
        else:
            print("❌ 格式错误，请使用：action|reason|category")
    
    elif args.deduct:
        parts = args.deduct.split("|")
        if len(parts) >= 2:
            action = parts[0]
            reason = parts[1]
            category = parts[2] if len(parts) > 2 else "其他"
            # 扣除积分为负值
            points = Config.POINTS_RULES.get(action, 0)
            if points > 0:
                points = -points
            manager.record_change(action, points, reason, category)
        else:
            print("❌ 格式错误，请使用：action|reason|category")
    
    elif args.history:
        manager.show_history(20)
    
    elif args.report:
        report = manager.generate_report()
        print(report)
    
    elif args.init:
        print("⚠️ 确定要初始化状态吗？(当前分数将重置为 80 分)")
        confirm = input("确认 (y/n): ")
        if confirm.lower() == 'y':
            manager.state = PointsState(
                current_points=Config.STARTING_POINTS,
                grade=GradeLevel.B.value,
                history=[],
                today_change=0,
                week_change=0,
                last_updated=datetime.now().isoformat()
            )
            manager.save_state()
            print("✅ 初始化完成")
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
