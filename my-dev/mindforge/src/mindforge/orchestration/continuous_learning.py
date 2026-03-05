#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
持续学习与迭代系统 v1.0

功能:
- 自动学习外部 AI 模型
- 产品迭代改进
- 自我进化
- 知识整合
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


class ContinuousLearning:
    """持续学习系统"""
    
    def __init__(self, storage_dir: Optional[Path] = None):
        if storage_dir is None:
            storage_dir = Path.home() / ".openclaw" / "workspace" / "memory"
        
        self.storage_dir = storage_dir
        self.learning_log = storage_dir / "continuous-learning.jsonl"
        self.knowledge_base = storage_dir / "knowledge-base.json"
        self.iteration_history = storage_dir / "iteration-history.json"
        
        self.knowledge = self.load_knowledge()
        self.iterations = self.load_iterations()
    
    def load_knowledge(self) -> Dict:
        """加载知识库"""
        if self.knowledge_base.exists():
            with open(self.knowledge_base, "r", encoding="utf-8") as f:
                return json.load(f)
        return {"models": [], "technologies": [], "patterns": []}
    
    def save_knowledge(self):
        """保存知识库"""
        self.knowledge_base.parent.mkdir(parents=True, exist_ok=True)
        with open(self.knowledge_base, "w", encoding="utf-8") as f:
            json.dump(self.knowledge, f, ensure_ascii=False, indent=2)
    
    def load_iterations(self) -> List:
        """加载迭代历史"""
        if self.iteration_history.exists():
            with open(self.iteration_history, "r", encoding="utf-8") as f:
                return json.load(f)
        return []
    
    def save_iterations(self):
        """保存迭代历史"""
        self.iteration_history.parent.mkdir(parents=True, exist_ok=True)
        with open(self.iteration_history, "w", encoding="utf-8") as f:
            json.dump(self.iterations, f, ensure_ascii=False, indent=2)
    
    def log_learning(self, source: str, content: str, category: str):
        """记录学习"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "source": source,
            "content": content,
            "category": category
        }
        
        with open(self.learning_log, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        
        print(f"📚 学习记录：{source} - {category}")
    
    def learn_from_github(self, project_name: str, insights: List[str]):
        """从 GitHub 学习"""
        self.knowledge["models"].append({
            "name": project_name,
            "learned_at": datetime.now().isoformat(),
            "insights": insights
        })
        self.save_knowledge()
        
        self.log_learning(
            source=f"GitHub/{project_name}",
            content=", ".join(insights),
            category="ai_model"
        )
    
    def learn_new_technology(self, tech_name: str, description: str):
        """学习新技术"""
        self.knowledge["technologies"].append({
            "name": tech_name,
            "description": description,
            "learned_at": datetime.now().isoformat()
        })
        self.save_knowledge()
        
        self.log_learning(
            source="technology",
            content=f"{tech_name}: {description}",
            category="technology"
        )
    
    def learn_pattern(self, pattern_name: str, description: str, application: str):
        """学习设计模式"""
        self.knowledge["patterns"].append({
            "name": pattern_name,
            "description": description,
            "application": application,
            "learned_at": datetime.now().isoformat()
        })
        self.save_knowledge()
        
        self.log_learning(
            source="pattern",
            content=f"{pattern_name} - {application}",
            category="design_pattern"
        )
    
    def iterate_product(self, product_name: str, changes: List[str], improvements: List[str]):
        """产品迭代"""
        iteration = {
            "timestamp": datetime.now().isoformat(),
            "product": product_name,
            "changes": changes,
            "improvements": improvements,
            "version": f"v{len(self.iterations) + 1}.0"
        }
        
        self.iterations.append(iteration)
        self.save_iterations()
        
        print(f"\n🔄 产品迭代：{product_name}")
        print(f"   版本：{iteration['version']}")
        print(f"   变更：{len(changes)} 项")
        print(f"   改进：{len(improvements)} 项")
    
    def self_improvement(self, area: str, before: str, after: str, lessons: List[str]):
        """自我改进"""
        improvement = {
            "timestamp": datetime.now().isoformat(),
            "area": area,
            "before": before,
            "after": after,
            "lessons": lessons
        }
        
        self.log_learning(
            source="self_improvement",
            content=f"{area}: {before} → {after}",
            category="self_evolution"
        )
        
        print(f"\n🌱 自我改进：{area}")
        print(f"   改进前：{before}")
        print(f"   改进后：{after}")
        print(f"   经验：{len(lessons)} 条")
    
    def get_knowledge_summary(self) -> Dict:
        """获取知识摘要"""
        return {
            "models_count": len(self.knowledge.get("models", [])),
            "technologies_count": len(self.knowledge.get("technologies", [])),
            "patterns_count": len(self.knowledge.get("patterns", [])),
            "total_iterations": len(self.iterations)
        }
    
    def get_recent_learning(self, limit: int = 10) -> List:
        """获取最近学习"""
        if not self.learning_log.exists():
            return []
        
        learnings = []
        with open(self.learning_log, "r", encoding="utf-8") as f:
            for line in f:
                learnings.append(json.loads(line))
        
        return learnings[-limit:]
    
    def generate_learning_report(self) -> str:
        """生成学习报告"""
        summary = self.get_knowledge_summary()
        recent = self.get_recent_learning(5)
        
        report = f"\n📚 **持续学习报告**\n\n"
        report += f"**知识库统计**:\n"
        report += f"- AI 模型：{summary['models_count']} 个\n"
        report += f"- 技术：{summary['technologies_count']} 个\n"
        report += f"- 模式：{summary['patterns_count']} 个\n"
        report += f"- 产品迭代：{summary['total_iterations']} 次\n\n"
        
        if recent:
            report += f"**最近学习**:\n"
            for entry in reversed(recent):
                report += f"- {entry['timestamp'][:10]}: {entry['content'][:50]}...\n"
        
        return report


# 快速测试
if __name__ == "__main__":
    learning = ContinuousLearning()
    
    # 测试学习
    learning.learn_from_github("LangChain", ["模块化架构", "标准化接口"])
    learning.learn_new_technology("FastAPI", "现代 Python Web 框架")
    learning.learn_pattern("状态机", "清晰的状态流转", "任务编排")
    
    # 测试迭代
    learning.iterate_product(
        "MindForge",
        ["添加定时任务", "改进记忆系统"],
        ["性能提升 30%", "代码质量提高"]
    )
    
    # 测试自我改进
    learning.self_improvement(
        "代码能力",
        "基础 Python",
        "掌握设计模式",
        ["模块化重要", "测试必要"]
    )
    
    # 生成报告
    report = learning.generate_learning_report()
    print(report)
