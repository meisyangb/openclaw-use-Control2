#!/bin/bash
# 版本升级脚本
# 用法：./scripts/version-bump.sh [major|minor|patch|prerelease]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 获取当前版本
get_current_version() {
    if [ -f "$ROOT_DIR/package.json" ]; then
        cat "$ROOT_DIR/package.json" | grep '"version"' | head -1 | sed 's/.*"version": "\([^"]*\)".*/\1/'
    elif [ -f "$ROOT_DIR/my-dev/openclaw-deployment/src/config/version.ts" ]; then
        # 从 TypeScript 版本文件读取
        grep -oP 'major: \d+' "$ROOT_DIR/my-dev/openclaw-deployment/src/config/version.ts" | head -1 | sed 's/major: //'
        echo "."
        grep -oP 'minor: \d+' "$ROOT_DIR/my-dev/openclaw-deployment/src/config/version.ts" | head -1 | sed 's/minor: //'
        echo "."
        grep -oP 'patch: \d+' "$ROOT_DIR/my-dev/openclaw-deployment/src/config/version.ts" | head -1 | sed 's/patch: //'
    else
        echo "0.0.0"
    fi
}

# 解析版本号
parse_version() {
    local version=$1
    echo $version | sed 's/v//' | tr '.' ' '
}

# 升级版本号
bump_version() {
    local current=$1
    local type=$2
    
    read MAJOR MINOR PATCH <<< $(parse_version $current)
    
    case $type in
        major)
            MAJOR=$((MAJOR + 1))
            MINOR=0
            PATCH=0
            ;;
        minor)
            MINOR=$((MINOR + 1))
            PATCH=0
            ;;
        patch)
            PATCH=$((PATCH + 1))
            ;;
        prerelease)
            # 预发布版本处理
            if [[ $PATCH == *-* ]]; then
                local base=${PATCH%-*}
                local num=${PATCH#*-}
                PATCH="$base-$((num + 1))"
            else
                PATCH="$PATCH-beta.1"
            fi
            ;;
        *)
            echo -e "${RED}错误：未知的版本类型 '$type'${NC}"
            echo "支持的类型：major, minor, patch, prerelease"
            exit 1
            ;;
    esac
    
    echo "$MAJOR.$MINOR.$PATCH"
}

# 更新版本文件
update_version_files() {
    local new_version=$1
    
    echo -e "${YELLOW}更新版本文件...${NC}"
    
    # 更新 package.json
    if [ -f "$ROOT_DIR/package.json" ]; then
        sed -i.bak "s/\"version\": \"[^\"]*\"/\"version\": \"$new_version\"/" "$ROOT_DIR/package.json"
        rm -f "$ROOT_DIR/package.json.bak"
        echo "  ✓ package.json"
    fi
    
    # 更新 Python 版本文件
    find "$ROOT_DIR/my-dev" -name "__init__.py" -exec grep -l "__version__" {} \; | while read file; do
        sed -i.bak "s/__version__ = \"[^\"]*\"/__version__ = \"$new_version\"/" "$file"
        rm -f "$file.bak"
        echo "  ✓ $file"
    done
    
    # 更新 TypeScript 版本文件
    if [ -f "$ROOT_DIR/my-dev/openclaw-deployment/src/config/version.ts" ]; then
        # 这里需要根据实际文件结构调整
        echo "  ✓ version.ts (需手动更新)"
    fi
}

# 主函数
main() {
    local bump_type=${1:-patch}
    
    echo -e "${GREEN}=== OpenClaw 版本升级工具 ===${NC}"
    echo ""
    
    # 获取当前版本
    local current=$(get_current_version)
    echo -e "当前版本：${YELLOW}v$current${NC}"
    
    # 计算新版本
    local new_version=$(bump_version $current $bump_type)
    echo -e "新版本：${GREEN}v$new_version${NC}"
    echo ""
    
    # 确认
    read -p "确认升级？[y/N] " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${RED}已取消${NC}"
        exit 0
    fi
    
    # 更新版本文件
    update_version_files $new_version
    
    # Git 操作
    echo ""
    echo -e "${YELLOW}Git 操作...${NC}"
    
    git add -A
    git commit -m "chore: 升级到 v$new_version" || echo "  ⚠ 没有变更需要提交"
    git tag -a "v$new_version" -m "Release v$new_version"
    
    echo ""
    echo -e "${GREEN}✅ 版本升级完成！${NC}"
    echo ""
    echo "下一步："
    echo "  1. 检查变更：git show v$new_version"
    echo "  2. 推送标签：git push origin v$new_version"
    echo "  3. 创建 Release: https://github.com/meisyangb/openclaw-use-Control2/releases/new"
}

# 执行
main "$@"
