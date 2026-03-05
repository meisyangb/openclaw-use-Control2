# 版本管理策略 (Version Management Strategy)

**文档版本**: v1.0  
**创建日期**: 2026-03-05  
**适用范围**: OpenClaw 本体 + 开发项目 (my-dev/)

---

## 📋 目录

1. [版本命名规范](#版本命名规范)
2. [Git 分支策略](#git-分支策略)
3. [提交规范](#提交规范)
4. [发布流程](#发布流程)
5. [标签管理](#标签管理)
6. [CHANGELOG 维护](#changelog-维护)
7. [自动化策略](#自动化策略)
8. [回滚与热修复](#回滚与热修复)

---

## 🎯 版本命名规范

### Semantic Versioning 2.0.0

采用语义化版本控制：`MAJOR.MINOR.PATCH-REVISION`

```
v2.1.3-42
│  │  │  └─ Revision: 构建次数/修订号（可选）
│  │  └──── Patch: 向后兼容的问题修复
│  └─────── Minor: 向后兼容的新功能
└────────── Major: 不兼容的 API 变更
```

### 版本类型

| 类型 | 格式 | 说明 | 示例 |
|------|------|------|------|
| **正式版** | `vMAJOR.MINOR.PATCH` | 生产环境使用 | `v2.1.0` |
| **预发布** | `vMAJOR.MINOR.PATCH-beta.N` | 测试版本 | `v2.1.0-beta.1` |
| **修订版** | `vMAJOR.MINOR.PATCH-RN` | 紧急修复 | `v2.1.3-42` |
| **开发版** | `vMAJOR.MINOR.PATCH-dev` | 开发中 | `v2.2.0-dev` |

### 版本号递增规则

```
1. PATCH++ : 修复 bug，不新增功能
   v2.1.3 → v2.1.4

2. MINOR++ : 新增功能，向下兼容
   v2.1.4 → v2.2.0

3. MAJOR++ : 破坏性变更
   v2.9.0 → v3.0.0
```

---

## 🌿 Git 分支策略

### 分支模型

```
main (生产)
  │
  ├─── develop (开发)
  │      │
  │      ├─── feature/* (新功能)
  │      ├─── bugfix/* (bug 修复)
  │      └─── hotfix/* (紧急修复)
  │
  └─── release/* (发布准备)
```

### 分支说明

| 分支 | 命名 | 来源 | 合并目标 | 说明 |
|------|------|------|----------|------|
| **主分支** | `main` | - | - | 生产环境，随时可发布 |
| **开发分支** | `develop` | `main` | `main` | 日常开发集成 |
| **功能分支** | `feature/xxx` | `develop` | `develop` | 新功能开发 |
| **修复分支** | `bugfix/xxx` | `develop` | `develop` | Bug 修复 |
| **热修复** | `hotfix/xxx` | `main` | `main` + `develop` | 生产紧急修复 |
| **发布分支** | `release/vX.Y.Z` | `develop` | `main` + `develop` | 发布准备 |

### 分支生命周期

```bash
# 创建功能分支
git checkout develop
git checkout -b feature/model-monitor-v2

# 开发完成后合并
git checkout develop
git merge --no-ff feature/model-monitor-v2
git branch -d feature/model-monitor-v2

# 发布流程
git checkout develop
git checkout -b release/v2.1.0
# 测试、修复、更新版本号
git checkout main
git merge --no-ff release/v2.1.0
git tag -a v2.1.0 -m "Release v2.1.0"
git checkout develop
git merge --no-ff release/v2.1.0
git branch -d release/v2.1.0
```

---

## ✍️ 提交规范

### Conventional Commits

遵循 [Conventional Commits 1.0.0](https://www.conventionalcommits.org/)

```
<type>(<scope>): <description>

[optional body]

[optional footer(s)]
```

### Type 类型

| Type | 说明 | 版本影响 |
|------|------|----------|
| `feat` | 新功能 | MINOR |
| `fix` | Bug 修复 | PATCH |
| `docs` | 文档更新 | - |
| `style` | 代码格式 | - |
| `refactor` | 重构 | - |
| `perf` | 性能优化 | PATCH |
| `test` | 测试相关 | - |
| `chore` | 构建/工具 | - |
| `ci` | CI 配置 | - |
| `build` | 构建系统 | - |
| `revert` | 回滚 | - |

### Scope 范围

```
feat(monitor): 添加模型健康监控
fix(memory): 修复记忆系统泄漏
docs(api): 更新 API 文档
refactor(core): 重构核心模块
```

### 提交示例

```bash
# 新功能
git commit -m "feat(monitor): 添加自动 fallback 机制

- 实现模型错误检测
- 添加备用模型链
- 集成 heartbeat 检查

Closes #123"

# Bug 修复
git commit -m "fix(memory): 修复 JSON 解析错误

处理空值情况，避免崩溃

Fixes #456"

# 破坏性变更
git commit -m "feat(api)!: 重构认证接口

BREAKING CHANGE: 认证 API 从 /auth/login 改为 /v2/auth/token"
```

---

## 🚀 发布流程

### 标准发布流程

```bash
# 1. 创建发布分支
git checkout develop
git checkout -b release/v2.1.0

# 2. 更新版本号
# 编辑版本文件，更新为 2.1.0

# 3. 更新 CHANGELOG
# 运行 changelog 生成脚本
npm run changelog

# 4. 提交变更
git add .
git commit -m "chore: 准备发布 v2.1.0"

# 5. 测试验证
npm test
npm run build

# 6. 合并到 main
git checkout main
git merge --no-ff release/v2.1.0
git tag -a v2.1.0 -m "Release v2.1.0: 模型监控系统升级"

# 7. 合并回 develop
git checkout develop
git merge --no-ff release/v2.1.0

# 8. 删除发布分支
git branch -d release/v2.1.0

# 9. 推送到 GitHub
git push origin main develop --tags
```

### 紧急热修复

```bash
# 1. 从 main 创建热修复分支
git checkout main
git checkout -b hotfix/memory-leak

# 2. 修复问题
# ... 修复代码 ...
git commit -m "fix(memory): 紧急修复内存泄漏"

# 3. 合并到 main 和 develop
git checkout main
git merge --no-ff hotfix/memory-leak
git tag -a v2.0.1 -m "Hotfix v2.0.1: 内存泄漏修复"

git checkout develop
git merge --no-ff hotfix/memory-leak

# 4. 清理并推送
git branch -d hotfix/memory-leak
git push origin main develop --tags
```

---

## 🏷️ 标签管理

### 标签命名

```
v2.1.0           # 正式版
v2.1.0-beta.1    # 测试版
v2.1.0-rc.1      # 候选版
v2.0.1-hotfix    # 热修复
```

### 创建标签

```bash
# 轻量标签
git tag v2.1.0

# 附注标签（推荐）
git tag -a v2.1.0 -m "Release v2.1.0: 模型监控系统升级

## 新功能
- 模型健康监控 v2.0
- 自动 fallback 机制
- 错误日志记录

## Bug 修复
- 修复内存泄漏
- 修复 JSON 解析错误"

# 推送标签
git push origin v2.1.0
git push origin --tags  # 推送所有标签
```

### 标签验证

```bash
# 查看标签
git tag -l "v2.*"

# 查看标签详情
git show v2.1.0

# 验证签名（如有）
git tag -v v2.1.0
```

---

## 📝 CHANGELOG 维护

### 文件格式

```markdown
# Changelog

## [2.1.0] - 2026-03-05

### ✨ 新功能
- 添加模型健康监控系统
- 实现自动 fallback 机制
- 集成 heartbeat 检查

### 🐛 Bug 修复
- 修复记忆系统内存泄漏
- 修复 JSON 解析错误

### 📚 文档
- 更新 API 文档
- 添加使用示例

### ⚡ 性能优化
- 优化数据库查询
- 减少 API 调用次数

### 🔧 技术债务
- 重构核心模块
- 更新依赖版本

---

## [2.0.1] - 2026-03-01
...
```

### 自动生成 CHANGELOG

```bash
# 使用 conventional-changelog
npm install -g conventional-changelog-cli

# 生成 changelog
conventional-changelog -p angular -i CHANGELOG.md -s -r 0

# 预览下次发布的 changelog
conventional-changelog -p angular -u
```

### 提交时更新

```bash
# 使用 commitizen
npm install -g commitizen cz-conventional-changelog
echo '{ "path": "cz-conventional-changelog" }' > ~/.czrc

# 交互式提交
cz
```

---

## 🤖 自动化策略

### GitHub Actions 工作流

```yaml
# .github/workflows/release.yml
name: Release

on:
  push:
    tags:
      - 'v*'

jobs:
  release:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'
      
      - name: Install dependencies
        run: npm ci
      
      - name: Run tests
        run: npm test
      
      - name: Build
        run: npm run build
      
      - name: Create Release
        uses: softprops/action-gh-release@v1
        with:
          generate_release_notes: true
          files: |
            dist/*.zip
            dist/*.tar.gz
      
      - name: Publish to npm
        run: npm publish
        env:
          NODE_AUTH_TOKEN: ${{ secrets.NPM_TOKEN }}
```

### 版本检查脚本

```bash
#!/bin/bash
# scripts/version-check.sh

CURRENT_VERSION=$(cat package.json | jq -r '.version')
LAST_TAG=$(git describe --tags --abbrev=0 2>/dev/null || echo "v0.0.0")

echo "当前版本：$CURRENT_VERSION"
echo "最新标签：$LAST_TAG"

# 检查版本是否递增
if [ "$CURRENT_VERSION" = "${LAST_TAG#v}" ]; then
  echo "❌ 版本未更新"
  exit 1
fi

echo "✅ 版本检查通过"
```

---

## 🔄 回滚与热修复

### 回滚策略

```bash
# 1. 找到要回滚的提交
git log --oneline

# 2. 创建回滚提交
git revert <commit-hash>

# 3. 紧急回滚（重置）
git reset --hard <previous-commit>
git push --force  # 谨慎使用！
```

### 热修复流程

```
1. 发现问题 → 创建 hotfix 分支
2. 修复问题 → 提交并测试
3. 合并到 main → 创建标签
4. 合并到 develop → 同步修复
5. 发布热修复版本
```

### 版本兼容性

```
主版本 N: 支持 N 和 N-1 两个主版本
次版本：自动升级到最新次版本
补丁版本：建议所有用户升级
```

---

## 📊 项目特定策略

### OpenClaw 本体

```
版本文件：src/config/version.ts
发布渠道：GitHub Releases + npm
更新机制：Sparkle (macOS) / Auto-updater
```

### my-dev/ 开发项目

```
版本独立：每个子项目独立版本
协调发布：与主版本协调发布
文档同步：更新 VERSION-MANAGEMENT-STRATEGY.md
```

### MindForge AI 项目

```
版本文件：mindforge/src/mindforge/__init__.py
版本格式：__version__ = "2.1.0"
发布节奏：跟随 OpenClaw 主版本
```

---

## ✅ 检查清单

### 发布前检查

- [ ] 所有测试通过
- [ ] CHANGELOG 已更新
- [ ] 版本号已更新
- [ ] 文档已同步
- [ ] 代码已审查
- [ ] 构建成功
- [ ] 标签已创建

### 发布后检查

- [ ] GitHub Release 已创建
- [ ] 包已发布（npm/pypi）
- [ ] 文档已部署
- [ ] 通知已发送
- [ ] 监控已开启

---

## 📚 参考资源

- [Semantic Versioning 2.0.0](https://semver.org/)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [Git Flow](https://nvie.com/posts/a-successful-git-branching-model/)
- [GitHub Releases](https://docs.github.com/en/repositories/releasing-projects-on-github)
- [Keep a Changelog](https://keepachangelog.com/)

---

*此文档应定期审查和更新，确保与项目实践保持一致。*
