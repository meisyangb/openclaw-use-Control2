#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
外部探索追踪器 v1.0

功能:
- 记录探索活动
- 生成报告
- 安全监控
- 用户通知
"""

import json
import os
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Optional
from enum import Enum


# ============================================================================
# 配置
# ============================================================================

class Config:
    """配置常量"""
    
    # 路径
    WORKSPACE = Path.home() / ".openclaw" / "workspace"
    MEMORY_DIR = WORKSPACE / "memory"
    
    # 追踪文件
    EXPLORATION_LOG = MEMORY_DIR / "exploration-log.jsonl"
    EXPLORATION_REPORTS = MEMORY_DIR / "exploration-reports"
    SAFETY_ALERTS = MEMORY_DIR / "safety-alerts.jsonl"
    
    # 安全级别
    SAFE = "safe"
    CAUTION = "caution"
    DANGEROUS = "dangerous"


# ============================================================================
# 数据类型
# ============================================================================

class ActivityType(str, Enum):
    """活动类型"""
    BROWSING = "browsing"         # 浏览
    READING = "reading"           # 阅读
    REGISTERING = "registering"   # 注册
    DISCUSSING = "discussing"     # 讨论
    SHARING = "sharing"           # 分享
    CONTRIBUTING = "contributing" # 贡献


class RiskLevel(str, Enum):
    """风险级别"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class ExplorationActivity:
    """探索活动"""
    id: str
    timestamp: str
    activity_type: str
    website: str
    purpose: str
    duration_minutes: int
    risk_level: str
    what_i_did: str
    what_i_learned: str
    safety_concerns: List[str]
    follow_up_needed: bool
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class SafetyAlert:
    """安全警告"""
    id: str
    timestamp: str
    source: str
    threat_type: str
    description: str
    action_taken: str
    reported_to_user: bool
    
    def to_dict(self) -> Dict:
        return asdict(self)


# ============================================================================
# 追踪器
# ============================================================================

