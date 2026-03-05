#!/usr/bin/env python3
"""评估系统简单实现"""

from typing import Dict

class EvaluationSystem:
    """评估系统"""
    
    def __init__(self):
        self.evaluations = []
    
    def evaluate_tool(self, tool_name: str, time_spent: int, time_saved: int, satisfaction: float) -> Dict:
        roi = time_saved / time_spent if time_spent > 0 else 0
        evaluation = {
            "tool": tool_name,
            "roi": roi,
            "satisfaction": satisfaction,
            "recommendation": "KEEP" if roi >= 1.0 else "IMPROVE"
        }
        self.evaluations.append(evaluation)
        return evaluation
    
    def get_status(self) -> Dict:
        return {
            "total_evaluations": len(self.evaluations)
        }
