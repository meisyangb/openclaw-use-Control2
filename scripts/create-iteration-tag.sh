#!/bin/bash
# 创建迭代版本标签
# 用法：./scripts/create-iteration-tag.sh [描述]

set -e

DESCRIPTION=${1:-"iteration-update"}
TIMESTAMP=$(date +%Y%m%d-%H%M)
VERSION_TAG="v${TIMESTAMP}-${DESCRIPTION}"

echo "🏷️  创建迭代版本：${VERSION_TAG}"
echo "================================"

# 检查 Git 状态
if [[ -n $(git status -s) ]]; then
    echo "⚠️  有未提交的变更，请先提交"
    git status -s
    exit 1
fi

# 获取当前提交哈希
COMMIT_HASH=$(git log -1 --oneline)
echo "📝 当前提交：${COMMIT_HASH}"

# 创建标签
git tag -a "${VERSION_TAG}" -m "Iteration $(date '+%Y-%m-%d %H:%M:%S') - ${DESCRIPTION}"

echo "✅ 标签创建成功"

# 询问是否推送
read -p "是否推送到 GitHub？(y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    git push origin --tags
    echo "✅ 已推送到 GitHub"
fi

# 更新 VERSIONS.md
if [[ -f "VERSIONS.md" ]]; then
    # 在文件开头插入新版本
    TEMP_FILE=$(mktemp)
    echo "### ${VERSION_TAG} ($(date '+%H:%M'))" > ${TEMP_FILE}
    echo "- **变更**: ${DESCRIPTION}" >> ${TEMP_FILE}
    echo "- **提交**: ${COMMIT_HASH}" >> ${TEMP_FILE}
    echo "- **状态**: 🔄 testing" >> ${TEMP_FILE}
    echo "- **备注**: 待填写" >> ${TEMP_FILE}
    echo "" >> ${TEMP_FILE}
    cat VERSIONS.md >> ${TEMP_FILE}
    mv ${TEMP_FILE} VERSIONS.md
    
    echo "✅ 已更新 VERSIONS.md"
else
    echo "⚠️  VERSIONS.md 不存在，跳过更新"
fi

echo ""
echo "📊 版本信息:"
git tag -l "v${TIMESTAMP}*" --sort=-version:refname