class ExplorationTracker:
    """探索追踪器"""
    
    def __init__(self):
        self.activities: List[ExplorationActivity] = []
        self.alerts: List[SafetyAlert] = []
        self.load()
    
    def load(self):
        """加载记录"""
        if Config.EXPLORATION_LOG.exists():
            try:
                with open(Config.EXPLORATION_LOG, "r", encoding="utf-8") as f:
                    for line in f:
                        data = json.loads(line)
                        self.activities.append(ExplorationActivity(**data))
            except Exception as e:
                print(f"⚠️ 加载记录失败：{e}")
        
        if Config.SAFETY_ALERTS.exists():
            try:
                with open(Config.SAFETY_ALERTS, "r", encoding="utf-8") as f:
                    for line in f:
                        data = json.loads(line)
                        self.alerts.append(SafetyAlert(**data))
            except Exception as e:
                print(f"⚠️ 加载警告失败：{e}")
    
    def save(self):
        """保存记录"""
        Config.EXPLORATION_LOG.parent.mkdir(parents=True, exist_ok=True)
        with open(Config.EXPLORATION_LOG, "a", encoding="utf-8") as f:
            for activity in self.activities[-1:]:  # 只保存最新的
                f.write(json.dumps(activity.to_dict(), ensure_ascii=False) + "\n")
        
        Config.SAFETY_ALERTS.parent.mkdir(parents=True, exist_ok=True)
        with open(Config.SAFETY_ALERTS, "a", encoding="utf-8") as f:
            for alert in self.alerts[-1:]:  # 只保存最新的
                f.write(json.dumps(alert.to_dict(), ensure_ascii=False) + "\n")
    
    def start_activity(self, activity_type: str, website: str, purpose: str, 
                       risk_level: str = "low") -> str:
        """开始活动"""
        activity_id = f"activity_{datetime.now().timestamp()}"
        
        print(f"\n🌐 【探索报告 - 行动前】")
        print(f"时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}")
        print(f"计划：{activity_type}")
        print(f"目标：{website}")
        print(f"目的：{purpose}")
        print(f"风险：{risk_level}")
        print(f"状态：开始...")
        
        return activity_id
    
    def end_activity(self, activity_id: str, what_i_did: str, what_i_learned: str,
                     duration_minutes: int, safety_concerns: List[str] = None,
                     follow_up_needed: bool = False):
        """结束活动"""
        activity = ExplorationActivity(
            id=activity_id,
            timestamp=datetime.now().isoformat(),
            activity_type="browsing",
            website="pending",
            purpose="pending",
            duration_minutes=duration_minutes,
            risk_level="low",
            what_i_did=what_i_did,
            what_i_learned=what_i_learned,
            safety_concerns=safety_concerns or [],
            follow_up_needed=follow_up_needed
        )
        
        self.activities.append(activity)
        self.save()
        
        print(f"\n📋 【探索报告 - 行动后】")
        print(f"时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}")
        print(f"完成：{what_i_did}")
        print(f"收获：{what_i_learned}")
        if safety_concerns:
            print(f"风险：{safety_concerns}")
        print(f"状态：完成")
    
    def report_safety_alert(self, source: str, threat_type: str, 
                           description: str, action_taken: str):
        """报告安全警告"""
        alert = SafetyAlert(
            id=f"alert_{datetime.now().timestamp()}",
            timestamp=datetime.now().isoformat(),
            source=source,
            threat_type=threat_type,
            description=description,
            action_taken=action_taken,
            reported_to_user=True
        )
        
        self.alerts.append(alert)
        self.save()
        
        print(f"\n⚠️ 【安全警告】")
        print(f"时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}")
        print(f"来源：{source}")
        print(f"威胁：{threat_type}")
        print(f"描述：{description}")
        print(f"行动：{action_taken}")
        print(f"状态：已报告用户")
    
    def get_status(self) -> Dict:
        """获取状态"""
        return {
            "version": "1.0.0",
            "timestamp": datetime.now().isoformat(),
            "total_activities": len(self.activities),
            "total_alerts": len(self.alerts),
            "recent_activities": [a.to_dict() for a in self.activities[-5:]],
            "recent_alerts": [a.to_dict() for a in self.alerts[-5:]],
            "safety_status": "safe" if len(self.alerts) == 0 else "alerts_present"
        }
    
    def generate_daily_report(self) -> str:
        """生成日报"""
        today = datetime.now().date()
        today_activities = [
            a for a in self.activities
            if datetime.fromisoformat(a.timestamp).date() == today
        ]
        
        report = f"\n📊 【探索日报】{today}\n\n"
        report += f"总活动：{len(today_activities)}\n"
        report += f"安全警告：{len([a for a in self.alerts if datetime.fromisoformat(a.timestamp).date() == today])}\n\n"
        
        if today_activities:
            report += "活动详情:\n"
            for i, activity in enumerate(today_activities, 1):
                report += f"\n{i}. {activity.what_i_did}\n"
                report += f"   收获：{activity.what_i_learned}\n"
                if activity.safety_concerns:
                    report += f"   风险：{activity.safety_concerns}\n"
        else:
            report += "今天没有探索活动。\n"
        
        return report


# ============================================================================
# CLI
# ============================================================================

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="外部探索追踪器")
    parser.add_argument("--status", action="store_true", help="显示状态")
    parser.add_argument("--start", type=str, help="开始活动 (格式：type|website|purpose)")
    parser.add_argument("--end", type=str, help="结束活动 (格式：id|what_i_did|what_i_learned|duration)")
    parser.add_argument("--alert", type=str, help="报告安全问题 (格式：source|threat|description|action)")
    parser.add_argument("--report", action="store_true", help="生成日报")
    
    args = parser.parse_args()
    
    tracker = ExplorationTracker()
    
    if args.status:
        status = tracker.get_status()
        print(json.dumps(status, ensure_ascii=False, indent=2))
    
    elif args.start:
        parts = args.start.split("|")
        if len(parts) >= 3:
            activity_type, website, purpose = parts[0], parts[1], parts[2]
            risk_level = parts[3] if len(parts) > 3 else "low"
            tracker.start_activity(activity_type, website, purpose, risk_level)
        else:
            print("❌ 格式错误，请使用：type|website|purpose|risk_level")
    
    elif args.end:
        parts = args.end.split("|")
        if len(parts) >= 3:
            activity_id = parts[0]
            what_i_did = parts[1]
            what_i_learned = parts[2]
            duration = int(parts[3]) if len(parts) > 3 else 30
            tracker.end_activity(activity_id, what_i_did, what_i_learned, duration)
        else:
            print("❌ 格式错误，请使用：id|what_i_did|what_i_learned|duration")
    
    elif args.alert:
        parts = args.alert.split("|")
        if len(parts) >= 4:
            source, threat, description, action = parts[0], parts[1], parts[2], parts[3]
            tracker.report_safety_alert(source, threat, description, action)
        else:
            print("❌ 格式错误，请使用：source|threat|description|action")
    
    elif args.report:
        report = tracker.generate_daily_report()
        print(report)
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
