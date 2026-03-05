#!/bin/bash
# 版本检查脚本
# 用法：./scripts/version-check.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}=== OpenClaw 版本检查工具 ===${NC}"
echo ""

# 检查项统计
TOTAL=0
PASSED=0
FAILED=0

# 检查函数
check() {
    local name=$1
    local command=$2
    
    TOTAL=$((TOTAL + 1))
    echo -n "检查：$name ... "
    
    if eval "$command" > /dev/null 2>&1; then
        echo -e "${GREEN}✓ 通过${NC}"
        PASSED=$((PASSED + 1))
        return 0
    else
        echo -e "${RED}✗ 失败${NC}"
        FAILED=$((FAILED + 1))
        return 1
    fi
}

# 1. 检查 Git 仓库
check "Git 仓库" "git rev-parse --git-dir"

# 2. 检查当前分支
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
echo -n "检查：当前分支 ($CURRENT_BRANCH) ... "
if [ "$CURRENT_BRANCH" = "main" ] || [ "$CURRENT_BRANCH" = "develop" ]; then
    echo -e "${GREEN}✓ 通过${NC}"
    PASSED=$((PASSED + 1))
else
    echo -e "${YELLOW}⚠ 警告：不在主分支或开发分支${NC}"
fi
TOTAL=$((TOTAL + 1))

# 3. 检查是否有未提交的变更
echo -n "检查：工作区清洁 ... "
if [ -z "$(git status --porcelain)" ]; then
    echo -e "${GREEN}✓ 通过${NC}"
    PASSED=$((PASSED + 1))
else
    echo -e "${YELLOW}⚠ 有未提交的变更${NC}"
    git status --short | head -5
fi
TOTAL=$((TOTAL + 1))

# 4. 检查 package.json 版本
if [ -f "$ROOT_DIR/package.json" ]; then
    PKG_VERSION=$(cat "$ROOT_DIR/package.json" | grep '"version"' | head -1 | sed 's/.*"version": "\([^"]*\)".*/\1/')
    check "package.json 版本 ($PKG_VERSION)" "test -n '$PKG_VERSION'"
else
    echo -e "${YELLOW}⚠ 未找到 package.json${NC}"
fi
TOTAL=$((TOTAL + 1))

# 5. 检查 Git 标签
LATEST_TAG=$(git describe --tags --abbrev=0 2>/dev/null || echo "")
if [ -n "$LATEST_TAG" ]; then
    check "最新 Git 标签 ($LATEST_TAG)" "test -n '$LATEST_TAG'"
else
    echo -e "${YELLOW}⚠ 未找到 Git 标签${NC}"
    TOTAL=$((TOTAL + 1))
fi
TOTAL=$((TOTAL + 1))

# 6. 检查版本一致性
if [ -n "$LATEST_TAG" ] && [ -n "$PKG_VERSION" ]; then
    TAG_VERSION=${LATEST_TAG#v}
    echo -n "检查：版本一致性 (TAG: $TAG_VERSION vs PKG: $PKG_VERSION) ... "
    if [ "$TAG_VERSION" = "$PKG_VERSION" ]; then
        echo -e "${GREEN}✓ 通过${NC}"
        PASSED=$((PASSED + 1))
    else
        echo -e "${RED}✗ 不一致${NC}"
        FAILED=$((FAILED + 1))
    fi
    TOTAL=$((TOTAL + 1))
fi

# 7. 检查 CHANGELOG.md
check "CHANGELOG.md 存在" "test -f '$ROOT_DIR/CHANGELOG.md'"

# 8. 检查 VERSION-MANAGEMENT-STRATEGY.md
check "版本管理策略文档" "test -f '$ROOT_DIR/VERSION-MANAGEMENT-STRATEGY.md'"

# 9. 检查版本脚本
check "version-bump.sh 存在" "test -f '$ROOT_DIR/scripts/version-bump.sh'"
check "version-bump.sh 可执行" "test -x '$ROOT_DIR/scripts/version-bump.sh'"

# 10. 检查 Git 远程
check "Git 远程仓库" "git remote -v"

echo ""
echo "================================"
echo -e "总计：$TOTAL 项检查"
echo -e "通过：${GREEN}$PASSED${NC}"
echo -e "失败：${RED}$FAILED${NC}"
echo "================================"

if [ $FAILED -gt 0 ]; then
    echo ""
    echo -e "${RED}❌ 检查未通过，请修复上述问题${NC}"
    exit 1
else
    echo ""
    echo -e "${GREEN}✅ 所有检查通过！${NC}"
    exit 0
fi
