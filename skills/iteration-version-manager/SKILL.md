# Iteration Version Manager Skill

**版本**: v1.0  
**创建日期**: 2026-03-05  
**目标**: 管理 AI 助手的迭代版本，支持版本标记、回滚、历史记录

---

## 🎯 核心功能

### 1. 版本标记 (Tagging)

每次迭代更新自动创建 Git 标签：
```bash
# 格式：v{日期}-{迭代号}-{描述}
v20260305-1900-structure-optimization
v20260305-1930-code-standards
v20260305-1945-iteration-update
```

### 2. 版本记录 (Logging)

记录每个版本的：
- 时间戳
- 变更内容
- 提交哈希
- 版本状态（stable/beta/deprecated）

### 3. 版本回滚 (Rollback)

如果新版本出错，快速回滚到稳定版本：
```bash
# 回滚到上一个稳定版本
git revert --no-edit HEAD
git tag -a v20260305-1900-rollback -m "Rollback to stable version"
```

### 4. 版本历史 (History)

维护版本历史文件：
```markdown
## 版本历史

### v20260305-1945 (2026-03-05 19:45)
- 全面规范化更新
- 根目录文件：62 → 37
- 状态：stable

### v20260305-1930 (2026-03-05 19:30)
- 创建代码规范 Skill
- 状态：stable
```

---

## 📋 使用流程

### 标准迭代流程

```bash
# 1. 开始迭代前记录当前版本
git log -1 --oneline
# 输出：9f1f2f3 refactor: 全面规范化更新

# 2. 执行变更
# ... 修改代码、添加功能 ...

# 3. 提交变更
git add -A
git commit -m "feat: 添加新功能"

# 4. 创建版本标签
ITERATION_TIME=$(date +%Y%m%d-%H%M)
git tag -a "v${ITERATION_TIME}-iteration" -m "迭代更新 $(date '+%Y-%m-%d %H:%M:%S')"

# 5. 推送到 GitHub
git push origin main --tags

# 6. 记录到版本历史
echo "### v${ITERATION_TIME} ($(date '+%Y-%m-%d %H:%M'))" >> VERSIONS.md
echo "- 迭代更新" >> VERSIONS.md
echo "- 状态：testing" >> VERSIONS.md
echo "" >> VERSIONS.md
```

### 版本回滚流程

```bash
# 1. 检测问题
# - 功能异常
# - 测试失败
# - 性能下降

# 2. 查看版本历史
cat VERSIONS.md | grep "stable"

# 3. 回滚到稳定版本
STABLE_VERSION="v20260305-1900"
git checkout ${STABLE_VERSION}
git checkout -b rollback/${STABLE_VERSION}

# 4. 标记问题版本
git tag -a "v20260305-1945-deprecated" -m "Deprecated due to bugs"

# 5. 推送回滚
git push origin rollback/${STABLE_VERSION} --tags
```

---

## 🛠️ 自动化脚本

### 创建迭代版本

```bash
#!/bin/bash
# scripts/create-iteration.sh

# 检查 Git 状态
if [[ -n $(git status -s) ]]; then
    echo "❌ 有未提交的变更"
    exit 1
fi

# 生成版本标签
ITERATION_TIME=$(date +%Y%m%d-%H%M)
VERSION_TAG="v${ITERATION_TIME}-iteration"

# 创建标签
git tag -a "${VERSION_TAG}" -m "Iteration $(date '+%Y-%m-%d %H:%M:%S')"

# 推送
git push origin --tags

# 记录
echo "### ${VERSION_TAG} ($(date '+%Y-%m-%d %H:%M'))" >> VERSIONS.md
echo "- 迭代更新" >> VERSIONS.md
echo "- 提交：$(git log -1 --oneline)" >> VERSIONS.md
echo "- 状态：testing" >> VERSIONS.md
echo "" >> VERSIONS.md

echo "✅ 创建版本：${VERSION_TAG}"
```

### 版本回滚

```bash
#!/bin/bash
# scripts/rollback-version.sh

TARGET_VERSION=$1

if [[ -z "${TARGET_VERSION}" ]]; then
    echo "❌ 请指定目标版本"
    echo "用法：./scripts/rollback-version.sh v20260305-1900"
    exit 1
fi

# 检查版本是否存在
if ! git tag -l | grep -q "${TARGET_VERSION}"; then
    echo "❌ 版本不存在：${TARGET_VERSION}"
    exit 1
fi

# 回滚
git checkout ${TARGET_VERSION}
git checkout -b rollback/${TARGET_VERSION}

# 标记当前版本为废弃
CURRENT_VERSION=$(git describe --tags --abbrev=0)
git tag -a "${CURRENT_VERSION}-deprecated" -m "Deprecated, rolled back to ${TARGET_VERSION}"

# 推送
git push origin rollback/${TARGET_VERSION} --tags

echo "✅ 回滚到版本：${TARGET_VERSION}"
```

