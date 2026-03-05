# Model Error Patterns Reference

## Error Classification Matrix

| Error Type | HTTP Status | Patterns | Action | Cooldown |
|------------|-------------|----------|--------|----------|
| Billing | 402 | `billing`, `insufficient credit`, `payment required`, `credit balance`, `quota exceeded`, `run out of credit`, `余额不足`, `额度不足` | Immediate switch | 30 min |
| Auth | 401/403 | `unauthorized`, `invalid api key`, `认证失败`, `密钥无效` | Immediate switch | 15 min |
| Rate Limit | 429 | `rate limit`, `too many requests`, `throttl`, `请求过于频繁` | Wait & retry | 5 min |
| Timeout | 502/503/504 | `timeout`, `timed out`, `超时`, `服务不可用` | Log only | 1 min |
| Not Found | 404 | `model not found`, `does not exist` | Skip model | - |
| Bad Request | 400 | `invalid`, `bad request` | Log only | - |

## Regex Patterns

```python
ERROR_PATTERNS = {
    "billing": [
        r"billing", r"insufficient.*credit", r"payment.*required",
        r"credit.*balance", r"quota.*exceeded", r"402\b",
        r"run out of credit", r"余额不足", r"额度不足", r"欠费"
    ],
    "rate_limit": [
        r"rate.?limit", r"too.*many.*request", r"429\b",
        r"throttl", r"请求过于频繁", r"频率限制"
    ],
    "auth": [
        r"unauthorized", r"invalid.*api.*key", r"401\b",
        r"403\b", r"认证失败", r"密钥无效"
    ],
    "timeout": [
        r"timeout", r"timed.?out", r"502\b", r"503\b", r"504\b",
        r"超时", r"服务不可用"
    ]
}
```

## Error Detection in Session Logs

Session logs are JSONL files at:
```
~/.openclaw/agents/main/sessions/*.jsonl
```

Each line is a JSON object with:
```json
{
  "type": "message",
  "message": {
    "role": "toolResult",
    "content": [
      {
        "type": "text",
        "text": "error message here"
      }
    ]
  }
}
```

## Provider-Specific Errors

### OpenAI
- `insufficient_quota` - Billing
- `rate_limit_exceeded` - Rate limit
- `invalid_api_key` - Auth

### Anthropic
- `billing_error` - Billing
- `rate_limit_error` - Rate limit
- `authentication_error` - Auth

### ZAI (智谱)
- `余额不足` - Billing
- `请求过于频繁` - Rate limit
- `认证失败` - Auth

### Alibaba (通义千问)
- `额度不足` - Billing
- `频率限制` - Rate limit
- `密钥无效` - Auth

## Recovery Strategies

### Billing Error Recovery
1. Mark model as unavailable
2. Switch to next fallback
3. Wait 30 minutes before retry
4. User should check billing dashboard

### Rate Limit Recovery
1. Log the error
2. Wait 5 minutes
3. Retry same model
4. Switch if persistent

### Auth Error Recovery
1. Mark provider as unavailable
2. Switch to different provider
3. Wait 15 minutes
4. User should check API keys

## Monitoring Best Practices

1. **Scan recent sessions** - Only last 3-5 sessions
2. **Limit line depth** - Only last 20 lines per session
3. **Deduplicate errors** - Track by timestamp
4. **Persist state** - Save to JSON file
5. **Log rotations** - Keep last 100 entries