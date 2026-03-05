#!/usr/bin/env python3
"""
Project Structure Optimizer
执行项目结构优化
"""

import os
import shutil
from pathlib import Path

class ProjectStructureOptimizer:
    """项目结构优化器"""
    
    def __init__(self, root_path=".", dry_run=True):
        self.root = Path(root_path).resolve()
        self.dry_run = dry_run
        self.actions = []
        
    def optimize(self):
        """执行优化"""
        print(f"{'🔍' if self.dry_run else '🚀'} 项目结构优化")
        print(f"模式：{'预览' if self.dry_run else '执行'}")
        print("=" * 60)
        
        self.move_development_docs()
        self.consolidate_configs()
        self.cleanup_duplicates()
        
        self.print_summary()
        
    def move_development_docs(self):
        """移动开发文档"""
        print("\n📝 移动开发文档到 docs/development/")
        print("-" * 60)
        
        doc_mappings = [
            # 娱乐功能
            (['ENTERTAINMENT-PLAN.md', 'ENTERTAINMENT-REPORT-2026-03-05.md'], 
             'docs/development/features/entertainment/'),
            
            # 外部探索
            (['EXTERNAL-EXPLORATION-DAILY-2026-03-05.md', 
              'EXTERNAL-EXPLORATION-PLAN.md',
              'EXTERNAL-EXPLORATION-READY.md',
              'EXTERNAL-EXPLORATION-REPORT-2026-03-05.md'],
             'docs/development/reports/exploration/'),
            
            # 积分系统
            (['POINTS-REPORT-2026-03-05.md', 'POINTS-SYSTEM.md'],
             'docs/development/features/points/'),
            
            # MindForge
            (['MINDFORGE-PROJECT.md', 'MINDFORGE-SUMMARY.md'],
             'docs/development/features/mindforge/'),
            
            # 学习系统
            (['LEARNING-TOOLS-SYSTEM.md', 
              'TASK-LEARNING-SYSTEM.md',
              'SKILL-HELPER-QUICK-REF.md'],
             'docs/development/guides/learning/'),
        ]
        
        for files, target_dir in doc_mappings:
            target_path = self.root / target_dir
            moved = []
            
            for filename in files:
                src = self.root / filename
                if src.exists():
                    if not self.dry_run:
                        target_path.mkdir(parents=True, exist_ok=True)
                        shutil.move(str(src), str(target_path / filename))
                    moved.append(filename)
            
            if moved:
                action = f"移动 {len(moved)} 个文件 → {target_dir}"
                self.actions.append(action)
                print(f"  ✅ {action}")
                for f in moved:
                    print(f"     - {f}")
    
    def consolidate_configs(self):
        """集中配置文件"""
        print("\n⚙️ 集中配置文件到 config/")
        print("-" * 60)
        
        config_mappings = [
            # Docker 配置
            (['Dockerfile', 'Dockerfile.sandbox', 'Dockerfile.sandbox-browser', 
              'Dockerfile.sandbox-common', 'docker-compose.yml'],
             'config/docker/'),
            
            # Vitest 配置
            (['vitest.channels.config.ts', 'vitest.config.ts', 
              'vitest.e2e.config.ts', 'vitest.extensions.config.ts',
              'vitest.gateway.config.ts', 'vitest.live.config.ts',
              'vitest.scoped-config.ts', 'vitest.unit.config.ts'],
             'config/vitest/'),
            
            # 其他配置
            (['config-template.json', 'tsconfig.plugin-sdk.dts.json',
              'zizmor.yml', 'pnpm-workspace.yaml', 'render.yaml',
              'fly.toml', 'fly.private.toml'],
             'config/'),
        ]
        
        for files, target_dir in config_mappings:
            target_path = self.root / target_dir
            moved = []
            
            for filename in files:
                src = self.root / filename
                if src.exists():
                    if not self.dry_run:
                        target_path.mkdir(parents=True, exist_ok=True)
                        shutil.move(str(src), str(target_path / filename))
                    moved.append(filename)
            
            if moved:
                action = f"移动 {len(moved)} 个配置 → {target_dir}"
                self.actions.append(action)
                print(f"  ✅ {action}")
                for f in moved[:3]:  # 只显示前 3 个
                    print(f"     - {f}")
                if len(moved) > 3:
                    print(f"     ... 还有 {len(moved) - 3} 个")
    
    def cleanup_duplicates(self):
        """清理重复目录"""
        print("\n🗑️ 清理重复目录")
        print("-" * 60)
        
        # workspace-backup 可以保留（作为备份）
        # templates 重复需要合并
        
        template_dirs = [
            'src/line/flex-templates',
            'docs/zh-CN/reference/templates',
            'docs/reference/templates',
            'config/templates',
        ]
        
        print(f"  ℹ️  发现 {len(template_dirs)} 个 templates 目录")
        print(f"     建议：保留 config/templates/，其他删除或合并")
        
        self.actions.append(f"检测 {len(template_dirs)} 个重复 templates 目录")
    
    def print_summary(self):
        """打印总结"""
        print("\n" + "=" * 60)
        print("📊 优化总结")
        print("=" * 60)
        
        print(f"\n执行操作：{len(self.actions)} 项")
        for i, action in enumerate(self.actions, 1):
            print(f"  {i}. {action}")
        
        if self.dry_run:
            print("\n💡 预览模式 - 使用 --execute 执行实际优化")
            print("   python3 scripts/optimize-structure.py --execute")
        else:
            print("\n✅ 优化完成！")
            print("   记得提交更改：git add -A && git commit -m 'refactor: 优化项目结构'")


if __name__ == '__main__':
    import sys
    
    dry_run = '--execute' not in sys.argv
    optimizer = ProjectStructureOptimizer(dry_run=dry_run)
    optimizer.optimize()
