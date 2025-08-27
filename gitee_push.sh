#!/bin/bash

# SATS项目Gitee推送脚本
# 作者: sharksafe
# 日期: 2025-08-04
# 功能: 推送代码到Gitee

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 配置信息
GITEE_USERNAME="sharksafe"
REPO_NAME="sost"
REMOTE_URL="https://gitee.com/sharksafe/sost.git"

# 打印带颜色的消息
print_message() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
}

# 检查Git状态
check_git_status() {
    print_message $BLUE "检查Git状态..."

    if ! git status > /dev/null 2>&1; then
        print_message $RED "错误: 当前目录不是Git仓库"
        exit 1
    fi

    # 检查并配置Git邮箱（避免Gitee推送问题）
    local current_email=$(git config user.email)
    if [[ "$current_email" == *"@163.com"* ]] || [[ "$current_email" == *"@qq.com"* ]] || [[ "$current_email" == *"@gmail.com"* ]]; then
        print_message $YELLOW "检测到私有邮箱，正在配置为Gitee邮箱..."
        git config user.email "sharksafe@gitee.com"
        print_message $GREEN "邮箱配置已更新"
    fi
}

# 检查是否有未提交的更改
check_changes() {
    print_message $BLUE "检查是否有未提交的更改..."

    # 获取变化的文件列表
    local changed_files=$(git diff --name-only)
    local staged_files=$(git diff --cached --name-only)
    local untracked_files=$(git ls-files --others --exclude-standard)
    local deleted_files=$(git ls-files --deleted)

    if [ -z "$changed_files" ] && [ -z "$staged_files" ] && [ -z "$untracked_files" ] && [ -z "$deleted_files" ]; then
        print_message $GREEN "✅ 没有检测到文件变化，跳过推送"
        return 0
    else
        print_message $GREEN "检测到以下变化，准备提交..."
        if [ -n "$changed_files" ]; then
            print_message $CYAN "修改的文件:"
            echo "$changed_files" | while read file; do
                if [ -n "$file" ]; then
                    print_message $CYAN "  - $file"
                fi
            done
        fi
        if [ -n "$staged_files" ]; then
            print_message $CYAN "已暂存的文件:"
            echo "$staged_files" | while read file; do
                if [ -n "$file" ]; then
                    print_message $CYAN "  - $file"
                fi
            done
        fi
        if [ -n "$untracked_files" ]; then
            print_message $CYAN "新文件:"
            echo "$untracked_files" | while read file; do
                if [ -n "$file" ]; then
                    print_message $CYAN "  - $file"
                fi
            done
        fi
        if [ -n "$deleted_files" ]; then
            print_message $CYAN "删除的文件:"
            echo "$deleted_files" | while read file; do
                if [ -n "$file" ]; then
                    print_message $CYAN "  - $file"
                fi
            done
        fi
    fi
}

# 添加变化的文件到暂存区
add_files() {
    print_message $BLUE "添加变化的文件到暂存区..."

    # 获取变化的文件列表
    local changed_files=$(git diff --name-only)
    local staged_files=$(git diff --cached --name-only)
    local untracked_files=$(git ls-files --others --exclude-standard)
    local deleted_files=$(git ls-files --deleted)

    if [ -z "$changed_files" ] && [ -z "$staged_files" ] && [ -z "$untracked_files" ] && [ -z "$deleted_files" ]; then
        print_message $YELLOW "没有检测到文件变化"
        return 0
    fi

    print_message $BLUE "变化的文件:"
    if [ -n "$changed_files" ]; then
        echo "$changed_files" | while read file; do
            print_message $CYAN "  修改: $file"
        done
    fi

    if [ -n "$staged_files" ]; then
        echo "$staged_files" | while read file; do
            print_message $CYAN "  已暂存: $file"
        done
    fi

    if [ -n "$untracked_files" ]; then
        echo "$untracked_files" | while read file; do
            print_message $CYAN "  新文件: $file"
        done
    fi

    if [ -n "$deleted_files" ]; then
        echo "$deleted_files" | while read file; do
            print_message $CYAN "  删除: $file"
        done
    fi

    print_message $BLUE "添加变化的文件到暂存区..."

    # 添加所有变化的文件（包括删除的文件）
    if [ -n "$changed_files" ]; then
        echo "$changed_files" | xargs git add
    fi

    if [ -n "$untracked_files" ]; then
        echo "$untracked_files" | xargs git add
    fi

    if [ -n "$deleted_files" ]; then
        echo "$deleted_files" | xargs -I {} git rm {} 2>/dev/null || true
    fi

    if [ $? -eq 0 ]; then
        print_message $GREEN "变化文件添加成功"
    else
        print_message $RED "文件添加失败"
        exit 1
    fi
}

