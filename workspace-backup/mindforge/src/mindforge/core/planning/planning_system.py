#!/usr/bin/env python3
"""规划系统简单实现"""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Dict

@dataclass
class Goal:
    id: str
    title: str
    priority: str
    status: str = "active"

class PlanningSystem:
    """规划系统"""
    
    def __init__(self):
        self.goals: List[Goal] = []
    
    def create_goal(self, title: str, priority: str = "medium") -> Goal:
        goal = Goal(
            id=f"goal_{datetime.now().timestamp()}",
            title=title,
            priority=priority
        )
        self.goals.append(goal)
        return goal
    
    def get_status(self) -> Dict:
        return {
            "total_goals": len(self.goals),
            "active_goals": len([g for g in self.goals if g.status == "active"])
        }
