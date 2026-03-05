#!/usr/bin/env python3
"""学习系统简单实现"""

from typing import Dict

class LearningSystem:
    """学习系统"""
    
    def __init__(self):
        self.learnings = []
        self.preferences = {}
    
    def learn_from_interaction(self, interaction_type: str, success: bool, context: Dict = None):
        self.learnings.append({
            "type": interaction_type,
            "success": success,
            "context": context or {}
        })
    
    def learn_preference(self, key: str, value: str, confidence: float = 0.5):
        self.preferences[key] = {"value": value, "confidence": confidence}
    
    def get_status(self) -> Dict:
        return {
            "total_learnings": len(self.learnings),
            "preferences_count": len(self.preferences)
        }
