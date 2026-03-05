# 学习工具系统 v1.0

## 🎯 目标

为学习提供最佳工具支持：
- 根据学习任务选择最合适的 skill 组合
- 自动下载缺失的 skills
- 管理 skill 的使用和配置

---

## 📁 文件结构

```
~/.openclaw/workspace/
├── scripts/
│   └── skill_helper.py         # Skill 学习助手 (17.2KB) ✅
├── memory/
│   ├── skill-registry.json     # Skill 注册表 ✅
│   └── skill-usage.log         # Skill 使用日志 ✅
└── LEARNING-TOOLS-SYSTEM.md    # 本文件 ✅
```

---

## 🛠️ 核心功能

### 1. Skill 推荐

根据学习任务类型推荐最合适的 skills：

```python
# 预定义映射
LEARNING_SKILLS = {
    "research": ["web_search", "web_fetch", "browser-automation"],
    "coding": ["coding-agent", "ai-model-manager"],
    "memory": ["adaptive-agent", "model-health-monitor"],
    "documentation": ["basic-system", "skill-creator"],
    "github": ["github", "gh-issues"],
}
```

### 2. Skill 组合

根据学习目标智能选择 skill 组合：

```bash
# 规划学习
python3 skill_helper.py --plan "主题 | 目标"

# 示例
python3 skill_helper.py --plan "GitHub AI 项目学习 | 学习 LangChain 等项目的架构设计"
```

**输出**:
```
📋 学习规划:
   主题：GitHub AI 项目学习
   必需 skills: ['github', 'gh-issues', 'web_fetch', 'web_search', 'adaptive-agent']
   可选 skills: ['browser-automation', 'model-health-monitor']
```

### 3. 自动下载

检测并下载缺失的 skills：

```bash
# 下载指定 skills
python3 skill_helper.py --download "skill1,skill2,skill3"

# 示例
python3 skill_helper.py --download "web_search,web_fetch"
```

### 4. 状态管理

查看所有 skills 的状态：

```bash
# 查看状态
python3 skill_helper.py --status

# 扫描已安装的 skills
python3 skill_helper.py --scan
```

---

## 📊 当前 Skill 状态

### 已安装 Skills (57 个)

**核心 Skills**:
- ✅ adaptive-agent - 自学习和自适应
- ✅ browser-automation - 浏览器自动化
- ✅ coding-agent - 编码助手
- ✅ skill-creator - Skill 创建
- ✅ github - GitHub 集成
- ✅ model-health-monitor - 模型监控
- ✅ ai-model-manager - AI 模型管理

**其他 Skills**:
- 1password, apple-notes, apple-reminders, bear-notes, blogwatcher, blucli, bluebubbles, camsnap, canvas, clawhub, discord, eightctl, gemini, gh-issues, gifgrep, gog, goplaces, healthcheck, himalaya, imsg, mcporter, notion, openhue, oracle, peekaboo, songsee, weather, nano-banana-pro, openai-image-gen, openai-whisper-api, wacli, 等

### 缺失 Skills

- 🔲 web_search (需要 Brave API key)
- 🔲 web_fetch (需要配置)

---

## 🎯 使用场景

### 场景 1: 开始新的学习任务

```bash
# 1. 规划学习
python3 skill_helper.py --plan "主题 | 目标"

# 2. 检查技能状态
python3 skill_helper.py --status

# 3. 下载缺失的 skills
python3 skill_helper.py --download "missing_skill1,missing_skill2"

# 4. 开始学习
# (使用推荐的 skills 组合)
```

### 场景 2: 推荐 Skills

```bash
# 研究任务
python3 skill_helper.py --recommend research

# 编码任务
python3 skill_helper.py --recommend coding

# 文档任务
python3 skill_helper.py --recommend documentation
```

### 场景 3: 查看使用情况

```bash
# 查看状态（包含最常用的 skills）
python3 skill_helper.py --status
```

---

## 🔧 配置

### Skill 元数据

在 `skill_helper.py` 中配置：

```python
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
    # ... 更多 skills
}
```

### 学习技能映射

```python
LEARNING_SKILLS = {
    "research": ["web_search", "web_fetch", "browser-automation"],
    "coding": ["coding-agent", "ai-model-manager"],
    "memory": ["adaptive-agent", "model-health-monitor"],
    "documentation": ["basic-system", "skill-creator"],
    "github": ["github", "gh-issues"],
    "communication": ["discord", "message"],
}
```

---

## 📈 Skill 使用统计

### 记录使用

每次使用 skill 都会自动记录：

```python
# 在代码中
skill_manager.log_usage("adaptive-agent", "learning GitHub projects")
```

### 查看统计

```bash
python3 skill_helper.py --status
```

**输出**:
```json
{
  "most_used": [
    {"name": "adaptive-agent", "usage_count": 15},
    {"name": "model-health-monitor", "usage_count": 10},
    {"name": "thinking_engine", "usage_count": 8}
  ]
}
```

---

## 🔄 工作流程

### 完整学习流程

```
1. 定义学习目标
   ↓
2. 规划学习 (skill_helper --plan)
   ↓
3. 检查技能可用性
   ↓
4. 下载缺失技能 (skill_helper --download)
   ↓
5. 使用技能组合学习
   ↓
6. 记录技能使用
   ↓
7. 评估学习效果
   ↓
8. 优化技能组合
```

### 自动技能选择

```python
# 伪代码
def learn(topic, goal):
    # 1. 获取技能组合
    combination = skill_manager.get_skill_combination(goal)
    
    # 2. 检查可用性
    missing = check_availability(combination)
    
    # 3. 下载缺失的
    if missing:
        download(missing)
    
    # 4. 使用技能学习
    for skill in combination["required_skills"]:
        use_skill(skill, topic)
    
    # 5. 记录
    log_usage(combination["required_skills"])
```

---

## 🎓 最佳实践

### 1. 总是先规划

```bash
# ❌ 不好 - 直接使用技能
use adaptive-agent

# ✅ 好 - 先规划
skill_helper --plan "主题 | 目标"
# 然后使用推荐的技能组合
```

### 2. 选择最合适的组合

```
学习任务 → 技能组合
   ↓
研究     → web_search + web_fetch + browser-automation
编码     → coding-agent + ai-model-manager
架构分析 → adaptive-agent + skill-creator
文档     → basic-system + skill-creator
```

### 3. 保持技能更新

```bash
# 定期扫描
skill_helper --scan

# 查看状态
skill_helper --status
```

### 4. 记录使用情况

```python
# 在代码中记录
skill_manager.log_usage(skill_name, context)
```

---

## 🚀 未来增强

### v1.1.0 (短期)
- [ ] 自动从 GitHub 下载 skills
- [ ] Skill 版本管理
- [ ] 依赖关系检查

### v1.2.0 (中期)
- [ ] Skill 性能监控
- [ ] 自动优化技能组合
- [ ] 学习路径推荐

### v2.0.0 (长期)
- [ ] AI 驱动的技能选择
- [ ] 技能市场
- [ ] 社区贡献技能

---

## 📝 总结

**Skill 学习助手** 提供：

- 🎯 **智能推荐** - 根据任务推荐最佳技能
- 📦 **自动下载** - 检测并下载缺失技能
- 📊 **使用统计** - 追踪技能使用情况
- 🔧 **状态管理** - 管理所有技能的状态

**目标**: 让每次学习都使用最合适的工具组合。

---

*创建日期：2026-03-05*  
*版本：v1.0*  
*状态：✅ 运行中*
