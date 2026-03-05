#!/usr/bin/env node
/**
 * OpenClaw Model Health Monitor
 * 
 * 监控模型使用情况、检测额度耗尽、自动切换到备用模型
 * 用法：node model-health-monitor.js [--watch] [--interval-ms 30000]
 */

import { spawn, exec } from 'child_process';
import { promisify } from 'util';
import fs from 'fs';
import path from 'path';

const execAsync = promisify(exec);

const CONFIG_PATH = process.env.OPENCLAW_CONFIG || path.join(process.env.HOME || '/root', '.openclaw', 'openclaw.json');
const MEMORY_PATH = path.join(process.env.HOME || '/root', '.openclaw', 'workspace', 'memory');
const HEARTBEAT_STATE_PATH = path.join(MEMORY_PATH, 'model-health-state.json');

// 模型优先级配置
const MODEL_PRIORITY = {
  primary: 'bailian/qwen3-coder-plus',
  fallbacks: [
    'bailian/qwen3-coder-plus',
    'zai/glm-4.5-air',
    'zai/glm-4.7',
    'bailian/qwen3.5-plus',
    'bailian/glm-5'
  ]
};

// 错误类型映射
const ERROR_PATTERNS = {
  billing: [
    /billing/i,
    /insufficient.*credit/i,
    /payment.*required/i,
    /credit.*balance/i,
    /quota.*exceeded/i,
    /402\b/,
    /run out of credit/i,
    /余额不足/,
    /额度不足/,
    /欠费/
  ],
  rate_limit: [
    /rate.?limit/i,
    /too.*many.*request/i,
    /429\b/,
    /throttl/i,
    /请求过于频繁/,
    /频率限制/
  ],
  auth: [
    /unauthorized/i,
    /invalid.*api.*key/i,
    /401\b/,
    /403\b/,
    /认证失败/,
    /密钥无效/
  ],
  timeout: [
    /timeout/i,
    /timed.*out/i,
    /502\b/,
    /503\b/,
    /504\b/,
    /超时/,
    /服务不可用/
  ]
};

// 模型健康状态
class ModelHealthMonitor {
  constructor() {
    this.modelStatus = new Map();
    this.errorHistory = [];
    this.lastCheck = null;
    this.currentModel = MODEL_PRIORITY.primary;
  }

  /**
   * 加载配置
   */
  loadConfig() {
    try {
      if (fs.existsSync(CONFIG_PATH)) {
        const config = JSON.parse(fs.readFileSync(CONFIG_PATH, 'utf8'));
        if (config.agents?.defaults?.model?.primary) {
          this.currentModel = config.agents.defaults.model.primary;
        }
        if (config.agents?.defaults?.model?.fallbacks) {
          MODEL_PRIORITY.fallbacks = config.agents.defaults.model.fallbacks;
        }
        return config;
      }
    } catch (error) {
      console.error('Failed to load config:', error.message);
    }
    return null;
  }

  /**
   * 保存状态到文件
   */
  saveState() {
    try {
      if (!fs.existsSync(MEMORY_PATH)) {
        fs.mkdirSync(MEMORY_PATH, { recursive: true });
      }
      const state = {
        timestamp: new Date().toISOString(),
        currentModel: this.currentModel,
        modelStatus: Object.fromEntries(this.modelStatus),
        errorHistory: this.errorHistory.slice(-10),
        lastCheck: this.lastCheck
      };
      fs.writeFileSync(HEARTBEAT_STATE_PATH, JSON.stringify(state, null, 2));
    } catch (error) {
      console.error('Failed to save state:', error.message);
    }
  }

  /**
   * 加载历史状态
   */
  loadState() {
    try {
      if (fs.existsSync(HEARTBEAT_STATE_PATH)) {
        const state = JSON.parse(fs.readFileSync(HEARTBEAT_STATE_PATH, 'utf8'));
        this.currentModel = state.currentModel || MODEL_PRIORITY.primary;
        this.modelStatus = new Map(Object.entries(state.modelStatus || {}));
        this.errorHistory = state.errorHistory || [];
        this.lastCheck = state.lastCheck;
        return true;
      }
    } catch (error) {
      console.error('Failed to load state:', error.message);
    }
    return false;
  }

  /**
   * 检测错误类型
   */
  classifyError(errorMessage) {
    if (!errorMessage) return null;
    
    for (const [type, patterns] of Object.entries(ERROR_PATTERNS)) {
      for (const pattern of patterns) {
        if (pattern.test(errorMessage)) {
          return type;
        }
      }
    }
    return 'unknown';
  }

  /**
   * 记录错误
   */
  recordError(model, error, type) {
    const entry = {
      timestamp: new Date().toISOString(),
      model,
      error: error.substring(0, 200),
      type
    };
    this.errorHistory.push(entry);
    this.modelStatus.set(model, {
      status: 'error',
      errorType: type,
      lastError: entry.timestamp,
      errorCount: (this.modelStatus.get(model)?.errorCount || 0) + 1
    });
    
    // 如果是billing错误，标记模型为不可用
    if (type === 'billing') {
      this.modelStatus.set(model, {
        ...this.modelStatus.get(model),
        available: false,
        reason: 'billing_error'
      });
    }
    
    console.error(`[${entry.timestamp}] Model ${model} error (${type}): ${entry.error}`);
    this.saveState();
  }

