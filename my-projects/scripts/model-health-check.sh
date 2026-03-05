#!/bin/bash
# OpenClaw Model Health Check and Auto-Fallback Script
# 检查模型状态并在需要时自动切换到备用模型

set -e

CONFIG_FILE="${HOME}/.openclaw/openclaw.json"
STATE_FILE="${HOME}/.openclaw/workspace/memory/model-health-state.json"
LOG_FILE="${HOME}/.openclaw/workspace/memory/model-health.log"

# 确保目录存在
mkdir -p "$(dirname "$STATE_FILE")"
mkdir -p "$(dirname "$LOG_FILE")"

log() {
    echo "[$(date -Iseconds)] $1" | tee -a "$LOG_FILE"
}

# 检查openclaw命令是否可用
if ! command -v openclaw &> /dev/null; then
    log "ERROR: openclaw command not found"
    exit 1
fi

# 获取当前模型状态
get_current_model() {
    local model=$(openclaw models status --plain 2>/dev/null | head -1 | awk '{print $1}')
    echo "${model:-bailian/qwen3-coder-plus}"
}

# 检查最近的API错误
check_recent_errors() {
    local sessions_dir="${HOME}/.openclaw/agents/main/sessions"
    
    if [ ! -d "$sessions_dir" ]; then
        return 0
    fi
    
    # 获取最新的会话文件
    local latest_session=$(ls -t "$sessions_dir"/*.jsonl 2>/dev/null | head -1)
    
    if [ -z "$latest_session" ]; then
        return 0
    fi
    
    # 检查最后10行中的错误
    local errors=$(tail -10 "$latest_session" 2>/dev/null | grep -iE "billing|insufficient|quota|402|credit.*balance|run out of" || true)
    
    if [ -n "$errors" ]; then
        log "WARNING: Billing/quota error detected in recent session"
        echo "billing_error"
        return 1
    fi
    
    # 检查rate limit错误
    errors=$(tail -10 "$latest_session" 2>/dev/null | grep -iE "rate.?limit|429|too.*many.*request|throttl" || true)
    
    if [ -n "$errors" ]; then
        log "WARNING: Rate limit detected"
        echo "rate_limit"
        return 1
    fi
    
    return 0
}

# 切换到备用模型
switch_to_fallback() {
    local reason="$1"
    local current_model=$(get_current_model)
    
    # 从配置获取fallback列表
    local fallbacks=("bailian/qwen3-coder-plus" "zai/glm-4.5-air" "zai/glm-4.7" "bailian/qwen3.5-plus")
    
    for model in "${fallbacks[@]}"; do
        if [ "$model" != "$current_model" ]; then
            log "Attempting to switch from $current_model to $model (reason: $reason)"
            
            if openclaw models set "$model" 2>&1 | tee -a "$LOG_FILE"; then
                log "SUCCESS: Switched to $model"
                
                # 记录状态
                echo "{\"timestamp\":\"$(date -Iseconds)\",\"previous_model\":\"$current_model\",\"current_model\":\"$model\",\"reason\":\"$reason\"}" > "$STATE_FILE"
                
                return 0
            else
                log "FAILED: Could not switch to $model"
            fi
        fi
    done
    
    log "ERROR: All fallback models failed"
    return 1
}

# 主函数
main() {
    log "Starting model health check..."
    
    local current_model=$(get_current_model)
    log "Current model: $current_model"
    
    # 检查错误
    local error_type=$(check_recent_errors)
    
    if [ -n "$error_type" ]; then
        log "Detected error type: $error_type"
        
        case "$error_type" in
            billing_error)
                switch_to_fallback "billing_error"
                ;;
            rate_limit)
                # 对于rate limit，等待一段时间后重试
                log "Rate limit detected, waiting 60 seconds..."
                sleep 60
                ;;
        esac
    else
        log "No critical errors detected"
    fi
    
    # 检查模型状态
    if openclaw models status --check 2>&1 | tee -a "$LOG_FILE"; then
        log "Model status check passed"
    else
        log "Model status check failed, attempting fallback..."
        switch_to_fallback "status_check_failed"
    fi
}

# 支持watch模式
if [ "$1" = "--watch" ] || [ "$1" = "-w" ]; then
    interval="${2:-60}"
    log "Starting watch mode (interval: ${interval}s)"
    
    while true; do
        main
        sleep "$interval"
    done
else
    main
fi