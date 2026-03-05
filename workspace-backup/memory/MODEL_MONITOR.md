# Model Monitor Setup

## 已创建的监控工具

### 1. model_monitor.py
主要监控脚本，用于检测模型错误并自动切换。

**功能：**
- 检查最近的API调用错误
- 识别billing、rate_limit、auth错误
- 自动切换到备用模型
- 记录错误历史

**使用方法：**
```bash
python3 ~/.openclaw/workspace/scripts/model_monitor.py
```

### 2. quick-switch.py
快速模型切换工具。

**使用方法：**
```bash
# 自动切换到下一个可用模型
python3 ~/.openclaw/workspace/scripts/quick-switch.py

# 切换到指定模型
python3 ~/.openclaw/workspace/scripts/quick-switch.py zai/glm-4.5-air
```

### 3. model-health-check.sh
Shell版本的监控脚本，适用于cron或手动执行。

**使用方法：**
```bash
# 单次检查
~/.openclaw/workspace/scripts/model-health-check.sh

# 持续监控（每60秒）
~/.openclaw/workspace/scripts/model-health-check.sh --watch 60
```

## 错误检测机制

系统会检测以下错误类型并自动处理：

| 错误类型 | 匹配模式 | 处理方式 |
|---------|---------|---------|
| billing | billing, insufficient credit, 402, 额度不足 | 立即切换模型 |
| rate_limit | rate limit, 429, too many requests | 记录错误，等待恢复 |
| auth | unauthorized, 401, 403, 认证失败 | 立即切换模型 |
| timeout | timeout, 502, 503, 504 | 记录错误 |

## Fallback模型顺序

配置文件中已设置以下fallback顺序：

1. `bailian/qwen3-coder-plus` (主模型)
2. `zai/glm-4.5-air`
3. `zai/glm-4.7`

## 集成到Heartbeat

HEARTBEAT.md 已更新，每次heartbeat时会自动检查模型健康状态。

## 状态文件

- **状态存储**: `~/.openclaw/workspace/memory/model-monitor-state.json`
- **日志文件**: `~/.openclaw/workspace/memory/model-monitor.log`

## 现有系统机制

OpenClaw已内置模型fallback机制：

- **配置位置**: `~/.openclaw/openclaw.json` 中的 `agents.defaults.model.fallbacks`
- **核心代码**: `/root/oepnclaw/openclaw-main/src/agents/model-fallback.ts`
- **错误处理**: `/root/oepnclaw/openclaw-main/src/agents/failover-error.ts`

当API调用失败时，系统会自动尝试fallback列表中的模型。