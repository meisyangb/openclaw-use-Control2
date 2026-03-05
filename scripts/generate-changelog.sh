#!/bin/bash
# CHANGELOG 生成脚本
# 用法：./scripts/generate-changelog.sh [v1.0.0]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"
CHANGELOG_FILE="$ROOT_DIR/CHANGELOG.md"

# 颜色输出
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 获取所有标签
get_tags() {
    git tag --sort=-creatordate
}

# 获取两个标签之间的提交
get_commits_between() {
    local from=$1
    local to=$2
    
    if [ -z "$from" ]; then
        git log "$to" --pretty=format:"%h|%s|%b" --reverse
    else
        git log "$from..$to" --pretty=format:"%h|%s|%b" --reverse
    fi
}

# 分类提交
categorize_commits() {
    local commits="$1"
    
    local features=""
    local fixes=""
    local docs=""
    local styles=""
    local refactors=""
    local perfs=""
    local tests=""
    local chores=""
    
    while IFS= read -r line; do
        local hash=$(echo "$line" | cut -d'|' -f1)
        local subject=$(echo "$line" | cut -d'|' -f2)
        local body=$(echo "$line" | cut -d'|' -f3-)
        
        # 根据提交类型分类
        if [[ $subject =~ ^feat(\(.+\))?:\ (.+)$ ]]; then
            features+="- ${BASH_REMATCH[2]} (\`$hash\`)\n"
        elif [[ $subject =~ ^fix(\(.+\))?:\ (.+)$ ]]; then
            fixes+="- ${BASH_REMATCH[2]} (\`$hash\`)\n"
        elif [[ $subject =~ ^docs(\(.+\))?:\ (.+)$ ]]; then
            docs+="- ${BASH_REMATCH[2]} (\`$hash\`)\n"
        elif [[ $subject =~ ^style(\(.+\))?:\ (.+)$ ]]; then
            styles+="- ${BASH_REMATCH[2]} (\`$hash\`)\n"
        elif [[ $subject =~ ^refactor(\(.+\))?:\ (.+)$ ]]; then
            refactors+="- ${BASH_REMATCH[2]} (\`$hash\`)\n"
        elif [[ $subject =~ ^perf(\(.+\))?:\ (.+)$ ]]; then
            perfs+="- ${BASH_REMATCH[2]} (\`$hash\`)\n"
        elif [[ $subject =~ ^test(\(.+\))?:\ (.+)$ ]]; then
            tests+="- ${BASH_REMATCH[2]} (\`$hash\`)\n"
        elif [[ $subject =~ ^chore(\(.+\))?:\ (.+)$ ]]; then
            chores+="- ${BASH_REMATCH[2]} (\`$hash\`)\n"
        else
            # 未分类的提交
            chores+="- $subject (\`$hash\`)\n"
        fi
    done <<< "$commits"
    
    # 输出分类结果
    if [ -n "$features" ]; then
        echo -e "### ✨ 新功能\n$features"
    fi
    
    if [ -n "$fixes" ]; then
        echo -e "### 🐛 Bug 修复\n$fixes"
    fi
    
    if [ -n "$docs" ]; then
        echo -e "### 📚 文档\n$docs"
    fi
    
    if [ -n "$styles" ]; then
        echo -e "### 💄 样式\n$styles"
    fi
    
    if [ -n "$refactors" ]; then
        echo -e "### ♻️ 重构\n$refactors"
    fi
    
    if [ -n "$perfs" ]; then
        echo -e "### ⚡ 性能优化\n$perfs"
    fi
    
    if [ -n "$tests" ]; then
        echo -e "### ✅ 测试\n$tests"
    fi
    
    if [ -n "$chores" ]; then
        echo -e "### 🔧 其他\n$chores"
    fi
}

# 生成单个版本的 changelog
generate_version_changelog() {
    local version=$1
    local prev_version=$2
    local date=$(git log -1 --format=%cs "$version")
    
    echo "## [$version] - $date"
    echo ""
    
    local commits=$(get_commits_between "$prev_version" "$version")
    categorize_commits "$commits"
    
    echo ""
}

# 主函数
main() {
    local target_version=$1
    
    echo -e "${GREEN}=== OpenClaw CHANGELOG 生成器 ===${NC}"
    echo ""
    
    # 检查 CHANGELOG.md 是否存在
    if [ ! -f "$CHANGELOG_FILE" ]; then
        echo -e "${YELLOW}创建新的 CHANGELOG.md${NC}"
        echo "# Changelog" > "$CHANGELOG_FILE"
        echo "" >> "$CHANGELOG_FILE"
        echo "所有重要的项目变更都将记录在此文件中。" >> "$CHANGELOG_FILE"
        echo "" >> "$CHANGELOG_FILE"
        echo "格式基于 [Keep a Changelog](https://keepachangelog.com/)，" >> "$CHANGELOG_FILE"
        echo "项目遵循 [语义化版本](https://semver.org/)。" >> "$CHANGELOG_FILE"
        echo "" >> "$CHANGELOG_FILE"
    fi
    
    # 获取所有标签
    local tags=$(get_tags)
    
    if [ -z "$tags" ]; then
        echo -e "${YELLOW}未找到 Git 标签${NC}"
        exit 0
    fi
    
    # 生成 changelog
    local temp_file=$(mktemp)
    
    # 复制现有 changelog 的头部
    if [ -f "$CHANGELOG_FILE" ]; then
        head -n 10 "$CHANGELOG_FILE" > "$temp_file"
        echo "" >> "$temp_file"
    fi
    
    # 生成每个版本的 changelog
    local prev_tag=""
    for tag in $tags; do
        echo -e "${BLUE}处理版本：$tag${NC}"
        generate_version_changelog "$tag" "$prev_tag" >> "$temp_file"
        prev_tag="$tag"
    done
    
    # 如果有未标签的提交，生成"Unreleased"部分
    local latest_tag=$(echo "$tags" | head -1)
    local unreleased_commits=$(git log "$latest_tag..HEAD" --pretty=format:"%h|%s|%b" 2>/dev/null || true)
    
    if [ -n "$unreleased_commits" ]; then
        echo -e "${YELLOW}发现未发布的提交${NC}"
        echo "## [Unreleased]" >> "$temp_file"
        echo "" >> "$temp_file"
        categorize_commits "$unreleased_commits" >> "$temp_file"
        echo "" >> "$temp_file"
    fi
    
    # 替换原文件
    mv "$temp_file" "$CHANGELOG_FILE"
    
    echo ""
    echo -e "${GREEN}✅ CHANGELOG 生成完成！${NC}"
    echo ""
    echo "查看结果：cat $CHANGELOG_FILE"
}

# 执行
main "$@"
