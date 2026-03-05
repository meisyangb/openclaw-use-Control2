#!/usr/bin/env python3
"""
Quick Model Switcher - 快速模型切换工具
用于在模型出现问题时快速切换到备用模型
"""

import json
import subprocess
import sys
from pathlib import Path

HOME = Path.home()
CONFIG_PATH = HOME / ".openclaw" / "openclaw.json"

def load_config():
    """加载配置"""
    try:
        with open(CONFIG_PATH) as f:
            return json.load(f)
    except Exception:
        return {}

def get_current_model():
    """获取当前模型"""
    try:
        result = subprocess.run(
            ["openclaw", "models", "status", "--plain"],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            lines = result.stdout.strip().split("\n")
            if lines:
                return lines[0].split()[0]
    except Exception:
        pass
    return "bailian/qwen3-coder-plus"

def get_fallbacks():
    """获取备用模型列表"""
    config = load_config()
    fallbacks = config.get("agents", {}).get("defaults", {}).get("model", {}).get("fallbacks", [])
    if not fallbacks:
        fallbacks = [
            "bailian/qwen3-coder-plus",
            "zai/glm-4.5-air",
            "zai/glm-4.7",
            "bailian/qwen3.5-plus"
        ]
    return fallbacks

def switch_model(target_model):
    """切换模型"""
    try:
        result = subprocess.run(
            ["openclaw", "models", "set", target_model],
            capture_output=True,
            text=True,
            timeout=30
        )
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def main():
    current = get_current_model()
    fallbacks = get_fallbacks()
    
    print(f"Current model: {current}")
    print(f"Available fallbacks: {', '.join(fallbacks)}")
    
    if len(sys.argv) > 1:
        target = sys.argv[1]
        if target in fallbacks or target.startswith("bailian/") or target.startswith("zai/"):
            success, stdout, stderr = switch_model(target)
            if success:
                print(f"✓ Switched to {target}")
            else:
                print(f"✗ Failed: {stderr}")
                sys.exit(1)
        else:
            print(f"Unknown model: {target}")
            sys.exit(1)
    else:
        # 自动切换到下一个可用模型
        for model in fallbacks:
            if model != current:
                print(f"Switching to {model}...")
                success, stdout, stderr = switch_model(model)
                if success:
                    print(f"✓ Switched to {model}")
                    break
                else:
                    print(f"✗ Failed to switch to {model}: {stderr}")

if __name__ == "__main__":
    main()