# 获取提交信息
get_commit_message() {
    print_message $BLUE "请输入提交信息 (默认: 自动提交 - $(date '+%Y-%m-%d %H:%M:%S')):"
    read -r commit_message

    if [ -z "$commit_message" ]; then
        commit_message="自动提交 - $(date '+%Y-%m-%d %H:%M:%S')"
    fi

    echo "$commit_message"
}

# 提交更改
commit_changes() {
    local commit_message=$1

    print_message $BLUE "提交更改..."

    git commit -m "$commit_message"

    if [ $? -eq 0 ]; then
        print_message $GREEN "提交成功: $commit_message"
    else
        print_message $RED "提交失败"
        exit 1
    fi
}

# 检查远程仓库
check_remote() {
    print_message $BLUE "检查远程仓库配置..."

    if ! git remote get-url origin > /dev/null 2>&1; then
        print_message $YELLOW "未配置远程仓库，正在添加..."
        git remote add origin "$REMOTE_URL"
    else
        git remote set-url origin "$REMOTE_URL"
    fi

    print_message $GREEN "远程仓库配置完成"
}

# 推送到远程仓库
push_to_remote() {
    print_message $BLUE "推送到Gitee..."

    local current_branch=$(git branch --show-current)

    # 尝试推送到master分支（Gitee默认分支）
    if [ "$current_branch" = "main" ]; then
        print_message $YELLOW "当前分支是main，尝试推送到master分支..."
        git push -u origin main:master
    else
        git push -u origin "$current_branch"
    fi

    if [ $? -eq 0 ]; then
        print_message $GREEN "推送成功！"
        print_message $GREEN "仓库地址: https://gitee.com/${GITEE_USERNAME}/${REPO_NAME}"
    else
        print_message $YELLOW "常规推送失败，尝试强制推送..."
        if [ "$current_branch" = "main" ]; then
            git push -u origin main:master --force
        else
            git push -u origin "$current_branch" --force
        fi
        
        if [ $? -eq 0 ]; then
            print_message $GREEN "强制推送成功！"
            print_message $GREEN "仓库地址: https://gitee.com/${GITEE_USERNAME}/${REPO_NAME}"
        else
            print_message $RED "推送失败"
            exit 1
        fi
    fi
}

# 显示帮助信息
show_help() {
    echo "用法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  -f, --force       强制推送（不询问）"
    echo "  -q, --quiet       静默模式"
    echo "  -h, --help        显示帮助信息"
    echo ""
    echo "示例:"
    echo "  $0                正常推送"
    echo "  $0 -f             强制推送"
    echo "  $0 -q             静默推送"
}

# 主函数
main() {
    print_message $GREEN "=== 开始推送代码到Gitee ==="
    print_message $GREEN "开始时间: $(date '+%Y-%m-%d %H:%M:%S')"
    echo

    check_git_status
    check_changes

    # 检查是否有文件需要提交
    local changed_files=$(git diff --name-only)
    local staged_files=$(git diff --cached --name-only)
    local untracked_files=$(git ls-files --others --exclude-standard)

    if [ -z "$changed_files" ] && [ -z "$staged_files" ] && [ -z "$untracked_files" ]; then
        print_message $GREEN "✅ 没有文件变化，跳过推送"
        return 0
    fi

    add_files

    local commit_message=$(get_commit_message)
    commit_changes "$commit_message"
    check_remote
    push_to_remote

    print_message $GREEN "=== 推送完成 ==="
    print_message $GREEN "结束时间: $(date '+%Y-%m-%d %H:%M:%S')"
}

# 处理命令行参数
case "${1:-}" in
    -h|--help|help)
        show_help
        exit 0
        ;;
    -f|--force)
        # 强制模式，跳过用户交互
        print_message $YELLOW "强制模式：跳过用户交互"
        ;;
    -q|--quiet)
        # 静默模式
        print_message $YELLOW "静默模式：使用默认提交信息"
        ;;
    "")
        # 正常模式
        ;;
    *)
        print_message $RED "未知选项: $1"
        show_help
        exit 1
        ;;
esac

# 执行主函数
main "$@"
