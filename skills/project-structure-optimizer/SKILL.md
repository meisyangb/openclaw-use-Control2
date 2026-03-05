# Project Structure Optimizer Skill

**版本**: v1.0.0  
**创建日期**: 2026-03-05  
**目标**: 优化大型项目的目录结构，保持清晰和可维护性

---

## 🎯 核心原则

### 1. 根目录简洁 (Clean Root)
- 根目录只保留 **必要** 的配置文件和入口文件
- 目标：< 30 个文件/目录
- 所有开发文档归档到 `docs/`

### 2. 功能分组 (Functional Grouping)
- 相关功能放在同一目录
- 避免功能分散在多处
- 使用一致的命名约定

### 3. 深度适中 (Moderate Depth)
- 目录深度：3-5 层为佳
- 避免过浅（混乱）或过深（难找）
- 每层有明确的职责

### 4. 文档集中 (Centralized Docs)
- 所有文档在 `docs/` 下
- 按功能/模块分类
- 保持 README 简洁

---

## 📋 检查清单

### 根目录检查

```bash
# 检查根目录文件数
ls -1 | wc -l  # 目标：< 30

# 列出所有 markdown 文件
find . -maxdepth 1 -name "*.md"  # 目标：< 10

# 检查重复目录
find . -maxdepth 2 -type d -name "*backup*" -o -name "*old*" -o -name "*tmp*"
```

### 常见问题检测

| 问题 | 检测命令 | 解决方案 |
|------|---------|---------|
| 根目录过乱 | `ls -1 \| wc -l` | 移动文件到子目录 |
| 文档分散 | `find . -name "*.md"` | 归档到 `docs/` |
| 重复目录 | `find . -type d -name "*backup*"` | 合并或删除 |
| 配置分散 | `find . -name "*.json" -o -name "*.yml"` | 集中到 `config/` |
| 临时文件 | `find . -name "*.tmp" -o -name "*.bak"` | 清理 |

---

## 🏗️ 推荐结构

### 标准开源项目结构

```
project-root/
├── .github/                    # GitHub 配置
├── .vscode/                    # IDE 配置
├── .openclaw/                  # OpenClaw 配置
│
├── src/                        # 源代码 ⭐
│   ├── cli/                    # CLI 工具
│   ├── gateway/                # 网关服务
│   ├── plugins/                # 插件系统
│   └── ...                     # 其他模块
│
├── packages/                   # 子包 (monorepo)
├── apps/                       # 应用程序
├── extensions/                 # 扩展插件
│
├── docs/                       # 文档 ⭐
│   ├── zh-CN/                  # 中文文档
│   ├── reference/              # API 参考
│   ├── guides/                 # 使用指南
│   ├── design/                 # 设计文档
│   └── development/            # 开发文档
│       ├── features/           # 功能开发
│       ├── reports/            # 开发报告
│       └── plans/              # 开发计划
│
├── config/                     # 配置文件 ⭐
│   ├── docker/                 # Docker 配置
│   ├── vitest/                 # 测试配置
│   └── templates/              # 配置模板
│
├── scripts/                    # 脚本工具 ⭐
├── test/                       # 测试文件
├── skills/                     # AI Skills
│
├── dev/                        # 开发工作空间 ⭐
│   ├── memory/                 # 记忆文件
│   ├── scripts/                # 开发脚本
│   ├── projects/               # 开发项目
│   └── logs/                   # 开发日志
│
├── dist/                       # 构建输出
├── node_modules/               # 依赖
│
├── README.md                   # 项目说明 ⭐
├── LICENSE                     # 许可证
├── package.json                # 项目配置 ⭐
├── tsconfig.json               # TypeScript 配置
└── ...                         # 其他必要配置
```

---

## 🔧 优化步骤

### Step 1: 分析当前结构

```bash
# 1. 统计根目录文件
echo "=== 根目录文件统计 ==="
ls -1 | wc -l

# 2. 列出所有 markdown
echo "=== Markdown 文件 ==="
find . -maxdepth 1 -name "*.md" -type f

# 3. 查找配置文件
echo "=== 配置文件 ==="
find . -maxdepth 1 -name "*.json" -o -name "*.yml" -o -name "*.toml" | head -20

# 4. 查找重复目录
echo "=== 可能的重复目录 ==="
find . -maxdepth 2 -type d \( -name "*backup*" -o -name "*old*" -o -name "*tmp*" \)
```

### Step 2: 创建目标目录

```bash
# 创建文档分类
mkdir -p docs/development/{features,reports,plans}
mkdir -p docs/guides
mkdir -p docs/reference

# 创建配置目录
mkdir -p config/{docker,vitest,templates}

# 创建开发空间
mkdir -p dev/{memory,scripts,projects,logs}
```

### Step 3: 移动文件

