#!/usr/bin/env python3
"""监控系统简单实现"""

from typing import Dict

class MonitorSystem:
    """监控系统"""
    
    def __init__(self):
        self.health_status = "healthy"
        self.error_count = 0
    
    def check_health(self) -> Dict:
        return {
            "status": self.health_status,
            "error_count": self.error_count
        }
    
    def get_status(self) -> Dict:
        return self.check_health()
