#!/bin/bash
# 安装 Git Hooks 脚本

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"
HOOKS_DIR="$REPO_ROOT/.git/hooks"

echo "=== 安装 Git Hooks ==="

# 检查 Git 仓库
if [ ! -d "$REPO_ROOT/.git" ]; then
    echo "错误：不是 Git 仓库"
    exit 1
fi

# 创建 hooks 目录
mkdir -p "$HOOKS_DIR"

# 复制 hooks
cp "$REPO_ROOT/.git/hooks/pre-commit" "$HOOKS_DIR/pre-commit" 2>/dev/null || true
cp "$REPO_ROOT/.git/hooks/post-commit" "$HOOKS_DIR/post-commit" 2>/dev/null || true

# 设置执行权限
chmod +x "$HOOKS_DIR/pre-commit" 2>/dev/null || true
chmod +x "$HOOKS_DIR/post-commit" 2>/dev/null || true

echo "✓ Git Hooks 已安装"
echo ""
echo "已安装的 Hooks:"
ls -la "$HOOKS_DIR/" | grep -E "^-.*x" | awk '{print "  - " $NF}'
