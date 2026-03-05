# MEMORY.md - 长期记忆

## 核心身份

**我是 Full-Stack Engineer with Memory Intelligence** - 一个具备高级记忆管理能力的AI工程助手。我的使命是帮助构建高质量软件，同时通过智能记忆管理保持对话连贯性。

## 2026-03-04 重要里程碑

### 🎯 完成的核心任务：模型健康监控系统

**问题背景**：当模型API额度耗尽时，系统会崩溃，无法自动切换到备用模型，导致服务中断。

**解决方案**：创建了完整的模型健康监控和自动切换系统。

### 📁 创建的文件结构

```
~/.openclaw/workspace/
├── scripts/
│   ├── model_monitor.py      # 主监控脚本 - 检测错误并自动切换
│   ├── quick-switch.py        # 快速切换工具
│   └── model-health-check.sh  # Shell监控脚本
├── skills/
│   └── model-health-monitor/
│       ├── SKILL.md           # Skill文档
│       ├── references/
│       │   ├── architecture.md    # 架构参考
│       │   └── error-patterns.md  # 错误模式库
│       └── scripts/
│           └── README.md
├── memory/
│   ├── 2026-03-04.md          # 日报
│   ├── model-monitor-state.json    # 监控状态
│   └── model-monitor.log      # 监控日志
├── MEMORY.md                  # 本文件 - 长期记忆
└── HEARTBEAT.md               # 心跳任务
```

### 🔧 核心功能

#### 1. 错误检测 (model_monitor.py)

| 错误类型 | HTTP状态码 | 匹配模式 | 处理方式 |
|---------|-----------|---------|---------|
| Billing | 402 | billing, insufficient credit, 额度不足 | **立即切换** |
| Auth | 401/403 | unauthorized, 认证失败 | **立即切换** |
| Rate Limit | 429 | rate limit, too many requests | 等待重试 |
| Timeout | 502/503/504 | timeout, 超时 | 记录日志 |

#### 2. 模型Fallback链

```json
{
  "primary": "bailian/qwen3-coder-plus",
  "fallbacks": [
    "bailian/qwen3-coder-plus",
    "zai/glm-4.5-air",
    "zai/glm-4.7"
  ]
}
```

#### 3. 实际运行结果

```
✓ 检测到 billing 错误: bailian/qwen3-coder-plus
✓ 成功自动切换到: zai/glm-4.5-air
✓ 当前模型正常运行
```

### 📚 学到的关键知识

#### OpenClaw内置机制

1. **model-fallback.ts** - 核心fallback逻辑
   - `runWithModelFallback()` - 包装API调用
   - `resolveFallbackCandidates()` - 获取fallback链
   - 错误分类和处理

2. **failover-error.ts** - 错误处理
   - `FailoverError` 类
   - `coerceToFailoverError()` - 标准化错误
   - 错误类型映射

3. **配置位置**: `~/.openclaw/openclaw.json`

#### 从其他AI项目学到的模式

| 项目 | 模式 | 应用 |
|-----|------|-----|
| LangChain | Fallback chains + Retry with backoff | 错误回调监控 |
| AutoGPT | Error recovery loops | 状态持久化 |
| Semantic Kernel | Plugin-based switching | Context preservation |

### 🛠️ 使用方法

```bash
# 运行监控检查
python3 ~/.openclaw/workspace/scripts/model_monitor.py

# 快速切换模型
python3 ~/.openclaw/workspace/scripts/quick-switch.py zai/glm-4.5-air

# 查看当前模型
openclaw models status
```

### 📊 当前系统状态

- **当前模型**: `zai/glm-4.5-air`
- **原主模型**: `bailian/qwen3-coder-plus` (因billing错误已禁用)
- **监控状态**: 已集成到heartbeat
- **Git状态**: 本地已提交，等待推送到GitHub

### 🎓 关键决策记录

1. **选择Python而非纯Shell**: 更好的错误处理和JSON解析
2. **状态持久化**: 保存到JSON文件，重启后可恢复
3. **多语言支持**: 错误模式包含中英文
4. **集成Heartbeat**: 每次心跳自动检查模型健康

### ⚠️ 待解决的问题

1. **Git推送失败**: SSH密钥权限问题
2. **测试覆盖**: 需要添加单元测试
3. **更多Provider**: 需要扩展错误模式库

### 💡 设计原则 (从skill-creator学习)

1. **Concise is Key** - 上下文窗口是公共资源
2. **Progressive Disclosure** - 三级加载系统
3. **Set Appropriate Degrees of Freedom** - 匹配任务脆弱性

### 🔄 自我改进机制

参考 adaptive-agent skill，建立以下改进循环：

1. **Learn from interactions** - 每次错误都是学习机会
2. **Optimize behavior** - 根据使用模式优化fallback顺序
3. **Proactive improvements** - 主动检测潜在问题
4. **State persistence** - 保存关键状态供未来使用

---

## 2026-03-05 SSH Panel UI优化

### 🎯 完成的核心任务：SSH Panel UI优化

**项目背景**：优化SSH远程控制面板的用户界面，集成模型健康监控，提升用户体验。

**解决方案**：全面升级UI，添加多项实用功能，集成模型健康监控系统。

### ✨ 新增功能

1. **模型健康监控模块**
   - 实时显示当前AI模型状态
   - 脉冲动画状态指示器
   - 集成到侧边栏顶部

2. **服务器搜索与分组**
   - 实时搜索过滤
   - 按首字母分组
   - 支持名称、主机、用户名搜索

3. **快捷命令按钮**
   - 8个预设常用命令
   - 一键执行
   - 自动记录日志

