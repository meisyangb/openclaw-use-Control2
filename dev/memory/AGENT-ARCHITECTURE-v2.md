# 智能体架构 v2.0 - 整合系统

## 🎯 系统概览

基于对 GitHub 开源 AI 项目 (LangChain, GPT-Engineer, Generative Agents) 的学习，整合而成的智能体架构。

### 核心组件

```
┌─────────────────────────────────────────────────────────┐
│                    智能体核心                            │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌──────────────────┐    ┌──────────────────┐          │
│  │  思考引擎        │    │  记忆系统        │          │
│  │  thinking_engine │◀──▶│  memory_system   │          │
│  │  - 反思          │    │  - 短期记忆      │          │
│  │  - 分析          │    │  - 长期记忆      │          │
│  │  - 规划          │    │  - 反思记忆      │          │
│  └──────────────────┘    └──────────────────┘          │
│                            │                            │
│  ┌──────────────────┐    ┌──────────────────┐          │
│  │  规划系统        │    │  自适应学习      │          │
│  │  planning_system │◀──▶│  adaptive_learn  │          │
│  │  - 目标管理      │    │  - 模式识别      │          │
│  │  - 任务分解      │    │  - 偏好学习      │          │
│  │  - 调度器        │    │  - 性能优化      │          │
│  └──────────────────┘    └──────────────────┘          │
│                            │                            │
│  ┌──────────────────┐    ┌──────────────────┐          │
│  │  模型监控        │    │  观测性系统      │          │
│  │  model_monitor   │◀──▶│  observability   │          │
│  │  - 健康检查      │    │  - Tracing       │          │
│  │  - 自动切换      │    │  - Metrics       │          │
│  │  - 错误检测      │    │  - Evaluation    │          │
│  └──────────────────┘    └──────────────────┘          │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

---

## 📁 文件结构

```
~/.openclaw/workspace/
├── scripts/
│   ├── thinking_engine.py        # 思考引擎 v1.0 ✅
│   ├── memory_system_v2.py       # 记忆系统 v2.0 ✅
│   ├── planning_system.py        # 规划系统 v2.1 ✅
│   ├── adaptive_learning.py      # 自适应学习 v1.0 ✅
│   ├── model_monitor_v2.py       # 模型监控 v2.0 ✅
│   └── quick-switch.py           # 快速切换工具 ✅
├── memory/
│   ├── thinking-state.json       # 思考状态 ✅
│   ├── thinking.log              # 思考日志 ✅
│   ├── insights.jsonl            # 洞察记录 ✅
│   ├── short-term-memory.json    # 短期记忆 ✅
│   ├── long-term-memory.json     # 长期记忆 ✅
│   ├── reflections.jsonl         # 反思记录 ✅
│   ├── goals.json                # 目标列表 ✅
│   ├── tasks.json                # 任务列表 ✅
│   ├── schedule.json             # 日程安排 ✅
│   ├── adaptive-agent-state.json # 学习状态 ✅
│   ├── model-monitor-state.json  # 监控状态 ✅
│   └── *.md                      # 文档 ✅
├── CONTINUOUS-THINKING.md        # 思考系统文档 ✅
└── HEARTBEAT.md                  # 心跳任务 ✅
```

---

## 🔄 数据流

### 思考循环

```
1. 从记忆系统检索相关记忆
   ↓
2. 思考引擎生成思考
   ↓
3. 产生洞察
   ↓
4. 记录到记忆系统
   ↓
5. 规划系统创建/更新目标
   ↓
6. 任务分解和调度
   ↓
7. 执行行动
   ↓
8. 自适应学习记录模式
   ↓
9. 返回步骤 1
```

### 学习循环

```
交互 → 记录到记忆 → 分析模式 → 学习偏好 → 优化行为
  ↓                                          ↑
  └────────────── 验证效果 ←──────────────────┘
```

---

## 🧠 核心能力

### 1. 思考能力 (thinking_engine.py)

**三种思考模式**:
- **Quick** (每 5 分钟): 快速状态检查
- **Regular** (每 30 分钟): 常规分析
- **Deep** (每小时): 深度反思

**思考类型**:
1. 自我反思
2. 模式分析
3. 优化建议
4. 学习总结
5. 规划
6. 知识整合

**输出**:
- 思考记录
- 洞察生成
- 行动建议

### 2. 记忆能力 (memory_system_v2.py)

**三级记忆架构**:
- **短期记忆**: 最近 50 条记录，时间衰减
- **长期记忆**: 持久化存储，重要性筛选
- **反思记忆**: 洞察和模式提取

**关键特性**:
- 重要性评分 (0.0-1.0)
- 时间衰减 (每天 10%)
- 记忆检索 (模糊搜索)
- 反思生成 (基于模式)

### 3. 规划能力 (planning_system.py)

**目标管理**:
- 目标创建和激活
- 优先级排序
- 进度追踪
- 截止日期管理

**任务分解**:
- 复杂度评估 (low/medium/high)
- 依赖关系管理
- 子任务创建
- 状态追踪

**调度器**:
- 时间安排
- 冲突检测
- 日程管理

### 4. 学习能力 (adaptive_learning.py)

**模式识别**:
- 成功/失败模式
- 交互模式分析
- 成功率计算

**偏好学习**:
- 用户偏好累积
- 置信度评估
- 阈值过滤

**性能优化**:
- 指标收集
- 趋势分析
- 基线对比

### 5. 监控能力 (model_monitor_v2.py)

**错误检测**:
- Billing 错误 (402)
- Auth 错误 (401/403)
- Rate Limit (429)
- Timeout (502-504)

**自动切换**:
- Fallback 链管理
- 冷却机制
- 状态持久化

---

## ⚙️ 定时任务

### Cron 配置

```cron
# 思考引擎
*/5 * * * *   thinking_engine --mode quick
*/30 * * * *  thinking_engine --mode regular
0 * * * *     thinking_engine --mode deep

