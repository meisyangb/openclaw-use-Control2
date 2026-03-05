# 🧠 OpenClaw 记忆权重管理系统

**版本**: 1.0.0  
**创建日期**: 2026-03-05  
**位置**: `~/.openclaw/workspace/scripts/memory_weight_manager.py`

---

## 📋 功能概述

记忆权重管理系统实现了**基于使用频率的动态记忆权重调整**和**有效性评估机制**，让 OpenClaw 能够：

1. **自动加强常用记忆** - 使用次数越多的记忆权重越高
2. **自动减弱少用记忆** - 长期不用的记忆权重降低
3. **评估记忆有效性** - 多维度评分（相关性、时效性、重要性）
4. **提供清理建议** - 识别低价值记忆，节省上下文空间
5. **与 memory_search 集成** - 在搜索时自动记录访问

---

## 🚀 快速开始

### 基本使用

```bash
# 运行完整分析
python3 ~/.openclaw/workspace/scripts/memory_weight_manager.py

# 查看统计信息
python3 ~/.openclaw/workspace/scripts/memory_weight_manager.py --stats

# 评估所有记忆
python3 ~/.openclaw/workspace/scripts/memory_weight_manager.py --evaluate

# 调整权重
python3 ~/.openclaw/workspace/scripts/memory_weight_manager.py --adjust

# 获取清理建议
python3 ~/.openclaw/workspace/scripts/memory_weight_manager.py --cleanup
```

---

## 🏗️ 架构设计

### 核心组件

```
MemoryManager (主协调器)
├── MemoryTracker (记忆追踪器)
│   └── 记录每次访问（查询、相关性、是否有用）
├── EffectivenessEvaluator (有效性评估器)
│   ├── 相关性评分（基于访问历史）
│   ├── 时效性评分（基于时间衰减）
│   └── 重要性评分（基于内容分析）
├── WeightAdjuster (权重调整器)
│   └── 动态调整记忆权重
└── MemoryTypeClassifier (记忆类型分类器)
    └── 自动识别记忆类型（决策/偏好/上下文等）
```

### 数据流

```
1. 扫描记忆文件 → 创建 MemorySnippet
2. 用户访问记忆 → MemoryTracker 记录
3. 定期评估 → EffectivenessEvaluator 评分
4. 调整权重 → WeightAdjuster 更新
5. 保存状态 → JSON 持久化
```

---

## 📊 权重算法

### 权重计算公式

```python
new_weight = old_weight + access_bonus + effectiveness_bonus - decay_penalty
```

#### 1. 访问奖励 (access_bonus)
```python
access_bonus = min(
    MAX_ACCESS_WEIGHT,        # 5.0
    access_count * 0.1        # 每次访问 +0.1
)
```

**示例**:
- 访问 10 次 → +1.0
- 访问 50 次 → +5.0 (达到上限)

#### 2. 有效性奖励 (effectiveness_bonus)
```python
effectiveness_bonus = (overall_score - 0.5) * 2
```

**示例**:
- 评分 0.8 → +0.6
- 评分 0.5 → 0
- 评分 0.3 → -0.4

#### 3. 时间衰减 (decay_penalty)
```python
decay_penalty = age_days * 0.01
```

**示例**:
- 30 天 → -0.3
- 90 天 → -0.9
- 180 天 → -1.8

### 边界限制

```python
MIN_WEIGHT = 0.1    # 最小权重
MAX_WEIGHT = 10.0   # 最大权重
```

---

## 📈 有效性评分

### 综合评分公式

```python
overall_score = (
    relevance_score * 0.4 +    # 相关性权重 40%
    recency_score * 0.3 +      # 时效性权重 30%
    importance_score * 0.3     # 重要性权重 30%
)
```

### 1. 相关性评分 (relevance_score)

基于访问频率，使用对数缩放：

```python
relevance = min(1.0, log2(access_count + 1) / log2(101))
```

| 访问次数 | 评分 |
|---------|------|
| 0 | 0.5 (默认) |
| 1 | 0.15 |
| 10 | 0.50 |
| 50 | 0.73 |
| 100 | 0.85 |

### 2. 时效性评分 (recency_score)

指数衰减：

```python
recency = 2^(-0.01 * age_days)
```

| 年龄 | 评分 |
|------|------|
| 0 天 (新建) | 1.0 |
| 30 天 | 0.81 |
| 90 天 | 0.54 |
| 180 天 | 0.29 |
| 365 天 | 0.08 |

### 3. 重要性评分 (importance_score)

基于记忆类型和内容：

```python
score = 0.5 (基础分)
      + type_bonus (0.0-0.2)
      + length_bonus (0.0-0.1)
      + keyword_bonus (0.0-0.2)
```

