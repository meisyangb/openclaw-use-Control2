#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Skill 学习助手 v1.0

功能:
- 根据学习任务选择最合适的 skill 组合
- 自动下载缺失的 skills
- 管理 skill 的使用和配置
"""

import json
import os
import subprocess
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Optional


# ============================================================================
# 配置
# ============================================================================

class Config:
    """配置常量"""
    
    # 路径
    WORKSPACE = Path.home() / ".openclaw" / "workspace"
    OPENCLAW_MAIN = Path.home() / "oepnclaw" / "openclaw-main" / "skills"
    WORKSPACE_SKILLS = WORKSPACE / "skills"
    DEPLOYMENT_SKILLS = WORKSPACE / "openclaw-deployment" / "skills"
    
    # Skill 注册表
    SKILL_REGISTRY = WORKSPACE / "memory" / "skill-registry.json"
    SKILL_USAGE_LOG = WORKSPACE / "memory" / "skill-usage.log"
    
    # 学习相关 skills
    LEARNING_SKILLS = {
        "research": ["web_search", "web_fetch", "browser-automation"],
        "coding": ["coding-agent", "ai-model-manager"],
        "memory": ["adaptive-agent", "model-health-monitor"],
        "documentation": ["basic-system", "skill-creator"],
        "github": ["github", "gh-issues"],
        "communication": ["discord", "message"],
    }
    
    # Skill 元数据
    SKILL_METADATA = {
        "adaptive-agent": {
            "description": "自学习和自适应 AI 代理",
            "use_cases": ["学习模式识别", "用户偏好学习", "性能优化"],
            "priority": "high"
        },
        "browser-automation": {
            "description": "浏览器自动化和网页交互",
            "use_cases": ["网页抓取", "表单填写", "自动化导航"],
            "priority": "high"
        },
        "coding-agent": {
            "description": "编码助手",
            "use_cases": ["代码生成", "代码审查", "重构"],
            "priority": "high"
        },
        "skill-creator": {
            "description": "创建或更新 AgentSkills",
            "use_cases": ["设计技能", "打包技能", "文档编写"],
            "priority": "medium"
        },
        "github": {
            "description": "GitHub 集成",
            "use_cases": ["仓库管理", "PR 处理", "Issue 跟踪"],
            "priority": "high"
        },
        "model-health-monitor": {
            "description": "模型健康监控",
            "use_cases": ["错误检测", "自动切换", "状态监控"],
            "priority": "critical"
        },
    }


# ============================================================================
# 数据类型
# ============================================================================

@dataclass
class SkillInfo:
    """Skill 信息"""
    name: str
    location: str
    description: str
    use_cases: List[str]
    priority: str
    installed: bool = False
    last_used: Optional[str] = None
    usage_count: int = 0
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class LearningTask:
    """学习任务"""
    id: str
    topic: str
    required_skills: List[str]
    optional_skills: List[str]
    status: str  # pending, in_progress, completed
    created_at: str
    completed_at: Optional[str] = None
    notes: str = ""
    
    def to_dict(self) -> Dict:
        return asdict(self)


# ============================================================================
# Skill 管理器
# ============================================================================

class SkillManager:
    """Skill 管理器"""
    
    def __init__(self):
        self.registry: Dict[str, SkillInfo] = {}
        self.load_registry()
    
    def load_registry(self):
        """加载注册表"""
        if Config.SKILL_REGISTRY.exists():
            try:
                with open(Config.SKILL_REGISTRY, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.registry = {
                        k: SkillInfo(**v) for k, v in data.get("skills", {}).items()
                    }
            except Exception as e:
                print(f"⚠️ 加载注册表失败：{e}")
        
        # 扫描已安装的 skills
        self.scan_installed_skills()
    
    def save_registry(self):
        """保存注册表"""
        Config.SKILL_REGISTRY.parent.mkdir(parents=True, exist_ok=True)
        with open(Config.SKILL_REGISTRY, "w", encoding="utf-8") as f:
            json.dump({
                "skills": {k: v.to_dict() for k, v in self.registry.items()},
                "updated_at": datetime.now().isoformat()
            }, f, ensure_ascii=False, indent=2)
    
    def scan_installed_skills(self):
        """扫描已安装的 skills"""
        locations = [
            Config.OPENCLAW_MAIN,
            Config.WORKSPACE_SKILLS,
            Config.DEPLOYMENT_SKILLS
        ]
        
        for location in locations:
            if location.exists():
                for skill_dir in location.iterdir():
                    if skill_dir.is_dir() and (skill_dir / "SKILL.md").exists():
                        skill_name = skill_dir.name
                        if skill_name not in self.registry:
                            self.registry[skill_name] = SkillInfo(
                                name=skill_name,
                                location=str(skill_dir),
                                description="Auto-detected skill",
                                use_cases=[],
                                priority="medium",
                                installed=True
                            )
                        else:
                            self.registry[skill_name].installed = True
                            self.registry[skill_name].location = str(skill_dir)
        
        self.save_registry()
    
    def recommend_skills(self, task_type: str) -> List[str]:
        """根据任务类型推荐 skills"""
        recommended = []
        
        # 从预定义映射获取
        if task_type in Config.LEARNING_SKILLS:
            recommended.extend(Config.LEARNING_SKILLS[task_type])
        
        # 根据元数据添加高优先级 skills
        for name, meta in Config.SKILL_METADATA.items():
            if meta.get("priority") in ["high", "critical"]:
                if name not in recommended:
                    recommended.append(name)
        
        return recommended
    
    def get_skill_combination(self, learning_goal: str) -> Dict:
        """根据学习目标获取 skill 组合"""
        goal_lower = learning_goal.lower()
        
        # 分析学习目标
        required = []
        optional = []
        
        if any(word in goal_lower for word in ["github", "开源", "项目"]):
            required.extend(["github", "gh-issues", "web_fetch"])
        
        if any(word in goal_lower for word in ["学习", "研究", "分析"]):
            required.extend(["web_search", "web_fetch", "adaptive-agent"])
        
        if any(word in goal_lower for word in ["代码", "编程", "开发"]):
            required.extend(["coding-agent", "ai-model-manager"])
        
        if any(word in goal_lower for word in ["架构", "设计", "模式"]):
            required.extend(["skill-creator", "adaptive-agent"])
        
        if any(word in goal_lower for word in ["文档", "记录", "总结"]):
            required.extend(["basic-system", "skill-creator"])
        
        # 添加总是有用的 skills
        optional.extend(["browser-automation", "model-health-monitor"])
        
        # 去重
        required = list(dict.fromkeys(required))
        optional = list(dict.fromkeys(optional))
        
        # 移除 required 中已在 optional 的
        optional = [s for s in optional if s not in required]
        
        return {
            "learning_goal": learning_goal,
            "required_skills": required,
            "optional_skills": optional,
            "total_skills": len(required) + len(optional)
        }
    
    def check_availability(self, skill_names: List[str]) -> Dict[str, bool]:
        """检查 skills 是否可用"""
        availability = {}
        for name in skill_names:
            availability[name] = name in self.registry and self.registry[name].installed
        return availability
    
    def log_usage(self, skill_name: str, context: str):
        """记录 skill 使用"""
        # 更新注册表
        if skill_name in self.registry:
            self.registry[skill_name].usage_count += 1
            self.registry[skill_name].last_used = datetime.now().isoformat()
            self.save_registry()
        
        # 记录日志
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "skill": skill_name,
            "context": context
        }
        
        with open(Config.SKILL_USAGE_LOG, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
    
    def get_status(self) -> Dict:
        """获取状态"""
        installed = [s for s in self.registry.values() if s.installed]
        missing = [s for s in self.registry.values() if not s.installed]
        
        return {
            "version": "1.0.0",
            "timestamp": datetime.now().isoformat(),
            "total_skills": len(self.registry),
            "installed": len(installed),
            "missing": len(missing),
            "most_used": sorted(
                [s.to_dict() for s in installed],
                key=lambda x: x["usage_count"],
                reverse=True
            )[:5],
            "critical_skills": [
                name for name, meta in Config.SKILL_METADATA.items()
                if meta.get("priority") == "critical"
            ]
        }


# ============================================================================
# Skill 下载器
# ============================================================================

class SkillDownloader:
    """Skill 下载器"""
    
    def __init__(self, skill_manager: SkillManager):
        self.skill_manager = skill_manager
    
    def download_from_github(self, skill_name: str, repo_url: str = None) -> bool:
        """从 GitHub 下载 skill"""
        if repo_url is None:
            # 默认从 OpenClaw 官方仓库下载
            repo_url = "https://github.com/openclaw/openclaw.git"
        
        target_dir = Config.WORKSPACE_SKILLS / skill_name
        
        print(f"📥 下载 skill: {skill_name}")
        print(f"   目标：{target_dir}")
        
        try:
            # 使用 git sparse-checkout 或 clone
            if target_dir.exists():
                print(f"⚠️ Skill 已存在：{target_dir}")
                return True
            
            # 尝试从 openclaw-main 复制
            source = Config.OPENCLAW_MAIN / skill_name
            if source.exists():
                self.copy_skill(source, target_dir)
                print(f"✅ 已从 {source} 复制")
                return True
            
            # 尝试从 deployment 复制
            source = Config.DEPLOYMENT_SKILLS / skill_name
            if source.exists():
                self.copy_skill(source, target_dir)
                print(f"✅ 已从 {source} 复制")
                return True
            
            print(f"❌ 无法找到 skill: {skill_name}")
            print(f"   请用户帮助从 GitHub 下载")
            return False
            
        except Exception as e:
            print(f"❌ 下载失败：{e}")
            return False
    
    def copy_skill(self, source: Path, target: Path):
        """复制 skill 目录"""
        import shutil
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(source, target, dirs_exist_ok=True)
    
    def download_missing_skills(self, skill_names: List[str]) -> List[str]:
        """下载缺失的 skills"""
        availability = self.skill_manager.check_availability(skill_names)
        missing = [name for name, available in availability.items() if not available]
        downloaded = []
        
        if not missing:
            print("✅ 所有 skills 都已安装")
            return downloaded
        
        print(f"📋 需要下载 {len(missing)} 个 skills: {missing}")
        
        for skill_name in missing:
            success = self.download_from_github(skill_name)
            if success:
                downloaded.append(skill_name)
        
        # 重新扫描
        self.skill_manager.scan_installed_skills()
        
        return downloaded


# ============================================================================
# 学习助手
# ============================================================================

class LearningAssistant:
    """学习助手"""
    
    def __init__(self):
        self.skill_manager = SkillManager()
        self.downloader = SkillDownloader(self.skill_manager)
        self.tasks: List[LearningTask] = []
    
    def plan_learning(self, topic: str, goal: str) -> LearningTask:
        """规划学习"""
        # 获取推荐的 skill 组合
        combination = self.skill_manager.get_skill_combination(goal)
        
        # 检查可用性
        all_skills = combination["required_skills"] + combination["optional_skills"]
        availability = self.skill_manager.check_availability(all_skills)
        
        # 识别缺失的 skills
        missing = [s for s, available in availability.items() if not available]
        
        task = LearningTask(
            id=f"task_{datetime.now().timestamp()}",
            topic=topic,
            required_skills=combination["required_skills"],
            optional_skills=combination["optional_skills"],
            status="pending",
            created_at=datetime.now().isoformat(),
            notes=f"缺失 skills: {missing}" if missing else ""
        )
        
        self.tasks.append(task)
        
        return task
    
    def prepare_for_learning(self, task: LearningTask) -> Dict:
        """为学习做准备"""
        print(f"🎯 准备学习：{task.topic}")
        
        all_skills = task.required_skills + task.optional_skills
        
        # 检查可用性
        availability = self.skill_manager.check_availability(all_skills)
        missing = [s for s, available in availability.items() if not available]
        
        result = {
            "task": task.to_dict(),
            "available_skills": [s for s, available in availability.items() if available],
            "missing_skills": missing,
            "action_required": []
        }
        
        if missing:
            print(f"⚠️ 缺失 {len(missing)} 个 skills: {missing}")
            print("\n💡 建议操作:")
            print(f"   1. 尝试自动下载：skill_helper download {', '.join(missing)}")
            print(f"   2. 如果失败，请用户帮助从 GitHub 下载")
            result["action_required"] = ["download_missing_skills"]
        else:
            print("✅ 所有需要的 skills 都已就绪")
            result["action_required"] = ["start_learning"]
        
        return result
    
    def get_status(self) -> Dict:
        """获取状态"""
        return {
            "version": "1.0.0",
            "timestamp": datetime.now().isoformat(),
            "skill_manager": self.skill_manager.get_status(),
            "active_tasks": len([t for t in self.tasks if t.status == "in_progress"]),
            "completed_tasks": len([t for t in self.tasks if t.status == "completed"])
        }


# ============================================================================
# CLI
# ============================================================================

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Skill 学习助手")
    parser.add_argument("--status", action="store_true", help="显示状态")
    parser.add_argument("--plan", type=str, help="规划学习 (格式：topic|goal)")
    parser.add_argument("--recommend", type=str, help="推荐 skills (任务类型)")
    parser.add_argument("--download", type=str, help="下载 skills (逗号分隔)")
    parser.add_argument("--scan", action="store_true", help="扫描已安装的 skills")
    
    args = parser.parse_args()
    
    assistant = LearningAssistant()
    
    if args.status:
        status = assistant.get_status()
        print(json.dumps(status, ensure_ascii=False, indent=2))
    
    elif args.plan:
        parts = args.plan.split("|")
        if len(parts) >= 2:
            topic, goal = parts[0], parts[1]
            task = assistant.plan_learning(topic, goal)
            print(f"📋 学习规划:")
            print(f"   主题：{task.topic}")
            print(f"   必需 skills: {task.required_skills}")
            print(f"   可选 skills: {task.optional_skills}")
            
            # 准备
            result = assistant.prepare_for_learning(task)
            print(f"\n📊 准备状态:")
            print(f"   可用：{len(result['available_skills'])} 个")
            print(f"   缺失：{len(result['missing_skills'])} 个")
        else:
            print("❌ 格式错误，请使用：topic|goal")
    
    elif args.recommend:
        skills = assistant.skill_manager.recommend_skills(args.recommend)
        print(f"📚 推荐 skills for '{args.recommend}':")
        for skill in skills:
            meta = Config.SKILL_METADATA.get(skill, {})
            print(f"   - {skill}: {meta.get('description', 'N/A')}")
    
    elif args.download:
        skills = [s.strip() for s in args.download.split(",")]
        downloaded = assistant.downloader.download_missing_skills(skills)
        print(f"\n✅ 已下载：{downloaded}")
    
    elif args.scan:
        assistant.skill_manager.scan_installed_skills()
        print("✅ Skill 扫描完成")
        status = assistant.skill_manager.get_status()
        print(f"   总计：{status['total_skills']} 个")
        print(f"   已安装：{status['installed']} 个")
        print(f"   缺失：{status['missing']} 个")
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