  /**
   * 获取下一个可用的模型
   */
  getNextAvailableModel() {
    // 首先尝试fallback列表
    for (const model of MODEL_PRIORITY.fallbacks) {
      const status = this.modelStatus.get(model);
      if (!status || status.available !== false) {
        return model;
      }
    }
    
    // 如果所有fallback都不可用，重置状态并返回第一个
    console.warn('All models marked as unavailable, resetting status...');
    this.modelStatus.clear();
    return MODEL_PRIORITY.fallbacks[0];
  }

  /**
   * 切换到备用模型
   */
  async switchToFallback(reason) {
    const nextModel = this.getNextAvailableModel();
    
    if (nextModel === this.currentModel) {
      console.log('No alternative model available, staying with current model');
      return false;
    }

    console.log(`Switching from ${this.currentModel} to ${nextModel} (reason: ${reason})`);
    
    try {
      // 使用openclaw CLI切换模型
      const { stdout, stderr } = await execAsync(`openclaw models set ${nextModel}`);
      
      if (stderr && !stderr.includes('warning')) {
        throw new Error(stderr);
      }
      
      this.currentModel = nextModel;
      this.saveState();
      
      console.log(`✓ Successfully switched to ${nextModel}`);
      return true;
    } catch (error) {
      console.error(`Failed to switch model: ${error.message}`);
      return false;
    }
  }

  /**
   * 检查模型状态（通过openclaw status）
   */
  async checkModelStatus() {
    try {
      const { stdout } = await execAsync('openclaw status --json 2>/dev/null || openclaw status');
      this.lastCheck = new Date().toISOString();
      
      // 解析输出并提取有用信息
      if (stdout.includes('billing') || stdout.includes('quota') || stdout.includes('credit')) {
        console.log('Billing/quota information detected in status');
      }
      
      return true;
    } catch (error) {
      console.error('Failed to check model status:', error.message);
      return false;
    }
  }

  /**
   * 监控会话日志中的错误
   */
  async monitorSessionErrors() {
    const agentDir = process.env.OPENCLAW_AGENT_DIR || path.join(process.env.HOME || '/root', '.openclaw', 'agents', 'main');
    const sessionsDir = path.join(agentDir, 'sessions');
    
    if (!fs.existsSync(sessionsDir)) {
      return;
    }
    
    try {
      const files = fs.readdirSync(sessionsDir)
        .filter(f => f.endsWith('.jsonl'))
        .map(f => ({
          name: f,
          time: fs.statSync(path.join(sessionsDir, f)).mtime.getTime()
        }))
        .sort((a, b) => b.time - a.time)
        .slice(0, 5); // 只检查最近的5个文件
      
      for (const file of files) {
        const filePath = path.join(sessionsDir, file.name);
        const content = fs.readFileSync(filePath, 'utf8');
        const lines = content.trim().split('\n').slice(-10); // 只看最后10行
        
        for (const line of lines) {
          try {
            const data = JSON.parse(line);
            if (data.message?.role === 'toolResult' && data.message?.content) {
              for (const item of data.message.content) {
                if (item.type === 'text' && item.text) {
                  const errorType = this.classifyError(item.text);
                  if (errorType) {
                    await this.handleDetectedError(data.message.model || this.currentModel, item.text, errorType);
                  }
                }
              }
            }
          } catch (e) {
            // 忽略解析错误
          }
        }
      }
    } catch (error) {
      console.error('Failed to monitor session errors:', error.message);
    }
  }

  /**
   * 处理检测到的错误
   */
  async handleDetectedError(model, errorMessage, errorType) {
    // 检查是否是严重的billing错误
    if (errorType === 'billing') {
      console.error(`⚠️ Billing error detected for model ${model}`);
      this.recordError(model, errorMessage, errorType);
      await this.switchToFallback('billing_error');
    } else if (errorType === 'rate_limit') {
      console.warn(`⚠️ Rate limit detected for model ${model}`);
      this.recordError(model, errorMessage, errorType);
      // 对于rate limit，短暂等待后可能恢复，不立即切换
    } else if (errorType === 'auth') {
      console.error(`⚠️ Auth error detected for model ${model}`);
      this.recordError(model, errorMessage, errorType);
      await this.switchToFallback('auth_error');
    }
  }

  /**
   * 运行监控循环
   */
  async run(watch = false, intervalMs = 30000) {
    console.log('🔍 OpenClaw Model Health Monitor');
    console.log(`Current model: ${this.currentModel}`);
    console.log(`Fallback models: ${MODEL_PRIORITY.fallbacks.join(', ')}`);
    
    this.loadState();
    
    const runOnce = async () => {
      console.log(`\n[${new Date().toISOString()}] Running health check...`);
      await this.checkModelStatus();
      await this.monitorSessionErrors();
      this.saveState();
    };
    
    if (watch) {
      console.log(`\n👀 Watching mode (interval: ${intervalMs}ms)`);
      await runOnce();
      
      setInterval(async () => {
        try {
          await runOnce();
        } catch (error) {
          console.error('Health check error:', error.message);
        }
      }, intervalMs);
      
      // 保持进程运行
      process.on('SIGINT', () => {
        console.log('\n\n👋 Stopping monitor...');
        this.saveState();
        process.exit(0);
      });
    } else {
      await runOnce();
    }
  }
}

// CLI入口
async function main() {
  const args = process.argv.slice(2);
  const watch = args.includes('--watch') || args.includes('-w');
  const intervalIndex = args.findIndex(a => a === '--interval-ms' || a === '-i');
  const intervalMs = intervalIndex !== -1 ? parseInt(args[intervalIndex + 1]) || 30000 : 30000;
  
  const monitor = new ModelHealthMonitor();
  await monitor.run(watch, intervalMs);
}

main().catch(error => {
  console.error('Monitor failed:', error);
  process.exit(1);
});