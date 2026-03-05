# HEARTBEAT.md

# 心跳任务清单 - 每次心跳自动执行

## 1. 模型健康检查 (优先级: 最高)

运行监控脚本检测模型错误：
```bash
python3 ~/.openclaw/workspace/scripts/model_monitor.py
```

检查项目：
- [ ] 是否有billing错误（额度耗尽）
- [ ] 是否有rate limit错误
- [ ] 是否有auth错误
- [ ] 自动切换到备用模型

## 2. 自适应学习状态检查 (新增)

运行自适应学习框架：
```bash
python3 ~/.openclaw/workspace/scripts/adaptive_learning.py --status
```

检查项目：
- [ ] 查看学习进度
- [ ] 识别成功模式
- [ ] 应用优化建议
- [ ] 更新用户偏好

## 3. 状态文件检查

- `memory/model-monitor-state.json` - 监控状态
- `memory/model-monitor.log` - 错误日志
- `memory/adaptive-agent-state.json` - 自适应学习状态 (新增)
- `memory/adaptive-learning.log` - 学习日志 (新增)

## 3. 当前模型配置 (2026-03-05 更新)

### 推荐模型（支持图片理解）
- bailian/qwen3.5-plus ✅ 主模型
- bailian/kimi-k2.5 ✅ 支持图片
- bailian/glm-5 ✅
- bailian/MiniMax-M2.5 ✅

### 更多模型
- bailian/qwen3-max-2026-01-23
- bailian/qwen3-coder-next
- bailian/qwen3-coder-plus

### ZAI提供商
- zai/glm-5
- zai/glm-4.7
- zai/glm-4.5-air

## 4. Fallback模型优先级

1. bailian/qwen3.5-plus (主模型) ✅
2. zai/glm-4.6v (专用代币额度: 5,906,636 tokens，支持图片)
3. bailian/kimi-k2.5 (支持图片)
4. bailian/glm-5
5. bailian/MiniMax-M2.5
6. bailian/qwen3-max-2026-01-23
7. bailian/qwen3-coder-next
8. bailian/qwen3-coder-plus
9. zai/glm-5
10. zai/glm-4.7
11. zai/glm-4.5-air

## 5. 套餐限制

### 请求次数限制
- 每5小时: 1,200次请求
- 每周: 9,000次请求
- 每月: 18,000次请求

### GLM-4.6V专用额度
- 代币数: 5,906,636 tokens
- 计算方式: 按文本长度计算
- 模型: zai/glm-4.6v (支持图片理解)

## 6. 错误处理策略

| 错误类型 | 动作 | 冷却时间 |
|---------|------|---------|
| Billing (402) | 立即切换 | 30分钟 |
| Auth (401/403) | 立即切换 | 15分钟 |
| Rate Limit (429) | 等待重试 | 5分钟 |
| Timeout (502-504) | 记录日志 | 1分钟 |

## 7. 重要提醒

- 每次token都很珍贵 - 最大化利用每次请求
- 避免频繁请求 - 使用智能策略
- 保持写日志的习惯
- 记住从错误中学习
- Git提交: 本地已提交，待推送GitHub