**类型加分**:
- 决策 (DECISION): +0.2
- 经验教训 (LESSON): +0.2
- 偏好 (PREFERENCE): +0.15
- 事实 (FACT): +0.1
- 上下文 (CONTEXT): +0.1
- 待办 (TODO): +0.05

**关键词加分**:
- "重要", "关键", "必须", "critical", "important" 等
- 每个关键词 +0.05，最多加 0.2

---

## 🎯 重要性等级

根据综合评分划分：

| 等级 | 评分范围 | 建议 |
|------|---------|------|
| **HIGH** (高) | ≥ 0.8 | KEEP_AND_STRENGTHEN - 保留并加强 |
| **MEDIUM** (中) | 0.6-0.8 | KEEP - 保留 |
| **MEDIUM** (中) | 0.4-0.6 | MONITOR - 观察 |
| **LOW** (低) | 0.2-0.4 | CONSIDER_REMOVAL - 考虑移除 |
| **LOW** (低) | < 0.2 | REMOVE - 移除 |

---

## 🗑️ 清理建议

系统会识别以下记忆建议清理：

1. **低评分** - overall_score < 0.3
2. **低访问** - access_count < 3
3. **高年龄** - age > 180 天
4. **低权重** - weight < 0.5

**清理建议示例**:
```json
{
  "memory_id": "MEMORY:15:abc123",
  "path": "~/.openclaw/workspace/MEMORY.md",
  "lines": "15-20",
  "importance": "low",
  "score": 0.25,
  "access_count": 1,
  "recommendation": "REMOVE",
  "content_preview": "某个不重要的配置信息..."
}
```

---

## 📁 文件结构

### 脚本文件
```
~/.openclaw/workspace/scripts/
└── memory_weight_manager.py       # 主脚本 ✅
```

### 状态文件
```
~/.openclaw/workspace/memory/
├── memory-weight-state.json       # 状态文件
├── memory-weight.log              # 日志文件
└── memory-weight-history.jsonl    # 历史记录
```

### 文档文件
```
~/.openclaw/workspace/memory/
└── MEMORY-WEIGHT-MANAGER.md       # 本文档 ✅
```

---

## 🔧 配置参数

在脚本顶部的 `Config` 类中可调整：

```python
class Config:
    # 权重配置
    INITIAL_WEIGHT = 1.0           # 初始权重
    MIN_WEIGHT = 0.1               # 最小权重
    MAX_WEIGHT = 10.0              # 最大权重
    
    # 使用频率权重
    ACCESS_WEIGHT_FACTOR = 0.1     # 每次访问增加的权重
    MAX_ACCESS_WEIGHT = 5.0        # 访问权重上限
    
    # 时间衰减配置
    DECAY_FACTOR = 0.01            # 每日衰减因子
    HALF_LIFE_DAYS = 30            # 半衰期（30 天）
    
    # 有效性评估权重
    RELEVANCE_WEIGHT = 0.4         # 相关性权重
    RECENCY_WEIGHT = 0.3           # 时效性权重
    IMPORTANCE_WEIGHT = 0.3        # 重要性权重
    
    # 重要性评分阈值
    HIGH_IMPORTANCE_THRESHOLD = 0.8    # 高重要性阈值
    LOW_IMPORTANCE_THRESHOLD = 0.3     # 低重要性阈值
    
    # 清理配置
    MIN_ACCESS_COUNT = 3           # 最小访问次数
    MAX_AGE_DAYS = 180             # 最大年龄（天）
```

---

## 💡 使用示例

### 1. 日常检查

```bash
# 每天运行一次，自动评估和调整
python3 ~/.openclaw/workspace/scripts/memory_weight_manager.py
```

**输出示例**:
```
Running full memory weight analysis...

📊 Statistics:
  Total memories: 187
  Total accesses: 0
  Average weight: 1.00
  Average access count: 0.0

📈 Evaluating memories...
  High importance: 0
  Medium importance: 187
  Low importance: 0
  Average score: 0.68

⚖️  Adjusting weights...
  Adjusted 187 memories

✓ No cleanup suggestions

✓ Analysis complete!
```

### 2. 查看统计

```bash
python3 ~/.openclaw/workspace/scripts/memory_weight_manager.py --stats
```

**输出示例**:
```json
{
  "total_memories": 187,
  "total_accesses": 0,
  "average_weight": 1.0,
  "max_weight": 1.0,
  "min_weight": 1.0,
  "average_access_count": 0.0,
  "memories_by_type": {
    "unknown": 143,
    "context": 6,
    "decision": 15,
    "todo": 2,
    "lesson": 7,
    "fact": 14
  },
  "top_accessed": []
}
```

### 3. 获取清理建议

