# Skill Helper - 快速参考

## 🚀 常用命令

```bash
# 查看状态
python3 ~/.openclaw/workspace/scripts/skill_helper.py --status

# 扫描已安装的 skills
python3 ~/.openclaw/workspace/scripts/skill_helper.py --scan

# 推荐 skills
python3 ~/.openclaw/workspace/scripts/skill_helper.py --recommend <类型>
# 类型：research, coding, memory, documentation, github

# 规划学习
python3 ~/.openclaw/workspace/scripts/skill_helper.py --plan "主题 | 目标"

# 下载 skills
python3 ~/.openclaw/workspace/scripts/skill_helper.py --download "skill1,skill2"
```

## 📋 学习场景

### 研究开源项目
```bash
skill_helper.py --plan "GitHub 项目 | 学习架构设计"
# 推荐：github, web_fetch, adaptive-agent, skill-creator
```

### 编码任务
```bash
skill_helper.py --recommend coding
# 推荐：coding-agent, ai-model-manager
```

### 文档编写
```bash
skill_helper.py --recommend documentation
# 推荐：basic-system, skill-creator
```

## 📊 当前状态

- **总 Skills**: 57 个
- **已安装**: 57 个 ✅
- **缺失**: 0 个 ✅

## 🔧 核心 Skills

| Skill | 用途 | 优先级 |
|-------|------|--------|
| adaptive-agent | 自学习 | 🔴 High |
| browser-automation | 网页交互 | 🔴 High |
| coding-agent | 编码 | 🔴 High |
| model-health-monitor | 监控 | 🔴 Critical |
| skill-creator | 创建技能 | 🟡 Medium |
| github | GitHub 集成 | 🔴 High |

---

*完整文档：LEARNING-TOOLS-SYSTEM.md*
