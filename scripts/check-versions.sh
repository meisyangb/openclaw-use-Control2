#!/bin/bash
# 版本检查脚本
# 用法：./scripts/check-versions.sh

echo "📊 版本信息"
echo "================================"
echo ""

# 当前提交
echo "📝 当前提交:"
git log -1 --oneline
echo ""

# 当前标签
CURRENT_TAG=$(git describe --tags --abbrev=0 2>/dev/null || echo "无标签")
echo "🏷️  当前标签：${CURRENT_TAG}"
echo ""

# 最近 10 个版本
echo "📜 最近版本:"
git tag -l "v*" --sort=-version:refname | head -10
echo ""

# 版本统计
echo "📈 版本统计:"
TOTAL_TAGS=$(git tag -l | wc -l)
STABLE_TAGS=$(git tag -l | grep -c "stable" 2>/dev/null || echo 0)
DEPRECATED_TAGS=$(git tag -l | grep -c "deprecated" 2>/dev/null || echo 0)
TESTING_TAGS=$(git tag -l | grep -c "testing" 2>/dev/null || echo 0)

echo "  总标签数：${TOTAL_TAGS}"
echo "  ✅ Stable: ${STABLE_TAGS}"
echo "  🔄 Testing: ${TESTING_TAGS}"
echo "  ❌ Deprecated: ${DEPRECATED_TAGS}"
echo ""

# 版本历史
if [[ -f "VERSIONS.md" ]]; then
    echo "📖 版本历史 (最近 5 条):"
    echo "--------------------------------"
    grep "^### v" VERSIONS.md | head -5
    echo ""
fi

# 远程标签
echo "🌐 远程标签:"
git ls-remote --tags origin | wc -l | xargs echo "  数量:"
echo ""

# 建议
echo "💡 建议:"
if [[ ${TESTING_TAGS} -gt 0 ]]; then
    echo "  ⚠️  有 ${TESTING_TAGS} 个测试版本，建议验证后标记为 stable"
fi

if [[ ${DEPRECATED_TAGS} -gt 0 ]]; then
    echo "  ℹ️  有 ${DEPRECATED_TAGS} 个废弃版本，可考虑清理"
fi

if [[ -z "${CURRENT_TAG}" ]]; then
    echo "  ⚠️  当前没有标签，建议创建版本标签"
    echo "     运行：./scripts/create-iteration-tag.sh"
fi
