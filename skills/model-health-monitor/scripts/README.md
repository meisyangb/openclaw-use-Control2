# Model Health Monitor - Scripts

This directory contains monitoring scripts for model health management.

## Scripts

### model_monitor.py
Main monitoring script with:
- Session log scanning
- Error classification (billing, rate_limit, auth, timeout)
- Automatic model switching
- State persistence

### quick-switch.py
Quick model switching utility:
```bash
# Auto-switch to next available
python3 quick-switch.py

# Switch to specific model
python3 quick-switch.py zai/glm-4.5-air
```

### model-health-check.sh
Shell monitoring for cron/watch:
```bash
# Single check
./model-health-check.sh

# Watch mode (60s interval)
./model-health-check.sh --watch 60
```

## Error Patterns

The scripts detect these error patterns:

### Billing Errors (402)
- `billing`, `insufficient credit`, `payment required`
- `credit balance`, `quota exceeded`, `402`
- `run out of credit`
- 余额不足, 额度不足, 欠费

### Rate Limit Errors (429)
- `rate limit`, `too many requests`, `429`
- `throttl`
- 请求过于频繁, 频率限制

### Auth Errors (401/403)
- `unauthorized`, `invalid api key`
- `401`, `403`
- 认证失败, 密钥无效

### Timeout Errors (502/503/504)
- `timeout`, `timed out`
- `502`, `503`, `504`
- 超时, 服务不可用

## State Management

Scripts maintain state in:
- `~/.openclaw/workspace/memory/model-monitor-state.json`
- `~/.openclaw/workspace/memory/model-monitor.log`