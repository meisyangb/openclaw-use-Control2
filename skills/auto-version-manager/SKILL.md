# Auto Version Manager Skill

**版本**: v1.0.0  
**作者**: FullStack Engineer with Memory Intelligence  
**创建日期**: 2026-03-05

---

## 🎯 概述

全自动版本管理系统，提供防崩溃保护、自动回滚、安全边界等功能。

**核心目标**: 防止 AI 在自动化操作中"死亡"

---

## 🛡️ 安全特性

### 1. 三层防护

```
第一层：预防 (Prevention)
├── 健康检查
├── 提交前验证
└── 敏感文件检测

第二层：保护 (Protection)
├── 自动备份
├── 操作日志
└── 紧急停止

第三层：恢复 (Recovery)
├── 自动回滚
├── 状态恢复
└── 事故报告
```

### 2. 安全边界

| 风险等级 | 操作类型 | 保护措施 |
|---------|---------|---------|
| 🔴 极高 | 强制推送、分支删除 | 必须用户确认 |
| 🟠 高 | 发布流程、核心重构 | 自动备份 + 回滚 |
| 🟡 中 | 版本升级、合并 | 自动备份 |
| 🟢 低 | 常规提交 | 推荐备份 |

---

## 📦 安装

```bash
# 1. 安装脚本
chmod +x scripts/auto-version-manager.py
chmod +x scripts/install-hooks.sh

# 2. 安装 Git Hooks
./scripts/install-hooks.sh

# 3. 初始化配置
mkdir -p .openclaw/version-backups
```

---

## 🚀 使用方法

### 基本命令

```bash
# 健康检查
python3 scripts/auto-version-manager.py health

# 创建备份
python3 scripts/auto-version-manager.py backup

# 查看状态
python3 scripts/auto-version-manager.py status

# 列出备份
python3 scripts/auto-version-manager.py list
```

### 版本管理

```bash
# 升级版本
python3 scripts/auto-version-manager.py bump patch  # 补丁版本
python3 scripts/auto-version-manager.py bump minor  # 次版本
python3 scripts/auto-version-manager.py bump major  # 主版本

# 创建标签
python3 scripts/auto-version-manager.py tag --version 2.1.0

# 安全提交
python3 scripts/auto-version-manager.py commit -m "feat: 新功能"
```

### 自动发布

```bash
# 完整发布流程（带备份和回滚）
python3 scripts/auto-version-manager.py release --bump patch

# 不推送
python3 scripts/auto-version-manager.py release --bump minor --no-push
```

### 回滚操作

```bash
# 回滚到最新备份
python3 scripts/auto-version-manager.py rollback

# 回滚到指定备份
python3 scripts/auto-version-manager.py rollback --backup backup_20260305_170000_pre_commit
```

---

## 📋 提交策略

### Conventional Commits 格式

```
<type>(<scope>): <description>

[optional body]

[optional footer(s)]
```

### Type 说明

| Type | 含义 | 示例 |
|------|------|------|
| `feat` | 新功能 | `feat(api): 添加认证接口` |
| `fix` | Bug 修复 | `fix(memory): 修复泄漏` |
| `docs` | 文档更新 | `docs(readme): 更新说明` |
| `style` | 代码格式 | `style(css): 格式化样式` |
| `refactor` | 重构 | `refactor(core): 优化架构` |
| `perf` | 性能优化 | `perf(db): 优化查询` |
| `test` | 测试相关 | `test(unit): 添加测试` |
| `chore` | 构建/工具 | `chore(deps): 更新依赖` |

### 提交前检查清单

- [ ] 提交信息符合规范
- [ ] 无敏感文件泄露
- [ ] 文件大小合理
- [ ] 通过健康检查
- [ ] 已创建备份（重要操作）

---

## 🔄 自动回滚机制

### 触发条件

```python
triggers = [
    "commit_failed",          # 提交失败
    "test_failed",           # 测试失败
    "health_check_failed",   # 健康检查失败
    "push_failed",          # 推送失败
    "merge_conflict",       # 合并冲突
    "timeout",              # 超时
]
```

### 回滚流程

```
1. 检测错误
   ↓
2. 停止操作（设置 EMERGENCY_STOP）
   ↓
3. 选择最近的可用备份
   ↓
4. 恢复关键文件
   ↓
5. 验证恢复结果
   ↓
6. 记录回滚历史
   ↓
7. 通知用户
   ↓
8. 清理标志
```