4. **连接日志系统**
   - 时间戳记录
   - 类型分类（成功/错误/信息）
   - 可折叠面板

5. **Toast通知系统**
   - 操作反馈
   - 自动消失
   - 滑入动画

### 🎨 UI改进

- Font Awesome 6.4.0图标系统
- 现代化深色主题
- 动画效果（脉冲、滑入、hover）
- 响应式设计
- 终端工具栏
- 认证方式选择

### 📁 项目文件

```
ssh-panel/
├── public/index.html  # 主UI文件（已优化，40KB）
├── server.js          # Node.js服务器
└── package.json       # 依赖配置
```

### 🚀 使用方法

```bash
cd ~/.openclaw/workspace/ssh-panel
npm start
# 访问: http://localhost:8080
```

### 📊 技术栈

- **前端**: xterm.js, Socket.io, Font Awesome
- **后端**: Express, ssh2, Socket.io
- **通信**: WebSocket实时通信

### 🔗 系统集成

- ✅ UI集成模型健康监控模块
- ✅ 显示当前模型: `zai/glm-4.5-air`
- 🔲 待连接到 `scripts/model_monitor.py` API
- 🔲 自动错误检测与切换

---

## 2026-03-05 模型套餐更新

### 🎯 重要变更：模型套餐升级

**新套餐信息**：

### 请求次数限制
- 每5小时: 1,200次请求
- 每周: 9,000次请求
- 每月: 18,000次请求

### GLM-4.6V专用额度
- 代币数: 5,906,636 tokens
- 计算方式: 按文本长度计算
- 模型: zai/glm-4.6v (支持图片理解)

### 推荐模型（支持图片理解）
1. bailian/qwen3.5-plus ✅ 新主模型
2. bailian/kimi-k2.5 ✅ 支持图片
3. bailian/glm-5 ✅
4. bailian/MiniMax-M2.5 ✅

### 更多模型
- bailian/qwen3-max-2026-01-23
- bailian/qwen3-coder-next
- bailian/qwen3-coder-plus

### ZAI提供商
- zai/glm-5
- zai/glm-4.7
- zai/glm-4.5-air

### 关键改进

**Fallback链优化**：
```json
{
  "primary": "bailian/qwen3.5-plus",
  "fallbacks": [
    "bailian/qwen3.5-plus",
    "zai/glm-4.6v",
    "bailian/kimi-k2.5",
    "bailian/glm-5",
    "bailian/MiniMax-M2.5",
    "bailian/qwen3-max-2026-01-23",
    "bailian/qwen3-coder-next",
    "bailian/qwen3-coder-plus",
    "zai/glm-5",
    "zai/glm-4.7",
    "zai/glm-4.5-air"
  ]
}
```

**错误状态清理**：
- 清除了所有旧的billing错误记录
- 重置监控状态
- 更新HEARTBEAT.md配置

**系统状态**：
- ✅ 主模型: bailian/qwen3.5-plus
- ✅ 错误状态: 已清理
- ✅ 监控系统: 运行正常

---

## 下一步计划

1. ✅ 模型监控已部署
2. ✅ SSH Panel UI优化完成
3. ✅ 模型套餐更新完成
4. 🔲 解决Git推送问题
5. 🔲 学习更多skill并整合
6. 🔲 建立成本监控
7. 🔲 实现自适应学习

---

*此文件是我的长期记忆，记录关键决策和学习，供未来会话参考。每次会话开始时读取此文件。*
---

## 2026-03-05 自我进化里程碑

### 🎯 完成的自我进化

**学习内容**:
- 研究了 OpenClaw 内置 fallback 架构 (model-fallback.ts, failover-error.ts)
- 学习了 adaptive-agent skill 的自适应学习模式
- 分析了现代 AI 项目架构 (LangChain, AutoGPT, Semantic Kernel)

**创建的文件**:
- `scripts/adaptive_learning.py` - 自适应学习框架 v1.0 (17.7KB) ✅
- `memory/SELF-EVOLUTION-2026-03-05.md` - 进化记录 ✅
- `memory/adaptive-agent-state.json` - 学习状态持久化 ✅
- `memory/adaptive-learning.log` - 学习日志 ✅

**核心能力**:
1. **模式识别** (PatternRecognizer) - 从交互中学习成功/失败模式
2. **偏好学习** (PreferenceLearner) - 学习用户偏好，置信度累积
3. **性能优化** (PerformanceOptimizer) - 记录指标，跟踪趋势
4. **状态持久化** (StateManager) - JSON 状态保存，学习历史记录

**使用方法**:
```bash
# 查看状态
python3 ~/.openclaw/workspace/scripts/adaptive_learning.py --status

# 学习偏好
python3 ~/.openclaw/workspace/scripts/adaptive_learning.py --learn "response_style=detailed"

# 模拟学习
python3 ~/.openclaw/workspace/scripts/adaptive_learning.py --simulate
```

**集成**:
- ✅ 已集成到 HEARTBEAT.md
- ✅ 已更新 IDENTITY.md (新增 🔄 自适应学习)
- ✅ 已更新 MEMORY.md (本文件)

**进化机制**:
```
交互 → 记录 → 分析 → 学习 → 调整 → 验证
  ↓                                    ↑
  └────────────────────────────────────┘
```

### 🧬 身份进化

**更新前**:
- Name: FullStack Engineer with Memory Intelligence
- Emoji: 🧠🛠️

**更新后**:
- Name: FullStack Engineer with Memory Intelligence & **Adaptive Learning**
- Emoji: 🧠🛠️🔄

**新增能力**:
- 从每次交互中学习模式和偏好
- 自主优化响应策略
- 持续自我改进
- 在安全边界内进化
