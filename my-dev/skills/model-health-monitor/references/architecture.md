# Model Fallback Architecture

## OpenClaw Built-in Fallback

### Core Components

1. **model-fallback.ts** - Main fallback logic
   - `runWithModelFallback()` - Wraps API calls with fallback
   - `resolveFallbackCandidates()` - Gets fallback chain
   - Error classification and handling

2. **failover-error.ts** - Error handling
   - `FailoverError` class
   - `coerceToFailoverError()` - Normalize errors
   - `resolveFailoverReasonFromError()` - Classify errors

3. **pi-embedded-helpers/errors.ts** - Error detection
   - `isBillingErrorMessage()` - Detect billing errors
   - `isRateLimitErrorMessage()` - Detect rate limits
   - `isAuthErrorMessage()` - Detect auth errors

### Fallback Flow

```
API Call → Error? → Classify → Fallback?
   ↓                      ↓
 Success            Yes → Try next model
   ↓                      ↓
 Return            No → Throw error
```

### Error Classification

```typescript
type FailoverReason =
  | "billing"       // 402 - Quota exhausted
  | "rate_limit"    // 429 - Temporary limit
  | "auth"          // 401 - Invalid credentials
  | "auth_permanent"// 403 - Permanently blocked
  | "timeout"       // 502/503/504 - Service issue
  | "format"        // 400 - Request format error
  | "model_not_found" // 404 - Model doesn't exist
  | "session_expired" // 410 - Session gone
  | "unknown";      // Other errors
```

### Cooldown Management

- Rate limits: Model-specific cooldown
- Auth errors: Provider-wide cooldown
- Billing errors: Provider-wide cooldown

## Best Practices from Major AI Projects

### LangChain
- Fallback chains with LLM classes
- Retry with exponential backoff
- Error callbacks for monitoring

### AutoGPT
- Error recovery loops
- Graceful degradation
- State persistence

### Semantic Kernel
- Plugin-based model switching
- Skill-based error handling
- Context preservation

## Implementation Patterns

### Pattern 1: Wrap and Retry
```python
def with_fallback(func, fallbacks):
    for model in fallbacks:
        try:
            return func(model)
        except FallbackError:
            continue
    raise AllModelsFailedError()
```

### Pattern 2: Proactive Monitoring
```python
def check_health():
    errors = scan_recent_errors()
    for error in errors:
        if error.type in CRITICAL_ERRORS:
            switch_model(error.model)
```

### Pattern 3: State-based Recovery
```python
def get_available_model():
    for model in fallbacks:
        if not is_in_cooldown(model):
            return model
    return fallbacks[0]  # Reset if all in cooldown
```