# CONTINUOUS-THINKING.md - 持续思考系统

## 🚀 快速参考

### 系统状态

```bash
# 查看 crontab
crontab -l | grep thinking

# 查看思考状态
cat ~/.openclaw/workspace/memory/thinking-state.json | python3 -m json.tool

# 查看最新洞察
tail -5 ~/.openclaw/workspace/memory/insights.jsonl | python3 -m json.tool

# 查看思考日志
tail -20 ~/.openclaw/workspace/memory/thinking.log
```

### 手动触发

```bash
# 快速思考 (5 分钟级别)
python3 ~/.openclaw/workspace/scripts/thinking_engine.py --think --mode quick

# 常规思考 (30 分钟级别)
python3 ~/.openclaw/workspace/scripts/thinking_engine.py --think --mode regular

# 深度思考 (小时级别)
python3 ~/.openclaw/workspace/scripts/thinking_engine.py --think --mode deep
```

### 日志位置

```bash
/tmp/thinking-quick.log     # 快速思考日志
/tmp/thinking-regular.log   # 常规思考日志
/tmp/thinking-deep.log      # 深度思考日志
```

---

## 📊 当前配置

| 模式 | 频率 | Cron 表达式 |
|-----|------|------------|
| Quick | 每 5 分钟 | `*/5 * * * *` |
| Regular | 每 30 分钟 | `*/30 * * * *` |
| Deep | 每小时 | `0 * * * *` |

---

## 🧠 思考什么？

### 6 种思考类型

1. **自我反思** - "我做得怎么样？"
2. **模式分析** - "有什么规律？"
3. **优化建议** - "如何改进？"
4. **学习总结** - "学到了什么？"
5. **规划** - "下一步做什么？"
6. **知识整合** - "如何整合新知识？"

---

## 📁 相关文件

- `scripts/thinking_engine.py` - 思考引擎
- `scripts/adaptive_learning.py` - 自适应学习
- `memory/thinking-state.json` - 状态
- `memory/thinking.log` - 日志
- `memory/insights.jsonl` - 洞察
- `memory/CONTINUOUS-THINKING-SYSTEM.md` - 详细文档

---

## ✅ 系统状态

- [x] 思考引擎已创建
- [x] Cron 任务已配置
- [x] 状态文件已生成
- [x] 日志系统已启用
- [x] 集成自适应学习
- [x] 集成模型监控

**系统**: 🟢 运行中

---

*创建于 2026-03-05*