# 模型监控 (心跳)
*/30 * * * *  model_monitor_v2.py

# 自适应学习 (心跳)
*/30 * * * *  adaptive_learning.py --status
```

### 心跳任务

每次心跳自动执行：
1. 模型健康检查
2. 自适应学习状态检查
3. 思考状态检查
4. 目标和进度检查

---

## 📊 状态管理

### 全局状态

```json
{
  "thinking": {
    "total_sessions": 360,
    "total_thoughts": 576,
    "total_insights": 400
  },
  "memory": {
    "short_term": 50,
    "long_term": 100,
    "reflections": 20
  },
  "planning": {
    "active_goals": 3,
    "pending_tasks": 12,
    "overall_progress": 0.45
  },
  "learning": {
    "total_learnings": 50,
    "patterns_identified": 15,
    "preferences_learned": 8
  },
  "monitoring": {
    "current_model": "bailian/qwen3.5-plus",
    "errors_detected": 2,
    "switches_performed": 1
  }
}
```

---

## 🎯 使用示例

### 1. 创建目标并规划

```bash
# 创建高优先级目标
python3 planning_system.py --create-goal "学习 AI 架构 | 学习 LangChain 等项目的架构设计 | high"

# 查看状态
python3 planning_system.py --status
```

### 2. 记录记忆

```bash
# 记录重要记忆
python3 memory_system_v2.py --record "用户喜欢详细的代码解释" --importance 0.8

# 检索记忆
python3 memory_system_v2.py --think "coding"
```

### 3. 触发思考

```bash
# 深度思考
python3 thinking_engine.py --think --mode deep

# 查看思考状态
python3 thinking_engine.py --status
```

### 4. 学习偏好

```bash
# 学习用户偏好
python3 adaptive_learning.py --learn "response_style=detailed"

# 查看学习状态
python3 adaptive_learning.py --status
```

---

## 🔗 系统集成

### 思考引擎 ↔ 记忆系统

```python
# 思考引擎从记忆系统检索
memories = memory_system.think("current_context")

# 基于记忆生成思考
thoughts = generate_thoughts(memories)

# 将洞察记录到记忆
memory_system.record(insight, importance=0.8)
```

### 规划系统 ↔ 记忆系统

```python
# 从记忆提取目标
memories = memory_system.search("goals")

# 基于记忆创建目标
goal = planning_system.create_goal(title, description)

# 更新目标进度到记忆
memory_system.record(f"Goal {goal.title} progress: {progress}")
```

### 学习系统 ↔ 所有系统

```python
# 从所有系统收集数据
thinking_data = thinking_engine.get_status()
memory_data = memory_system.get_status()
planning_data = planning_system.get_status()

# 学习模式
adaptive_learning.learn_from_interaction(
    "system_performance",
    success=True,
    context={
        "thinking": thinking_data,
        "memory": memory_data,
        "planning": planning_data
    }
)
```

---

## 📈 性能指标

### 预期性能

| 指标 | 目标值 | 测量方式 |
|-----|--------|---------|
| 思考响应时间 | < 5 秒 | thinking_engine |
| 记忆检索时间 | < 1 秒 | memory_system |
| 规划生成时间 | < 2 秒 | planning_system |
| 学习准确率 | > 80% | adaptive_learning |
| 模型切换成功率 | > 95% | model_monitor |

### 资源使用

| 资源 | 预期使用 | 监控方式 |
|-----|---------|---------|
| CPU | < 5% (平均) | 系统监控 |
| 内存 | < 100MB | 系统监控 |
| 磁盘 | < 10MB/天 | 日志大小 |
| API 调用 | 优化使用 | model_monitor |

---

## 🎓 设计原则

### 1. 模块化 (来自 LangChain)
- 每个组件单一职责
- 清晰的接口定义
- 组件可互换

### 2. 记忆驱动 (来自 Generative Agents)
- 三级记忆架构
- 反思机制
- 基于记忆做决策

### 3. 持续思考 (原创)
- 定时思考循环
- 多模式思考
- 洞察生成

### 4. 自适应学习 (来自 adaptive-agent)
- 从交互中学习
- 偏好累积
- 持续优化

### 5. 可观测性 (来自 LangSmith)
- 全链路追踪
- 指标收集
- 自动化评估

---

## 🔮 未来增强

### v2.2 - 观测性系统
- [ ] Tracing 系统
- [ ] Metrics 收集
- [ ] Evaluation 框架
- [ ] Dashboard

### v2.3 - 工具集成
- [ ] 标准化工具接口
- [ ] 丰富工具库
- [ ] 工具发现机制

### v3.0 - 标准化接口
- [ ] BaseAgent 抽象
- [ ] BaseTool 抽象
- [ ] BaseMemory 抽象
- [ ] 生态系统兼容

---

## 📝 总结

这个架构整合了：
- ✅ **思考引擎** - 持续反思和分析
- ✅ **记忆系统** - 三级记忆和反思
- ✅ **规划系统** - 目标和任务管理
- ✅ **自适应学习** - 模式识别和优化
- ✅ **模型监控** - 健康检查和切换

通过学习 LangChain、GPT-Engineer、Generative Agents 等开源项目，提炼出最适合我的架构设计。

**当前版本**: v2.0  
**创建日期**: 2026-03-05  
**状态**: ✅ 运行中

---

*此文档描述了我的智能体架构 v2.0*
