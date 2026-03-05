# Version Manager Skill

**版本**: v1.0  
**作者**: FullStack Engineer with Memory Intelligence  
**创建日期**: 2026-03-05

---

## 📋 描述

版本管理自动化技能，提供语义化版本控制、CHANGELOG 生成、发布流程自动化等功能。

---

## 🎯 功能

### 1. 版本升级

```bash
# 升级补丁版本
./scripts/version-bump.sh patch

# 升级次版本
./scripts/version-bump.sh minor

# 升级主版本
./scripts/version-bump.sh major

# 预发布版本
./scripts/version-bump.sh prerelease
```

### 2. CHANGELOG 生成

```bash
# 生成完整 CHANGELOG
./scripts/generate-changelog.sh

# 生成指定版本
./scripts/generate-changelog.sh v2.1.0
```

### 3. 版本检查

```bash
# 检查当前版本
npm version

# 检查 Git 标签
git tag -l "v*"

# 版本对比
./scripts/version-check.sh
```

---

## 📁 文件结构

```
openclaw-main/
├── scripts/
│   ├── version-bump.sh      # 版本升级脚本
│   ├── version-check.sh     # 版本检查脚本
│   └── generate-changelog.sh # CHANGELOG 生成
├── skills/
│   └── version-manager/
│       ├── SKILL.md         # 本文档
│       └── references/
│           └── semver.md    # 语义化版本参考
├── .github/
│   └── RELEASE-TEMPLATE.md  # Release 模板
├── CHANGELOG.md             # 变更日志
└── VERSION-MANAGEMENT-STRATEGY.md # 版本管理策略
```

---

## 🔧 配置

### package.json

```json
{
  "version": "2.1.0",
  "scripts": {
    "version:patch": "./scripts/version-bump.sh patch",
    "version:minor": "./scripts/version-bump.sh minor",
    "version:major": "./scripts/version-bump.sh major",
    "changelog": "./scripts/generate-changelog.sh",
    "release": "npm run version:patch && npm run changelog && git push --follow-tags"
  }
}
```

### Git Hooks

```bash
# .husky/pre-commit
#!/bin/sh
npm run version-check

# .husky/pre-push
#!/bin/sh
npm test
```

---

## 📖 使用示例

### 发布新版本

```bash
# 1. 运行测试
npm test

# 2. 升级版本
npm run version:minor

# 3. 生成 CHANGELOG
npm run changelog

# 4. 提交并推送
git add .
git commit -m "chore: 发布 v2.1.0"
git push origin main --tags

# 5. 创建 GitHub Release
# 访问：https://github.com/meisyangb/openclaw-use-Control2/releases/new
```

### 紧急热修复

```bash
# 1. 创建热修复分支
git checkout -b hotfix/critical-bug main

# 2. 修复并提交
git commit -m "fix: 修复关键 bug"

# 3. 升级补丁版本
npm run version:patch

# 4. 合并并推送
git checkout main
git merge hotfix/critical-bug
git push origin main --tags
```

---

## 🎓 最佳实践

### 1. 版本命名

- ✅ `v2.1.0` - 标准语义化版本
- ✅ `v2.1.0-beta.1` - 预发布版本
- ❌ `2.1` - 缺少补丁号
- ❌ `v2.1.0.1` - 格式错误

### 2. 提交信息

- ✅ `feat(api): 添加用户认证`
- ✅ `fix(memory): 修复内存泄漏`
- ❌ `更新代码` - 太模糊
- ❌ `修复 bug` - 缺少 scope

### 3. 发布频率

- **补丁版本**: 随时（bug 修复）
- **次版本**: 每 2-4 周（新功能）
- **主版本**: 按需（破坏性变更）

---

## 🔍 故障排除

### 问题：版本升级失败

```bash
# 检查 Git 状态
git status

# 检查是否有未提交的变更
git diff

# 解决冲突后重试
```

### 问题：CHANGELOG 格式错误

```bash
# 检查提交信息格式
git log --oneline -10

# 手动编辑 CHANGELOG.md
nano CHANGELOG.md
```

### 问题：标签冲突

```bash
# 删除本地标签
git tag -d v2.1.0

# 删除远程标签
git push origin :refs/tags/v2.1.0

# 重新创建
git tag -a v2.1.0 -m "Release v2.1.0"
```

---

## 📚 参考资源

- [语义化版本 2.0.0](https://semver.org/lang/zh-CN/)
- [Conventional Commits](https://www.conventionalcommits.org/zh-hans/)
- [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)
- [GitHub Releases](https://docs.github.com/en/repositories/releasing-projects-on-github)

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request 来改进此技能！

---

*最后更新：2026-03-05*