### 版本检查

```bash
#!/bin/bash
# scripts/check-version.sh

echo "📊 当前版本信息"
echo "==============="

# 当前标签
CURRENT_TAG=$(git describe --tags --abbrev=0 2>/dev/null || echo "无标签")
echo "当前标签：${CURRENT_TAG}"

# 最近 5 个版本
echo ""
echo "最近版本:"
git tag -l "v*" --sort=-version:refname | head -5

# 版本统计
echo ""
echo "版本统计:"
echo "总标签数：$(git tag -l | wc -l)"
echo "稳定版本：$(git tag -l | grep -c "stable" || echo 0)"
echo "废弃版本：$(git tag -l | grep -c "deprecated" || echo 0)"
```

---

## 📁 文件结构

```
openclaw-main/
├── scripts/
│   ├── create-iteration.sh    # 创建迭代版本
│   ├── rollback-version.sh    # 版本回滚
│   ├── check-version.sh       # 版本检查
│   └── list-versions.sh       # 列出所有版本
├── VERSIONS.md                # 版本历史记录 ⭐
├── .github/
│   └── workflows/
│       └── version-tag.yml    # 自动标签工作流
└── skills/
    └── iteration-version-manager/
        └── SKILL.md           # 本文档
```

---

## 📝 VERSIONS.md 模板

```markdown
# 版本历史

## 2026-03-05

### v20260305-1945 (19:45)
- **变更**: 全面规范化更新
- **提交**: 9f1f2f3
- **状态**: ✅ stable
- **备注**: 根目录优化完成

### v20260305-1930 (19:30)
- **变更**: 创建代码规范 Skill
- **提交**: d3862fd
- **状态**: ✅ stable
- **备注**: 添加 ESLint/Prettier 配置

### v20260305-1900 (19:00)
- **变更**: 项目结构优化
- **提交**: 278d63c
- **状态**: ✅ stable
- **备注**: 文档归档完成

## 回滚记录

### v20260305-1945-deprecated
- **回滚时间**: 2026-03-05 20:00
- **回滚原因**: 发现配置错误
- **回滚到**: v20260305-1930
```

---

## 🎓 最佳实践

### 1. 版本命名

**推荐格式**:
```
v{日期}-{时间}-{描述}
v20260305-1945-structure-opt
v20260305-2000-bugfix-login
```

**状态标记**:
```
v20260305-1945-stable      # 稳定版本
v20260305-1945-beta        # 测试版本
v20260305-1945-deprecated  # 废弃版本
```

### 2. 迭代频率

- **小迭代**: 每 30-60 分钟（功能开发中）
- **中迭代**: 每 2-4 小时（功能完成）
- **大迭代**: 每天（每日总结）

### 3. 版本保护

```bash
# 保护稳定版本
git tag -a "v20260305-1900-stable" -m "Stable release"

# 不要删除稳定版本标签
# 如果必须删除，先标记为 deprecated
git tag "v20260305-1900-deprecated"
```

### 4. 回滚策略

```bash
# 1. 小问题 → 热修复
git commit -m "fix: 快速修复"
git tag "v20260305-1946-hotfix"

# 2. 中等问题 → 回滚 + 修复
./scripts/rollback-version.sh v20260305-1930
# 在 rollback 分支修复

# 3. 严重问题 → 立即回滚
git reset --hard v20260305-1900
git push --force
```

---

## 🔍 故障排除

### 问题：标签太多混乱

```bash
# 只查看稳定版本
git tag -l "*-stable"

# 删除废弃版本（谨慎）
git tag -d v20260305-1945-deprecated
git push origin :refs/tags/v20260305-1945-deprecated
```

### 问题：忘记打标签

```bash
# 补打标签到之前的提交
git tag -a v20260305-1930-late abc123 -m "补打的标签"
```

### 问题：回滚后历史丢失

```bash
# 使用 revert 而不是 reset
git revert HEAD
# 这样保留历史记录
```

---

## 📚 参考资源

- [Git Tagging](https://git-scm.com/book/en/v2/Git-Basics-Tagging)
- [Git Revert](https://git-scm.com/docs/git-revert)
- [Semantic Versioning](https://semver.org/)
- [GitHub Releases](https://docs.github.com/en/repositories/releasing-projects-on-github)

---

## 🚀 快速开始

```bash
# 1. 查看当前版本
./scripts/check-version.sh

# 2. 创建新迭代
./scripts/create-iteration.sh

# 3. 推送到 GitHub
git push origin main --tags

# 4. 如果需要回滚
./scripts/rollback-version.sh v20260305-1900
```

---

*最后更新：2026-03-05 19:46*  
**维护者**: FullStack Engineer with Memory Intelligence
