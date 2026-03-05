#!/usr/bin/env python3
"""
Project Structure Analyzer
分析项目结构，识别问题，提供优化建议
"""

import os
import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict

class ProjectStructureAnalyzer:
    """项目结构分析器"""
    
    def __init__(self, root_path="."):
        self.root = Path(root_path).resolve()
        self.issues = []
        self.stats = defaultdict(int)
        
    def analyze(self):
        """执行完整分析"""
        print(f"🔍 分析项目结构：{self.root}\n")
        
        self.analyze_root_directory()
        self.analyze_markdown_files()
        self.analyze_config_files()
        self.analyze_directory_depth()
        self.find_duplicate_directories()
        self.find_large_files()
        
        self.print_report()
        
    def analyze_root_directory(self):
        """分析根目录"""
        print("📊 根目录分析")
        print("=" * 50)
        
        items = list(self.root.iterdir())
        files = [i for i in items if i.is_file()]
        dirs = [i for i in items if i.is_dir() and not i.name.startswith('.')]
        
        self.stats['root_total'] = len(items)
        self.stats['root_files'] = len(files)
        self.stats['root_dirs'] = len(dirs)
        
        print(f"总项目数：{len(items)}")
        print(f"  - 文件：{len(files)}")
        print(f"  - 目录：{len(dirs)}")
        
        # 检查是否过多
        if len(items) > 30:
            self.issues.append({
                'severity': '⚠️',
                'type': 'root_cluttered',
                'message': f'根目录文件过多 ({len(items)} > 30)',
                'suggestion': '移动文件到子目录 (docs/, config/, scripts/)'
            })
        else:
            print("✅ 根目录简洁")
        
        print()
        
    def analyze_markdown_files(self):
        """分析 Markdown 文件"""
        print("📝 Markdown 文件分析")
        print("=" * 50)
        
        md_files = list(self.root.glob("*.md"))
        self.stats['root_markdown'] = len(md_files)
        
        print(f"根目录 Markdown 文件：{len(md_files)}")
        
        if md_files:
            print("\n文件列表:")
            for f in md_files:
                print(f"  - {f.name}")
        
        # 检查是否应该移动到 docs/
        movable_docs = [
            'CHANGELOG', 'CONTRIBUTING', 'SECURITY',
            'ENTERTAINMENT', 'EXTERNAL', 'POINTS',
            'MINDFORGE', 'LEARNING', 'MODULE',
            'VERSION', 'CONTINUOUS'
        ]
        
        should_move = []
        for f in md_files:
            for pattern in movable_docs:
                if pattern in f.name.upper():
                    should_move.append(f.name)
                    break
        
        if should_move:
            self.issues.append({
                'severity': '⚠️',
                'type': 'docs_scattered',
                'message': f'{len(should_move)} 个文档应移动到 docs/',
                'files': should_move,
                'suggestion': 'mv *.md docs/development/'
            })
        else:
            print("✅ 文档组织良好")
        
        print()
        
    def analyze_config_files(self):
        """分析配置文件"""
        print("⚙️ 配置文件分析")
        print("=" * 50)
        
        config_patterns = ['*.json', '*.yml', '*.yaml', '*.toml']
        config_files = []
        
        for pattern in config_patterns:
            config_files.extend(self.root.glob(pattern))
        
        # 排除 package.json, tsconfig.json 等必要文件
        essential_configs = {
            'package.json', 'package-lock.json', 'pnpm-lock.yaml',
            'tsconfig.json', 'pyproject.toml', '.gitignore'
        }
        
        movable_configs = [f for f in config_files 
                          if f.name not in essential_configs 
                          and not f.name.startswith('.')]
        
        self.stats['root_configs'] = len(movable_configs)
        
        print(f"可移动的配置文件：{len(movable_configs)}")
        
        if movable_configs:
            print("\n建议移动到 config/:")
            for f in movable_configs:
                print(f"  - {f.name}")
            
            self.issues.append({
                'severity': 'ℹ️',
                'type': 'configs_scattered',
                'message': f'{len(movable_configs)} 个配置文件可集中管理',
                'suggestion': 'mv *.yml *.toml config/'
            })
        
        print()
        
    def analyze_directory_depth(self):
        """分析目录深度"""
        print("📏 目录深度分析")
        print("=" * 50)
        
        depths = []
        
        for dirpath, dirnames, filenames in os.walk(self.root):
            # 跳过 node_modules, .git 等
            if any(x in dirpath for x in ['node_modules', '.git', 'dist']):
                continue
            
            depth = dirpath.replace(str(self.root), '').count(os.sep)
            depths.append(depth)
        
        if depths:
            avg_depth = sum(depths) / len(depths)
            max_depth = max(depths)
            
            self.stats['avg_depth'] = avg_depth
            self.stats['max_depth'] = max_depth
            
            print(f"平均深度：{avg_depth:.1f} 层")
            print(f"最大深度：{max_depth} 层")
            
            if max_depth > 7:
                self.issues.append({
                    'severity': '⚠️',
                    'type': 'too_deep',
                    'message': f'目录过深 (最大{max_depth}层)',
                    'suggestion': '考虑扁平化结构'
                })
            else:
                print("✅ 目录深度合理")
        
        print()
        
    def find_duplicate_directories(self):
        """查找重复目录"""
        print("🔍 重复目录检测")
        print("=" * 50)
        
        duplicate_patterns = ['backup', 'old', 'tmp', 'temp', 'copy', 'v2']
        duplicates = []
        
        for dirpath, dirnames, filenames in os.walk(self.root):
            # 跳过 node_modules, .git
            if any(x in dirpath for x in ['node_modules', '.git']):
                continue
            
            for dirname in dirnames:
                for pattern in duplicate_patterns:
                    if pattern in dirname.lower():
                        duplicates.append(os.path.join(dirpath, dirname))
        
        if duplicates:
            print(f"发现 {len(duplicates)} 个可能的重复目录:")
            for d in duplicates[:10]:  # 只显示前 10 个
                print(f"  - {d}")
            
            self.issues.append({
                'severity': '⚠️',
                'type': 'duplicate_dirs',
                'message': f'发现 {len(duplicates)} 个重复/临时目录',
                'suggestion': '清理或合并重复目录'
            })
        else:
            print("✅ 未发现重复目录")
        
        print()
        
    def find_large_files(self):
        """查找大文件"""
        print("📦 大文件检测")
        print("=" * 50)
        
        large_files = []
        size_threshold = 10 * 1024 * 1024  # 10MB
        
        for dirpath, dirnames, filenames in os.walk(self.root):
            # 跳过 node_modules, .git, dist
            if any(x in dirpath for x in ['node_modules', '.git', 'dist']):
                continue
            
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                try:
                    size = os.path.getsize(filepath)
                    if size > size_threshold:
                        large_files.append({
                            'path': filepath,
                            'size': size
                        })
                except:
                    pass
        
        if large_files:
            print(f"发现 {len(large_files)} 个大文件 (>10MB):")
            for f in sorted(large_files, key=lambda x: x['size'], reverse=True)[:10]:
                size_mb = f['size'] / (1024 * 1024)
                print(f"  - {f['path']} ({size_mb:.1f}MB)")
            
            self.issues.append({
                'severity': 'ℹ️',
                'type': 'large_files',
                'message': f'发现 {len(large_files)} 个大文件',
                'suggestion': '考虑使用 Git LFS 或移到外部存储'
            })
        else:
            print("✅ 未发现异常大文件")
        
        print()
        
    def print_report(self):
        """打印报告"""
        print("\n" + "=" * 50)
        print("📊 优化建议总结")
        print("=" * 50)
        
        if not self.issues:
            print("✅ 项目结构良好，无需优化！")
        else:
            for i, issue in enumerate(self.issues, 1):
                print(f"\n{i}. {issue['severity']} {issue['message']}")
                print(f"   建议：{issue['suggestion']}")
                if 'files' in issue:
                    print(f"   文件：{', '.join(issue['files'][:5])}")
        
        print("\n" + "=" * 50)
        print("📈 统计信息")
        print("=" * 50)
        
        for key, value in self.stats.items():
            if isinstance(value, float):
                print(f"{key}: {value:.1f}")
            else:
                print(f"{key}: {value}")
        
        # 保存报告
        report = {
            'timestamp': datetime.now().isoformat(),
            'root': str(self.root),
            'stats': dict(self.stats),
            'issues': self.issues
        }
        
        report_path = self.root / 'dev' / 'logs' / 'structure-analysis.json'
        report_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 报告已保存：{report_path}")


if __name__ == '__main__':
    import sys
    
    root_path = sys.argv[1] if len(sys.argv) > 1 else '.'
    analyzer = ProjectStructureAnalyzer(root_path)
    analyzer.analyze()
