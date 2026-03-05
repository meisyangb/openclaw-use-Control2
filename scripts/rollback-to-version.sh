#!/bin/bash
# 回滚到指定版本
# 用法：./scripts/rollback-to-version.sh <版本号>

set -e

TARGET_VERSION=$1

if [[ -z "${TARGET_VERSION}" ]]; then
    echo "❌ 请指定目标版本"
    echo ""
    echo "用法：./scripts/rollback-to-version.sh v20260305-1900"
    echo ""
    echo "可用版本:"
    git tag -l "v*" --sort=-version:refname | head -10
    exit 1
fi

# 检查版本是否存在
if ! git tag -l | grep -q "${TARGET_VERSION}"; then
    echo "❌ 版本不存在：${TARGET_VERSION}"
    echo ""
    echo "可用版本:"
    git tag -l "v*" --sort=-version:refname | head -10
    exit 1
fi

echo "🔄 回滚到版本：${TARGET_VERSION}"
echo "================================"

# 获取当前版本
CURRENT_VERSION=$(git describe --tags --abbrev=0 2>/dev/null || echo "unknown")
echo "当前版本：${CURRENT_VERSION}"
echo "目标版本：${TARGET_VERSION}"

# 询问确认
read -p "确定要回滚吗？这将创建一个新的回滚分支 (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ 回滚已取消"
    exit 1
fi

# 创建回滚分支
ROLLBACK_BRANCH="rollback/${TARGET_VERSION}"
git checkout ${TARGET_VERSION}
git checkout -b ${ROLLBACK_BRANCH}

echo "✅ 已创建回滚分支：${ROLLBACK_BRANCH}"

# 标记当前版本为废弃（如果是测试版本）
if [[ "${CURRENT_VERSION}" == *"testing"* ]] || [[ "${CURRENT_VERSION}" == *"deprecated"* ]]; then
    echo ""
    read -p "是否将当前版本标记为废弃？(y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        git tag -a "${CURRENT_VERSION}-deprecated" -m "Deprecated, rolled back to ${TARGET_VERSION}"
        echo "✅ 已标记 ${CURRENT_VERSION} 为废弃"
    fi
fi

# 询问是否推送
echo ""
read -p "是否推送到 GitHub？(y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    git push origin ${ROLLBACK_BRANCH} --tags
    echo "✅ 已推送到 GitHub"
fi

echo ""
echo "📊 回滚完成!"
echo "分支：${ROLLBACK_BRANCH}"
echo "版本：${TARGET_VERSION}"
echo ""
echo "下一步:"
echo "1. 在回滚分支上测试功能"
echo "2. 确认无误后合并到 main"
echo "3. 或者继续修复问题后重新发布"
