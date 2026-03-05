#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
工具评估系统 v1.0

核心原则:
- 没有经过实际测试的工具，效果是未知的
- 不能带来提升的工具应该被废弃
- 持续评估，优胜劣汰

功能:
- 工具使用效果评估
- ROI 计算 (投入产出比)
- 自动废弃建议
- 定期审查
"""

import json
import os
from datetime import datetime, timedelta
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
    
    # 评估文件
    TOOL_EVALUATION_FILE = MEMORY_DIR / "tool-evaluation.json"
    TOOL_USAGE_LOG = MEMORY_DIR / "tool-usage-detailed.log"
    
    # 评估指标
    MIN_USAGE_COUNT = 3          # 最少使用次数才能评估
    EVALUATION_PERIOD_DAYS = 7   # 评估周期 (天)
    
    # 阈值
    ROI_THRESHOLD = 1.0          # ROI 阈值 (低于此值建议废弃)
    EFFICIENCY_THRESHOLD = 0.5   # 效率阈值
    SATISFACTION_THRESHOLD = 0.6 # 满意度阈值
    
    # 评分权重
    WEIGHT_ROI = 0.4             # ROI 权重
    WEIGHT_EFFICIENCY = 0.3      # 效率权重
    WEIGHT_SATISFACTION = 0.3    # 满意度权重


# ============================================================================
# 数据类型
# ============================================================================

class EvaluationStatus(str, Enum):
    """评估状态"""
    NEW = "new"                  # 新工具，待测试
    TESTING = "testing"          # 测试中
    EVALUATED = "evaluated"      # 已评估
    DEPRECATED = "deprecated"    # 已废弃
    CRITICAL = "critical"        # 关键工具 (不废弃)


class Recommendation(str, Enum):
    """推荐操作"""
    KEEP = "keep"                # 保留
    IMPROVE = "improve"          # 改进
    REVIEW = "review"            # 审查
    DEPRECATE = "deprecate"      # 废弃


@dataclass
class ToolEvaluation:
    """工具评估"""
    tool_name: str
    status: str
    created_at: str
    last_used: Optional[str]
    usage_count: int
    total_time_spent: int        # 分钟
    time_saved: int              # 分钟 (估算)
    satisfaction: float          # 0-1
    notes: str
    last_evaluated: Optional[str]
    recommendation: str
    roi: float = 0.0
    efficiency: float = 0.0
    overall_score: float = 0.0
    
    def to_dict(self) -> Dict:
        return asdict(self)


# ============================================================================
# 评估器
# ============================================================================

class ToolEvaluator:
    """工具评估器"""
    
    def __init__(self):
        self.evaluations: Dict[str, ToolEvaluation] = {}
        self.load()
    
    def load(self):
        """加载评估"""
        if Config.TOOL_EVALUATION_FILE.exists():
            try:
                with open(Config.TOOL_EVALUATION_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.evaluations = {
                        k: ToolEvaluation(**v) for k, v in data.get("evaluations", {}).items()
                    }
            except Exception as e:
                print(f"⚠️ 加载评估失败：{e}")
    
    def save(self):
        """保存评估"""
        Config.TOOL_EVALUATION_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(Config.TOOL_EVALUATION_FILE, "w", encoding="utf-8") as f:
            json.dump({
                "evaluations": {k: v.to_dict() for k, v in self.evaluations.items()},
                "updated_at": datetime.now().isoformat()
            }, f, ensure_ascii=False, indent=2)
    
    def register_tool(self, tool_name: str, is_critical: bool = False):
        """注册新工具"""
        if tool_name not in self.evaluations:
            status = EvaluationStatus.CRITICAL.value if is_critical else EvaluationStatus.NEW.value
            self.evaluations[tool_name] = ToolEvaluation(
                tool_name=tool_name,
                status=status,
                created_at=datetime.now().isoformat(),
                last_used=None,
                usage_count=0,
                total_time_spent=0,
                time_saved=0,
                satisfaction=0.0,
                notes="",
                last_evaluated=None,
                recommendation=Recommendation.KEEP.value if is_critical else Recommendation.REVIEW.value,
                roi=0.0,
                efficiency=0.0,
                overall_score=0.0
            )
            self.save()
            print(f"✅ 已注册工具：{tool_name} (状态：{status})")
    
    def log_usage(self, tool_name: str, time_spent: int, time_saved: int = 0, 
                  satisfaction: float = None, notes: str = ""):
        """记录工具使用"""
        if tool_name not in self.evaluations:
            self.register_tool(tool_name)
        
        eval = self.evaluations[tool_name]
        eval.usage_count += 1
        eval.total_time_spent += time_spent
        eval.time_saved += time_saved
        eval.last_used = datetime.now().isoformat()
        
        # 更新满意度 (移动平均)
        if satisfaction is not None:
            if eval.usage_count == 1:
                eval.satisfaction = satisfaction
            else:
                eval.satisfaction = (eval.satisfaction * (eval.usage_count - 1) + satisfaction) / eval.usage_count
        
        # 更新状态
        if eval.usage_count >= Config.MIN_USAGE_COUNT:
            eval.status = EvaluationStatus.TESTING.value
        
        # 记录详细日志
        self._log_detailed(tool_name, time_spent, time_saved, satisfaction, notes)
        
        self.save()
        print(f"📝 已记录 {tool_name} 使用：耗时 {time_spent}min, 节省 {time_saved}min")
    
    def _log_detailed(self, tool_name: str, time_spent: int, time_saved: int, 
                      satisfaction: float, notes: str):
        """记录详细日志"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "tool": tool_name,
            "time_spent": time_spent,
            "time_saved": time_saved,
            "satisfaction": satisfaction,
            "notes": notes
        }
        
        with open(Config.TOOL_USAGE_LOG, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
    
    def calculate_metrics(self, tool_name: str) -> Dict:
        """计算指标"""
        if tool_name not in self.evaluations:
            return {}
        
        eval = self.evaluations[tool_name]
        
        # ROI = 时间节省 / 时间投入
        if eval.total_time_spent > 0:
            eval.roi = eval.time_saved / eval.total_time_spent
        else:
            eval.roi = 0.0
        
        # 效率 = 平均每次使用节省的时间
        if eval.usage_count > 0:
            avg_time_spent = eval.total_time_spent / eval.usage_count
            avg_time_saved = eval.time_saved / eval.usage_count
            eval.efficiency = avg_time_saved / avg_time_spent if avg_time_spent > 0 else 0.0
        else:
            eval.efficiency = 0.0
        
        # 综合评分
        eval.overall_score = (
            eval.roi * Config.WEIGHT_ROI +
            eval.efficiency * Config.WEIGHT_EFFICIENCY +
            eval.satisfaction * Config.WEIGHT_SATISFACTION
        )
        
        # 推荐操作
        eval.recommendation = self._get_recommendation(eval)
        
        return {
            "roi": eval.roi,
            "efficiency": eval.efficiency,
            "overall_score": eval.overall_score,
            "recommendation": eval.recommendation
        }
    
    def _get_recommendation(self, eval: ToolEvaluation) -> str:
        """获取推荐操作"""
        if eval.status == EvaluationStatus.CRITICAL.value:
            return Recommendation.KEEP.value
        
        if eval.usage_count < Config.MIN_USAGE_COUNT:
            return Recommendation.REVIEW.value
        
        if eval.overall_score >= 0.8:
            return Recommendation.KEEP.value
        elif eval.overall_score >= 0.5:
            return Recommendation.IMPROVE.value
        elif eval.overall_score >= 0.3:
            return Recommendation.REVIEW.value
        else:
            return Recommendation.DEPRECATE.value
    
    def evaluate_all(self) -> Dict:
        """评估所有工具"""
        results = {}
        
        for tool_name in self.evaluations:
            metrics = self.calculate_metrics(tool_name)
            results[tool_name] = {
                "status": self.evaluations[tool_name].status,
                "usage_count": self.evaluations[tool_name].usage_count,
                "overall_score": self.evaluations[tool_name].overall_score,
                "recommendation": self.evaluations[tool_name].recommendation
            }
        
        self.save()
        return results
    
    def get_deprecated_candidates(self) -> List[str]:
        """获取建议废弃的工具"""
        candidates = []
        
        for tool_name, eval in self.evaluations.items():
            if eval.status == EvaluationStatus.CRITICAL.value:
                continue
            
            if eval.recommendation == Recommendation.DEPRECATE.value:
                candidates.append(tool_name)
        
        return candidates
    
    def deprecate_tool(self, tool_name: str):
        """废弃工具"""
        if tool_name in self.evaluations:
            self.evaluations[tool_name].status = EvaluationStatus.DEPRECATED.value
            self.evaluations[tool_name].recommendation = Recommendation.DEPRECATE.value
            self.save()
            print(f"⚠️ 已废弃工具：{tool_name}")
    
    def get_status(self) -> Dict:
        """获取状态"""
        # 先评估所有
        self.evaluate_all()
        
        by_recommendation = {}
        for eval in self.evaluations.values():
            rec = eval.recommendation
            if rec not in by_recommendation:
                by_recommendation[rec] = []
            by_recommendation[rec].append(eval.tool_name)
        
        return {
            "version": "1.0.0",
            "timestamp": datetime.now().isoformat(),
            "total_tools": len(self.evaluations),
            "by_status": {
                "new": len([e for e in self.evaluations.values() if e.status == EvaluationStatus.NEW.value]),
                "testing": len([e for e in self.evaluations.values() if e.status == EvaluationStatus.TESTING.value]),
                "evaluated": len([e for e in self.evaluations.values() if e.status == EvaluationStatus.EVALUATED.value]),
                "deprecated": len([e for e in self.evaluations.values() if e.status == EvaluationStatus.DEPRECATED.value]),
                "critical": len([e for e in self.evaluations.values() if e.status == EvaluationStatus.CRITICAL.value])
            },
            "by_recommendation": by_recommendation,
            "deprecated_candidates": self.get_deprecated_candidates(),
            "top_tools": sorted(
                [{"name": e.tool_name, "score": e.overall_score} for e in self.evaluations.values()],
                key=lambda x: x["score"],
                reverse=True
            )[:5]
        }


# ============================================================================
# CLI
# ============================================================================

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="工具评估系统")
    parser.add_argument("--status", action="store_true", help="显示状态")
    parser.add_argument("--register", type=str, help="注册新工具")
    parser.add_argument("--log", type=str, help="记录使用 (格式：tool|time_spent|time_saved|satisfaction)")
    parser.add_argument("--evaluate", action="store_true", help="评估所有工具")
    parser.add_argument("--deprecate", type=str, help="废弃工具")
    parser.add_argument("--critical", action="store_true", help="标记为关键工具")
    
    args = parser.parse_args()
    
    evaluator = ToolEvaluator()
    
    if args.status:
        status = evaluator.get_status()
        print(json.dumps(status, ensure_ascii=False, indent=2))
    
    elif args.register:
        is_critical = args.critical
        evaluator.register_tool(args.register, is_critical)
    
    elif args.log:
        parts = args.log.split("|")
        if len(parts) >= 2:
            tool_name = parts[0]
            time_spent = int(parts[1])
            time_saved = int(parts[2]) if len(parts) > 2 else 0
            satisfaction = float(parts[3]) if len(parts) > 3 else 0.7
            evaluator.log_usage(tool_name, time_spent, time_saved, satisfaction)
        else:
            print("❌ 格式错误，请使用：tool|time_spent|time_saved|satisfaction")
    
    elif args.evaluate:
        results = evaluator.evaluate_all()
        print("📊 评估结果:")
        for tool, data in results.items():
            emoji = {"keep": "✅", "improve": "🔧", "review": "⚠️", "deprecate": "❌"}.get(
                data["recommendation"], "📝"
            )
            print(f"   {emoji} {tool}: {data['recommendation']} (score: {data['overall_score']:.2f})")
    
    elif args.deprecate:
        evaluator.deprecate_tool(args.deprecate)
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
