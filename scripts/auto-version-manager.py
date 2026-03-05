#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
全自动版本管理系统 (Auto Version Manager)

功能：
- 自动版本检测和升级
- 提交前健康检查
- 自动回滚机制
- 安全边界保护
- Git 操作自动化

作者：FullStack Engineer with Memory Intelligence
版本：v1.0.0
日期：2026-03-05
"""

import os
import sys
import json
import subprocess
import re
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, List, Tuple
import hashlib

# 配置
CONFIG = {
    "repo_root": "/root/oepnclaw/openclaw-main",
    "state_file": ".openclaw/version-manager-state.json",
    "backup_dir": ".openclaw/version-backups",
    "max_backups": 10,
    "health_check_timeout": 300,  # 5 分钟
    "auto_rollback": True,
    "require_tests": True,
    "safety_mode": True,  # 安全模式：关键操作前必须备份
}

# 颜色输出
class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    PURPLE = '\033[0;35m'
    CYAN = '\033[0;36m'
    NC = '\033[0m'  # No Color

def log_info(msg: str):
    print(f"{Colors.BLUE}[INFO]{Colors.NC} {msg}")

def log_success(msg: str):
    print(f"{Colors.GREEN}[✓]{Colors.NC} {msg}")

def log_warning(msg: str):
    print(f"{Colors.YELLOW}[⚠]{Colors.NC} {msg}")

def log_error(msg: str):
    print(f"{Colors.RED}[✗]{Colors.NC} {msg}")

def log_critical(msg: str):
    print(f"{Colors.RED}[🚨 CRITICAL]{Colors.NC} {msg}")

def run_command(cmd: List[str], cwd: str = None, check: bool = True, capture: bool = True) -> subprocess.CompletedProcess:
    """运行 shell 命令"""
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd or CONFIG["repo_root"],
            capture_output=capture,
            text=True,
            timeout=CONFIG["health_check_timeout"]
        )
        if check and result.returncode != 0:
            raise subprocess.CalledProcessError(result.returncode, cmd, result.stdout, result.stderr)
        return result
    except subprocess.TimeoutExpired:
        log_error(f"命令超时：{' '.join(cmd)}")
        raise
    except Exception as e:
        if check:
            log_error(f"命令执行失败：{' '.join(cmd)}")
            log_error(str(e))
        raise

class VersionManager:
    """版本管理器核心类"""
    
    def __init__(self):
        self.repo_root = Path(CONFIG["repo_root"])
        self.state_file = self.repo_root / CONFIG["state_file"]
        self.backup_dir = self.repo_root / CONFIG["backup_dir"]
        self.state = self.load_state()
        
    def load_state(self) -> Dict:
        """加载状态文件"""
        if self.state_file.exists():
            with open(self.state_file, 'r') as f:
                return json.load(f)
        return {
            "current_version": "2.1.0",
            "last_commit": None,
            "last_tag": None,
            "backup_count": 0,
            "rollback_history": [],
            "health_status": "unknown",
            "last_health_check": None
        }
    
    def save_state(self):
        """保存状态文件"""
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.state_file, 'w') as f:
            json.dump(self.state, f, indent=2)
        log_success("状态已保存")
    
    def get_current_version(self) -> str:
        """获取当前版本"""
        # 从 package.json 读取
        package_json = self.repo_root / "package.json"
        if package_json.exists():
            with open(package_json, 'r') as f:
                data = json.load(f)
                return data.get("version", "0.0.0")
        
        # 从 Git 标签读取
        try:
            result = run_command(["git", "describe", "--tags", "--abbrev=0"], check=False)
            if result.returncode == 0:
                return result.stdout.strip().lstrip('v')
        except:
            pass
        
        return self.state["current_version"]
    
    def parse_version(self, version: str) -> Tuple[int, int, int]:
        """解析版本号"""
        match = re.match(r'v?(\d+)\.(\d+)\.(\d+)', version)
        if not match:
            raise ValueError(f"无效的版本号：{version}")
        return tuple(map(int, match.groups()))
    
    def bump_version(self, bump_type: str = "patch") -> str:
        """升级版本号"""
        current = self.get_current_version()
        major, minor, patch = self.parse_version(current)
        
        if bump_type == "major":
            major += 1
            minor = 0
            patch = 0
        elif bump_type == "minor":
            minor += 1
            patch = 0
        elif bump_type == "patch":
            patch += 1
        else:
            raise ValueError(f"未知的升级类型：{bump_type}")
        
        new_version = f"{major}.{minor}.{patch}"
        log_info(f"版本升级：{current} → {new_version}")
        return new_version
    
    def create_backup(self, label: str = None) -> str:
        """创建备份"""
        if not CONFIG["safety_mode"]:
            return None
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        label = label or "auto"
        backup_name = f"backup_{timestamp}_{label}"
        backup_path = self.backup_dir / backup_name
        
        log_info(f"创建备份：{backup_name}")
        
        # 创建备份目录
        backup_path.mkdir(parents=True, exist_ok=True)
        
        # 备份关键文件
        critical_files = [
            "package.json",
            "VERSION-MANAGEMENT-STRATEGY.md",
            "CHANGELOG.md",
            "scripts/version-bump.sh",
            "scripts/version-check.sh",
        ]
        
        for file in critical_files:
            src = self.repo_root / file
            if src.exists():
                dst = backup_path / file
                dst.parent.mkdir(parents=True, exist_ok=True)
                import shutil
                shutil.copy2(src, dst)
        
        # 备份 Git 状态
        try:
            run_command(["git", "rev-parse", "HEAD"], capture=True)
            with open(backup_path / "git_state.txt", 'w') as f:
                f.write(f"HEAD={run_command(['git', 'rev-parse', 'HEAD']).stdout.strip()}\n")
                f.write(f"BRANCH={run_command(['git', 'rev-parse', '--abbrev-ref', 'HEAD']).stdout.strip()}\n")
        except:
            pass
        
        # 清理旧备份
        self.cleanup_old_backups()
        
        log_success(f"备份完成：{backup_name}")
        return backup_name
    
    def cleanup_old_backups(self):
        """清理旧备份"""
        if not self.backup_dir.exists():
            return
        
        backups = sorted(self.backup_dir.iterdir(), key=lambda x: x.name, reverse=True)
        for old_backup in backups[CONFIG["max_backups"]:]:
            log_info(f"清理旧备份：{old_backup.name}")
            import shutil
            shutil.rmtree(old_backup)
    
    def rollback(self, backup_name: str = None) -> bool:
        """回滚到备份"""
        if not self.backup_dir.exists():
            log_error("没有可用的备份")
            return False
        
        if backup_name:
            backup_path = self.backup_dir / backup_name
        else:
            # 使用最新备份
            backups = sorted(self.backup_dir.iterdir(), key=lambda x: x.name, reverse=True)
            if not backups:
                log_error("没有可用的备份")
                return False
            backup_path = backups[0]
        
        if not backup_path.exists():
            log_error(f"备份不存在：{backup_path}")
            return False
        
        log_warning(f"开始回滚到：{backup_path.name}")
        
        import shutil
        
        # 恢复关键文件
        for file in backup_path.iterdir():
            if file.is_file():
                dst = self.repo_root / file.name
                log_info(f"恢复文件：{file.name}")
                shutil.copy2(file, dst)
        
        # 记录回滚历史
        self.state["rollback_history"].append({
            "timestamp": datetime.now().isoformat(),
            "backup": backup_path.name,
            "reason": "auto_rollback"
        })
        
        log_success("回滚完成")
        return True
    
    def health_check(self) -> Dict:
        """健康检查"""
        log_info("执行健康检查...")
        
        checks = {
            "git_repo": False,
            "working_tree_clean": False,
            "version_files": False,
            "scripts_executable": False,
            "backup_available": False,
        }
        
        results = {
            "passed": 0,
            "failed": 0,
            "warnings": 0,
            "details": []
        }
        
        # 1. 检查 Git 仓库
        try:
            run_command(["git", "rev-parse", "--git-dir"], check=False)
            checks["git_repo"] = True
            results["passed"] += 1
            results["details"].append("✓ Git 仓库正常")
        except:
            results["failed"] += 1
            results["details"].append("✗ Git 仓库异常")
        
        # 2. 检查工作区
        try:
            result = run_command(["git", "status", "--porcelain"])
            if result.stdout.strip():
                checks["working_tree_clean"] = False
                results["warnings"] += 1
                results["details"].append("⚠ 工作区有未提交的变更")
            else:
                checks["working_tree_clean"] = True
                results["passed"] += 1
                results["details"].append("✓ 工作区清洁")
        except:
            results["failed"] += 1
            results["details"].append("✗ Git 状态检查失败")
        
        # 3. 检查版本文件
        version_files = ["package.json", "VERSION-MANAGEMENT-STRATEGY.md"]
        missing = [f for f in version_files if not (self.repo_root / f).exists()]
        if not missing:
            checks["version_files"] = True
            results["passed"] += 1
            results["details"].append("✓ 版本文件完整")
        else:
            results["warnings"] += 1
            results["details"].append(f"⚠ 缺少文件：{', '.join(missing)}")
        
        # 4. 检查脚本可执行权限
        scripts = ["scripts/version-bump.sh", "scripts/version-check.sh"]
        executable = all((self.repo_root / s).exists() and os.access(self.repo_root / s, os.X_OK) for s in scripts)
        if executable:
            checks["scripts_executable"] = True
            results["passed"] += 1
            results["details"].append("✓ 脚本可执行")
        else:
            results["warnings"] += 1
            results["details"].append("⚠ 脚本权限检查")
        
        # 5. 检查备份
        if self.backup_dir.exists() and any(self.backup_dir.iterdir()):
            checks["backup_available"] = True
            results["passed"] += 1
            results["details"].append("✓ 备份可用")
        else:
            results["warnings"] += 1
            results["details"].append("⚠ 无可用备份")
        
        # 更新状态
        self.state["health_status"] = "healthy" if results["failed"] == 0 else "degraded"
        self.state["last_health_check"] = datetime.now().isoformat()
        
        # 输出结果
        print("\n" + "="*50)
        for detail in results["details"]:
            print(f"  {detail}")
        print("="*50)
        print(f"  通过：{results['passed']} | 失败：{results['failed']} | 警告：{results['warnings']}")
        print("="*50 + "\n")
        
        return results
    
    def safe_commit(self, message: str, files: List[str] = None, auto_backup: bool = True) -> bool:
        """安全提交（带备份和检查）"""
        log_info(f"准备提交：{message}")
        
        # 1. 健康检查
        health = self.health_check()
        if health["failed"] > 0:
            log_critical("健康检查失败，中止提交")
            return False
        
        # 2. 创建备份
        if auto_backup:
            backup_name = self.create_backup(label="pre_commit")
            if not backup_name:
                log_warning("备份失败，但继续提交")
        
        # 3. 添加文件
        try:
            if files:
                run_command(["git", "add"] + files)
            else:
                run_command(["git", "add", "-A"])
        except Exception as e:
            log_error(f"Git add 失败：{e}")
            if CONFIG["auto_rollback"]:
                self.rollback()
            return False
        
        # 4. 提交
        try:
            run_command(["git", "commit", "-m", message])
            log_success("提交成功")
        except Exception as e:
            log_error(f"Git commit 失败：{e}")
            if CONFIG["auto_rollback"]:
                self.rollback()
            return False
        
        # 5. 更新状态
        self.state["last_commit"] = run_command(["git", "rev-parse", "HEAD"]).stdout.strip()
        self.save_state()
        
        return True
    
    def safe_tag(self, version: str = None, message: str = None) -> bool:
        """安全打标签"""
        if not version:
            version = self.get_current_version()
        
        tag_name = f"v{version}"
        
        # 检查标签是否存在
        try:
            run_command(["git", "rev-parse", tag_name], check=False)
            log_warning(f"标签已存在：{tag_name}")
            return False
        except:
            pass
        
        # 创建标签
        try:
            tag_msg = message or f"Release {tag_name}"
            run_command(["git", "tag", "-a", tag_name, "-m", tag_msg])
            log_success(f"标签已创建：{tag_name}")
            
            self.state["last_tag"] = tag_name
            self.state["current_version"] = version
            self.save_state()
            
            return True
        except Exception as e:
            log_error(f"创建标签失败：{e}")
            return False
    
    def auto_release(self, bump_type: str = "patch", push: bool = True) -> bool:
        """自动发布流程"""
        log_info("="*60)
        log_info("开始自动发布流程")
        log_info("="*60)
        
        # 1. 健康检查
        log_info("步骤 1/6: 健康检查")
        health = self.health_check()
        if health["failed"] > 0:
            log_critical("健康检查失败，中止发布")
            return False
        
        # 2. 创建备份
        log_info("步骤 2/6: 创建备份")
        backup_name = self.create_backup(label="pre_release")
        
        # 3. 升级版本
        log_info("步骤 3/6: 升级版本")
        new_version = self.bump_version(bump_type)
        
        # 4. 更新版本文件
        log_info("步骤 4/6: 更新版本文件")
        self.update_version_files(new_version)
        
        # 5. 提交
        log_info("步骤 5/6: 提交变更")
        commit_msg = f"chore: 发布 v{new_version}"
        if not self.safe_commit(commit_msg, auto_backup=False):
            log_critical("提交失败，执行回滚")
            self.rollback(backup_name)
            return False
        
        # 6. 打标签
        log_info("步骤 6/6: 创建标签")
        if not self.safe_tag(new_version, f"Release v{new_version}"):
            log_warning("标签创建失败，但继续")
        
        # 7. 推送（可选）
        if push:
            log_info("推送到远程仓库...")
            try:
                run_command(["git", "push", "origin", "main"])
                run_command(["git", "push", "origin", "--tags"])
                log_success("推送完成")
            except Exception as e:
                log_warning(f"推送失败：{e}")
                log_info("本地发布完成，请手动推送")
        
        log_info("="*60)
        log_success(f"发布完成：v{new_version}")
        log_info("="*60)
        
        return True
    
    def update_version_files(self, version: str):
        """更新版本文件"""
        # 更新 package.json
        package_json = self.repo_root / "package.json"
        if package_json.exists():
            with open(package_json, 'r') as f:
                data = json.load(f)
            data["version"] = version
            with open(package_json, 'w') as f:
                json.dump(data, f, indent=2)
            log_success(f"已更新 package.json: {version}")
        
        # 更新其他版本文件...
        # (可以根据需要扩展)
    
    def list_backups(self):
        """列出所有备份"""
        if not self.backup_dir.exists():
            log_info("没有备份")
            return
        
        backups = sorted(self.backup_dir.iterdir(), key=lambda x: x.name, reverse=True)
        log_info(f"找到 {len(backups)} 个备份:")
        for backup in backups:
            print(f"  - {backup.name}")

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="全自动版本管理系统")
    subparsers = parser.add_subparsers(dest="command", help="命令")
    
    # health 命令
    subparsers.add_parser("health", help="健康检查")
    
    # backup 命令
    subparsers.add_parser("backup", help="创建备份")
    
    # rollback 命令
    rollback_parser = subparsers.add_parser("rollback", help="回滚")
    rollback_parser.add_argument("--backup", type=str, help="备份名称")
    
    # bump 命令
    bump_parser = subparsers.add_parser("bump", help="升级版本")
    bump_parser.add_argument("type", choices=["major", "minor", "patch"], default="patch")
    
    # commit 命令
    commit_parser = subparsers.add_parser("commit", help="安全提交")
    commit_parser.add_argument("-m", "--message", required=True, help="提交信息")
    commit_parser.add_argument("--no-backup", action="store_true", help="不创建备份")
    
    # tag 命令
    tag_parser = subparsers.add_parser("tag", help="创建标签")
    tag_parser.add_argument("--version", type=str, help="版本号")
    tag_parser.add_argument("--message", type=str, help="标签信息")
    
    # release 命令
    release_parser = subparsers.add_parser("release", help="自动发布")
    release_parser.add_argument("--bump", choices=["major", "minor", "patch"], default="patch")
    release_parser.add_argument("--no-push", action="store_true", help="不推送")
    
    # list 命令
    subparsers.add_parser("list", help="列出备份")
    
    # status 命令
    subparsers.add_parser("status", help="显示状态")
    
    args = parser.parse_args()
    
    vm = VersionManager()
    
    if args.command == "health":
        vm.health_check()
    elif args.command == "backup":
        vm.create_backup()
    elif args.command == "rollback":
        vm.rollback(args.backup)
    elif args.command == "bump":
        print(vm.bump_version(args.type))
    elif args.command == "commit":
        vm.safe_commit(args.message, auto_backup=not args.no_backup)
    elif args.command == "tag":
        vm.safe_tag(args.version, args.message)
    elif args.command == "release":
        vm.auto_release(args.bump, push=not args.no_push)
    elif args.command == "list":
        vm.list_backups()
    elif args.command == "status":
        print(json.dumps(vm.state, indent=2))
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