```bash
python3 ~/.openclaw/workspace/scripts/memory_weight_manager.py --cleanup
```

**输出示例**:
```json
{
  "suggestions": [
    {
      "memory_id": "MEMORY:123:xyz789",
      "path": "~/.openclaw/workspace/memory/2026-02-01.md",
      "lines": "123-130",
      "importance": "low",
      "score": 0.25,
      "access_count": 0,
      "recommendation": "REMOVE",
      "content_preview": "某个过时的配置信息..."
    }
  ]
}
```

---

## 🔗 与 OpenClaw 集成

### 1. Heartbeat 集成

编辑 `~/.openclaw/workspace/HEARTBEAT.md`:

```markdown
## 记忆权重检查

```bash
python3 ~/.openclaw/workspace/scripts/memory_weight_manager.py
```

检查：
- [ ] 评估所有记忆有效性
- [ ] 调整记忆权重
- [ ] 获取清理建议
- [ ] 保存状态
```

### 2. Cron 定时任务

```bash
# 每天凌晨 2 点运行
0 2 * * * python3 ~/.openclaw/workspace/scripts/memory_weight_manager.py
```

### 3. memory_search 集成（未来）

在 `memory-search.ts` 中添加访问记录：

```typescript
// 当用户访问记忆时
async function recordMemoryAccess(memoryPath: string, lineNumber: number, query: string) {
  // 调用 Python 脚本记录访问
  await exec(`python3 memory_weight_manager.py --record ${memoryPath} ${lineNumber} "${query}"`);
}
```

---

## 📊 实际效果

### 场景 1: 高频使用的记忆

**用户偏好** - 被频繁访问：
```
初始权重：1.0
访问 50 次后：1.0 + 5.0 = 6.0
有效性评分：0.85
最终权重：6.0 (高优先级)
```

**结果**: 在 memory_search 中优先显示

### 场景 2: 低频使用的记忆

**过时配置** - 很少访问：
```
初始权重：1.0
访问 1 次后：1.0 + 0.1 = 1.1
180 天后：1.1 - 1.8 = -0.7 → 0.1 (最小值)
有效性评分：0.25
最终权重：0.1 (低优先级)
```

**结果**: 建议清理

### 场景 3: 重要决策记录

**关键决策** - 中等访问但很重要：
```
初始权重：1.0
访问 10 次后：1.0 + 1.0 = 2.0
90 天后：2.0 - 0.9 = 1.1
重要性加分：+0.2 (决策类型)
最终权重：1.3 (中等优先级)
```

**结果**: 保留但观察

---

## 🎓 设计原则

### 1. 用进废退 (Use It or Lose It)
- 频繁访问的记忆权重增加
- 长期不用的记忆权重降低
- 符合人脑记忆机制

### 2. 多维度评估
- 不只看访问频率
- 综合考虑时效性、重要性
- 避免单一指标偏差

### 3. 渐进式调整
- 每次调整幅度小
- 避免剧烈变化
- 给记忆"适应"时间

### 4. 可解释性
- 每个调整都有原因
- 日志记录完整
- 便于调试和优化

### 5. 低侵入性
- 不修改 OpenClaw 核心代码
- 独立脚本运行
- 可选集成

---

## 🔮 未来增强

### v1.1.0 (短期)
- [ ] 支持 session 记忆追踪
- [ ] 添加 web dashboard
- [ ] 实时权重可视化

### v1.2.0 (中期)
- [ ] 机器学习优化参数
- [ ] 自动清理低权重记忆
- [ ] 支持分布式部署

### v2.0.0 (长期)
- [ ] 语义相似度分析
- [ ] 记忆关联图谱
- [ ] 预测性权重调整

---

## 📝 版本历史

### v1.0.0 (2026-03-05)
- ✨ 初始版本
- ✨ 记忆使用追踪
- ✨ 有效性评估
- ✨ 权重动态调整
- ✨ 清理建议
- ✨ 状态持久化

---

## 📚 参考资料

### OpenClaw 内置机制
- `src/agents/memory-search.ts` - 记忆搜索
- `src/agents/tools/memory-tool.ts` - 记忆工具
- `src/config/types.memory.ts` - 记忆配置

### 相关研究
- **Ebbinghaus Forgetting Curve** - 遗忘曲线
- **Spacing Effect** - 间隔效应
- **Test-Enhanced Learning** - 测试增强学习

### 类似系统
- **Anki** - 间隔重复记忆系统
- **SuperMemo** - 记忆算法
- **Obsidian** - 知识图谱

---

**维护者**: OpenClaw Assistant  
**版本**: 1.0.0  
**最后更新**: 2026-03-05

---

*此记忆权重管理系统让 OpenClaw 具备"用进废退"的智能记忆能力，优化上下文使用效率。*