```bash
# 移动开发文档
mv ENTERTAINMENT-*.md docs/development/features/ 2>/dev/null || true
mv EXTERNAL-EXPLORATION-*.md docs/development/reports/ 2>/dev/null || true
mv POINTS-*.md docs/development/features/ 2>/dev/null || true
mv MINDFORGE-*.md docs/development/features/ 2>/dev/null || true
mv LEARNING-*.md docs/development/guides/ 2>/dev/null || true

# 移动配置文件
mv Dockerfile* config/docker/ 2>/dev/null || true
mv docker-compose.yml config/docker/ 2>/dev/null || true
mv vitest.*.config.ts config/vitest/ 2>/dev/null || true

# 清理临时文件
find . -name "*.tmp" -delete 2>/dev/null || true
find . -name "*.bak" -delete 2>/dev/null || true
```

### Step 4: 验证结果

```bash
# 检查根目录文件数
echo "=== 优化后根目录文件数 ==="
ls -1 | wc -l

# 检查文档结构
echo "=== 文档结构 ==="
tree docs -L 2

# 检查配置结构
echo "=== 配置结构 ==="
tree config -L 2
```

---

## 📊 优化指标

### 关键指标

| 指标 | 优化前 | 目标 | 优化后 |
|------|--------|------|--------|
| 根目录文件数 | 50+ | < 30 | ✅ |
| 根目录 markdown | 20+ | < 10 | ✅ |
| 文档集中度 | 分散 | 100% 在 docs/ | ✅ |
| 配置集中度 | 分散 | 100% 在 config/ | ✅ |
| 重复目录数 | 3+ | 0 | ✅ |

### 质量检查

```bash
# 1. 根目录简洁度
root_count=$(ls -1 | wc -l)
if [ $root_count -lt 30 ]; then
    echo "✅ 根目录简洁：$root_count 个文件"
else
    echo "⚠️ 根目录过乱：$root_count 个文件"
fi

# 2. 文档集中度
doc_count=$(find . -maxdepth 1 -name "*.md" | wc -l)
if [ $doc_count -lt 10 ]; then
    echo "✅ 文档集中：$doc_count 个在根目录"
else
    echo "⚠️ 文档分散：$doc_count 个在根目录"
fi

# 3. 配置集中度
config_in_root=$(find . -maxdepth 1 -name "*.json" -o -name "*.yml" -o -name "*.toml" | wc -l)
echo "📋 根目录配置文件：$config_in_root 个"
```

---

## 🎓 最佳实践

### 1. 定期清理

```bash
# 每周检查
find . -maxdepth 1 -type f -mtime +30  # 30 天未修改的文件
find . -name "*.tmp" -o -name "*.bak"  # 临时文件
```

### 2. 文档规范

- 所有新功能文档 → `docs/development/features/`
- 所有报告 → `docs/development/reports/`
- 所有计划 → `docs/development/plans/`
- 用户指南 → `docs/guides/`
- API 参考 → `docs/reference/`

### 3. 配置管理

- Docker 配置 → `config/docker/`
- 测试配置 → `config/vitest/`
- 模板文件 → `config/templates/`
- 环境变量 → `.env` (不提交)

### 4. 开发空间

- 记忆文件 → `dev/memory/`
- 开发脚本 → `dev/scripts/`
- 实验项目 → `dev/projects/`
- 开发日志 → `dev/logs/`

---

## 🔍 常见问题

### Q1: 根目录还是太乱怎么办？

**A**: 继续分类移动：
```bash
# 移动不常用的配置
mv *.toml config/ 2>/dev/null || true
mv *.yml config/ 2>/dev/null || true

# 创建顶级文档索引
cat > README.md << 'EOF'
# 项目文档索引

- [开发文档](docs/development/)
- [使用指南](docs/guides/)
- [API 参考](docs/reference/)
EOF
```

### Q2: 如何保持结构长期整洁？

**A**: 建立规范：
1. 新文件必须放在合适的子目录
2. 定期运行清理脚本
3. 代码审查时检查文件位置
4. 使用 Git hooks 防止误提交

### Q3: 移动文件后 Git 历史怎么办？

**A**: Git 会自动跟踪：
```bash
# Git 会识别重命名
git mv old/path/file.md new/path/file.md

# 或者批量移动后
git add -A
git status  # Git 会显示 rename
```

---

## 📚 参考资源

### OpenClaw 内置
- `src/config/` - 配置管理
- `src/infra/` - 基础设施代码组织

### 外部参考
- [Angular Project Structure](https://angular.io/guide/file-structure)
- [Monorepo Best Practices](https://monorepo.tools/)
- [Keep a Changelog](https://keepachangelog.com/)

---

## 🚀 快速开始

```bash
# 1. 运行分析
python3 scripts/project-structure-analyzer.py

# 2. 执行优化
python3 scripts/project-structure-optimizer.py --dry-run  # 预览
python3 scripts/project-structure-optimizer.py --execute  # 执行

# 3. 验证结果
python3 scripts/project-structure-analyzer.py --report
```

---

*此技能持续改进中，欢迎反馈和建议。*

**维护者**: FullStack Engineer with Memory Intelligence  
**最后更新**: 2026-03-05  
**版本**: 1.0.0