### 手动回滚

```bash
# 查看备份列表
python3 scripts/auto-version-manager.py list

# 执行回滚
python3 scripts/auto-version-manager.py rollback --backup <备份名称>

# 验证回滚结果
python3 scripts/auto-version-manager.py health
```

---

## 🚨 紧急停止

### 启用紧急停止

```bash
# 创建紧急停止标志
touch .openclaw/EMERGENCY_STOP

# 系统将自动：
# - 禁止所有提交
# - 停止自动化操作
# - 等待人工介入
```

### 解除紧急停止

```bash
# 1. 检查问题
python3 scripts/auto-version-manager.py health

# 2. 手动修复
# ... 修复代码 ...

# 3. 删除标志
rm .openclaw/EMERGENCY_STOP

# 4. 验证恢复
python3 scripts/auto-version-manager.py health
```

---

## 📊 监控与日志

### 操作日志

位置：`.openclaw/operation-log.jsonl`

```json
{
  "timestamp": "2026-03-05T17:00:00+08:00",
  "operation": "release",
  "version": "2.1.0",
  "status": "success",
  "backup": "backup_20260305_170000_pre_release",
  "duration_ms": 5432
}
```

### 状态文件

位置：`.openclaw/version-manager-state.json`

```json
{
  "current_version": "2.1.0",
  "last_commit": "abc123...",
  "last_tag": "v2.1.0",
  "backup_count": 10,
  "rollback_history": [],
  "health_status": "healthy"
}
```

### 查看统计

```bash
# 查看最近操作
python3 scripts/auto-version-manager.py status

# 查看日志
cat .openclaw/operation-log.jsonl | tail -20

# 查看回滚历史
python3 -c "import json; print(json.dumps(json.load(open('.openclaw/version-manager-state.json'))['rollback_history'], indent=2))"
```

---

## ⚙️ 配置

### 配置文件

`.openclaw/commit-policy.json`

```json
{
  "auto_backup": {
    "enabled": true,
    "before_commit": true,
    "max_backups": 10
  },
  "auto_rollback": {
    "enabled": true,
    "cooldown_minutes": 5
  },
  "safety_mode": {
    "enabled": true,
    "confirm_destructive_operations": true
  }
}
```

### 环境变量

```bash
export AUTO_VERSION_MAX_BACKUPS=20
export AUTO_VERSION_REQUIRE_TESTS=true
export AUTO_VERSION_SAFETY_MODE=true
```

---

## 🎓 最佳实践

### 日常开发

```bash
# 开始工作前检查健康状态
python3 scripts/auto-version-manager.py health

# 频繁小步提交
python3 scripts/auto-version-manager.py commit -m "feat: 小功能"

# 定期查看日志
tail -f .openclaw/operation-log.jsonl
```

### 发布流程

```bash
# 1. 确保健康
python3 scripts/auto-version-manager.py health

# 2. 执行发布
python3 scripts/auto-version-manager.py release --bump minor

# 3. 验证结果
python3 scripts/auto-version-manager.py status
```

### 事故处理

```bash
# 1. 立即停止
python3 scripts/auto-version-manager.py rollback

# 2. 检查日志
python3 scripts/auto-version-manager.py status

# 3. 分析问题
cat .openclaw/operation-log.jsonl | grep error

# 4. 修复后恢复
rm .openclaw/EMERGENCY_STOP
```

---

## 🔧 故障排除

### 常见问题

**Q: 提交被阻止**
A: 检查 `.openclaw/EMERGENCY_STOP` 是否存在

**Q: 备份失败**
A: 检查磁盘空间和权限

**Q: 回滚失败**
A: 手动从 Git 历史恢复：`git checkout HEAD~1`

**Q: Hook 未生效**
A: 重新安装：`./scripts/install-hooks.sh`

---

## 📚 参考

- [VERSION-MANAGEMENT-STRATEGY.md](../../VERSION-MANAGEMENT-STRATEGY.md)
- [.openclaw/safety-boundaries.md](../../.openclaw/safety-boundaries.md)
- [.openclaw/commit-policy.json](../../.openclaw/commit-policy.json)

---

*此技能持续改进中，欢迎反馈和建议。*
