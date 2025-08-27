#!/bin/bash

# SATS项目Gitee自动化脚本
# 作者: sharksafe
# 日期: 2025-08-04
# 功能: 推送代码到Gitee + 下载最新代码 + MD5检查 + 自动备份

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 加载配置文件
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR"

# 配置信息（从配置文件加载）
# GITEE_USERNAME, GITEE_TOKEN, REPO_NAME, REMOTE_URL 从 gitee_config.sh 加载

# 备份配置
BACKUP_DIR="backups"
BACKUP_PREFIX="sats_backup_"
MD5_FILE=".md5_cache"

# 打印带颜色的消息
print_message() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
}

# 显示帮助信息
show_help() {
    echo "用法: $0 [命令] [选项]"
    echo ""
    echo "命令:"
    echo "  push              推送代码到Gitee"
    echo "  pull              下载最新代码"
    echo "  sync              同步（推送+下载）"
    echo "  backup            创建备份"
    echo "  restore <备份名>   恢复备份"
    echo "  status            显示状态信息"
    echo ""
    echo "选项:"
    echo "  -f, --force       强制操作（不询问）"
    echo "  -q, --quiet       静默模式"
    echo "  -h, --help        显示帮助信息"
    echo ""
    echo "示例:"
    echo "  $0 push           推送代码"
    echo "  $0 pull           下载最新代码"
    echo "  $0 sync           同步代码"
    echo "  $0 push -f        强制推送"
    echo "  $0 pull -q        静默下载"
    echo ""
    echo "备份管理:"
    echo "  $0 backup         创建备份"
    echo "  $0 restore backup_20250804_194500  恢复指定备份"
    echo "  $0 status         显示状态"
}

# 计算文件MD5值
calculate_md5() {
    local file_path="$1"
    if [ -f "$file_path" ]; then
        md5sum "$file_path" | cut -d' ' -f1
    else
        echo ""
    fi
}

# 计算目录MD5值
calculate_dir_md5() {
    local dir_path="$1"
    if [ -d "$dir_path" ]; then
        find "$dir_path" -type f -exec md5sum {} \; | sort | md5sum | cut -d' ' -f1
    else
        echo ""
    fi
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

    # 检查空文件夹变化
    local new_empty_dirs=""
    for item in $(find . -type d -empty -not -path "./.git*" -not -path "./backups*" -not -path "./__pycache__*" -not -path "./node_modules*" 2>/dev/null); do
        # 检查这个文件夹是否在Git中
        if ! git ls-files --error-unmatch "$item" >/dev/null 2>&1; then
            new_empty_dirs="$new_empty_dirs $item"
        fi
    done

    if [ -z "$changed_files" ] && [ -z "$staged_files" ] && [ -z "$untracked_files" ] && [ -z "$deleted_files" ] && [ -z "$new_empty_dirs" ]; then
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
        if [ -n "$new_empty_dirs" ]; then
            print_message $CYAN "新空文件夹:"
            echo "$new_empty_dirs" | while read dir; do
                if [ -n "$dir" ]; then
                    print_message $CYAN "  - $dir"
                fi
            done
        fi
    fi
}

# 处理文件夹操作
handle_folder_operations() {
    print_message $BLUE "检查文件夹操作..."

    # 获取所有变更的文件和目录
    local changed_files=$(git diff --name-only)
    local staged_files=$(git diff --cached --name-only)
    local untracked_files=$(git ls-files --others --exclude-standard)
    local deleted_files=$(git ls-files --deleted)

    # 检查是否有文件夹被删除
    local deleted_dirs=""
    for file in $deleted_files; do
        local dir=$(dirname "$file")
        if [ "$dir" != "." ]; then
            deleted_dirs="$deleted_dirs $dir"
        fi
    done

    # 去重
    deleted_dirs=$(echo "$deleted_dirs" | tr ' ' '\n' | sort -u | tr '\n' ' ')

    # 处理删除的文件夹
    for dir in $deleted_dirs; do
        if [ -n "$dir" ] && [ "$dir" != "." ]; then
            print_message $YELLOW "检测到删除的文件夹: $dir"
            # 确保文件夹被正确删除
            if [ -d "$dir" ]; then
                print_message $BLUE "删除文件夹: $dir"
                git rm -r "$dir" 2>/dev/null || true
            fi
        fi
    done

    # 检查新创建的文件夹（包括空文件夹）
    local new_dirs=""
    for file in $untracked_files; do
        local dir=$(dirname "$file")
        if [ "$dir" != "." ]; then
            new_dirs="$new_dirs $dir"
        fi
    done

    # 检查空文件夹
    for item in $(find . -type d -empty -not -path "./.git*" -not -path "./backups*" -not -path "./__pycache__*" -not -path "./node_modules*" 2>/dev/null); do
        # 检查这个文件夹是否在Git中
        if ! git ls-files --error-unmatch "$item" >/dev/null 2>&1; then
            new_dirs="$new_dirs $item"
        fi
    done

    # 去重
    new_dirs=$(echo "$new_dirs" | tr ' ' '\n' | sort -u | tr '\n' ' ')

    # 处理新创建的文件夹
    for dir in $new_dirs; do
        if [ -n "$dir" ] && [ "$dir" != "." ]; then
            print_message $YELLOW "检测到新文件夹: $dir"
            # 确保文件夹被添加到Git
            if [ -d "$dir" ]; then
                print_message $BLUE "添加文件夹: $dir"
                git add "$dir" 2>/dev/null || true
            fi
        fi
    done

    print_message $GREEN "文件夹操作处理完成"
}

# 执行数据库备份
execute_database_backup() {
    print_message $BLUE "执行数据库备份..."

    local export_script="$PROJECT_ROOT/scripts/export_database.py"

    if [ -f "$export_script" ]; then
        if [ -x "$export_script" ]; then
            python3 "$export_script"
            if [ $? -eq 0 ]; then
                print_message $GREEN "数据库备份成功"

                # 将备份文件添加到Git
                local sql_dir="$PROJECT_ROOT/sql"
                if [ -d "$sql_dir" ]; then
                    git add "$sql_dir"/*.sql 2>/dev/null || true

                    # 检查是否有新的SQL文件需要提交
                    if ! git diff --cached --quiet -- "$sql_dir"; then
                        print_message $BLUE "自动提交数据库备份文件..."
                        git commit -m "Auto backup database $(date '+%Y-%m-%d %H:%M:%S')" -- "$sql_dir"/*.sql 2>/dev/null || true
                    fi
                fi
            else
                print_message $YELLOW "数据库备份失败，继续执行其他操作"
            fi
        else
            print_message $YELLOW "数据库导出脚本不可执行，跳过备份"
        fi
    else
        print_message $YELLOW "数据库导出脚本不存在，跳过备份"
    fi
}

# 添加变化的文件到暂存区
add_files() {
    print_message $BLUE "检查变化的文件..."

    # 获取变化的文件列表
    local changed_files=$(git diff --name-only)
    local staged_files=$(git diff --cached --name-only)
    local untracked_files=$(git ls-files --others --exclude-standard)
    local deleted_files=$(git ls-files --deleted)

    # 检查是否有新创建的空文件夹
    local new_empty_dirs=""
    for item in $(find . -type d -empty -not -path "./.git*" -not -path "./backups*" -not -path "./__pycache__*" -not -path "./node_modules*" 2>/dev/null); do
        # 检查这个文件夹是否在Git中
        if ! git ls-files --error-unmatch "$item" >/dev/null 2>&1; then
            new_empty_dirs="$new_empty_dirs $item"
        fi
    done

    if [ -z "$changed_files" ] && [ -z "$staged_files" ] && [ -z "$untracked_files" ] && [ -z "$deleted_files" ] && [ -z "$new_empty_dirs" ]; then
        print_message $YELLOW "没有检测到文件变化"
        return 0
    fi

    # 处理文件夹操作
    handle_folder_operations

    # 执行数据库备份
    execute_database_backup

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

    if [ -n "$new_empty_dirs" ]; then
        echo "$new_empty_dirs" | while read dir; do
            print_message $CYAN "  新空文件夹: $dir"
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
    # 在静默模式下，直接使用默认提交信息
    if [ "$QUIET_MODE" = "true" ]; then
        commit_message="自动提交 - $(date '+%Y-%m-%d %H:%M:%S')"
    else
        print_message $BLUE "请输入提交信息 (默认: 自动提交 - $(date '+%Y-%m-%d %H:%M:%S')):"
        read -r commit_message

        if [ -z "$commit_message" ]; then
            commit_message="自动提交 - $(date '+%Y-%m-%d %H:%M:%S')"
        fi
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

    git push -u origin "$current_branch"

    if [ $? -eq 0 ]; then
        print_message $GREEN "推送成功！"
        print_message $GREEN "仓库地址: https://gitee.com/${GITEE_USERNAME}/${REPO_NAME}"
    else
        print_message $RED "推送失败"
        exit 1
    fi
}

# 创建备份
create_backup() {
    local backup_name="${BACKUP_PREFIX}$(date '+%Y%m%d_%H%M%S')"
    local backup_path="$BACKUP_DIR/$backup_name"

    print_message $BLUE "创建备份: $backup_name"

    # 创建备份目录
    mkdir -p "$backup_path"

    # 复制文件（排除备份目录和Git目录）
    rsync -av --exclude="$BACKUP_DIR" --exclude=".git" --exclude="*.pyc" --exclude="__pycache__" . "$backup_path/"

    if [ $? -eq 0 ]; then
        print_message $GREEN "备份创建成功: $backup_path"

        # 保存备份信息
        echo "$backup_name:$(date '+%Y-%m-%d %H:%M:%S')" >> "$BACKUP_DIR/backup_list.txt"

        # 计算备份MD5
        local backup_md5=$(calculate_dir_md5 "$backup_path")
        echo "$backup_name:$backup_md5" >> "$BACKUP_DIR/backup_md5.txt"

        print_message $GREEN "备份MD5: $backup_md5"
    else
        print_message $RED "备份创建失败"
        exit 1
    fi
}

# 恢复备份
restore_backup() {
    local backup_name="$1"
    local backup_path="$BACKUP_DIR/$backup_name"

    if [ -z "$backup_name" ]; then
        print_message $RED "请指定备份名称"
        print_message $BLUE "可用备份:"
        ls -1 "$BACKUP_DIR" | grep "^$BACKUP_PREFIX" | head -10
        exit 1
    fi

    if [ ! -d "$backup_path" ]; then
        print_message $RED "备份不存在: $backup_name"
        exit 1
    fi

    print_message $YELLOW "即将恢复备份: $backup_name"
    print_message $YELLOW "这将覆盖当前文件，是否继续？(y/n)"
    read -r response
    if [[ ! "$response" =~ ^[Yy]$ ]]; then
        print_message $BLUE "取消恢复"
        exit 0
    fi

    # 创建当前状态备份
    create_backup

    # 恢复文件
    rsync -av --delete "$backup_path/" . --exclude="$BACKUP_DIR" --exclude=".git"

    if [ $? -eq 0 ]; then
        print_message $GREEN "备份恢复成功: $backup_name"
    else
        print_message $RED "备份恢复失败"
        exit 1
    fi
}

# 下载最新代码
download_latest() {
    print_message $BLUE "下载最新代码..."

    # 创建临时目录
    local temp_dir="/tmp/sats_download_$$"
    mkdir -p "$temp_dir"

    # 克隆最新代码
    print_message $BLUE "克隆仓库到临时目录..."
    git clone "https://gitee.com/${GITEE_USERNAME}/${REPO_NAME}.git" "$temp_dir"

    if [ $? -ne 0 ]; then
        print_message $RED "克隆失败"
        rm -rf "$temp_dir"
        exit 1
    fi

    # 计算当前目录MD5
    local current_md5=$(calculate_dir_md5 ".")
    local new_md5=$(calculate_dir_md5 "$temp_dir")

    print_message $CYAN "当前目录MD5: $current_md5"
    print_message $CYAN "最新代码MD5: $new_md5"

    if [ "$current_md5" = "$new_md5" ]; then
        print_message $GREEN "代码无变化，无需更新"
        rm -rf "$temp_dir"
        return 0
    fi

    print_message $YELLOW "检测到代码变化，准备更新..."

    # 创建备份
    create_backup

    # 备份当前文件（排除备份目录和Git目录）
    local current_backup="$BACKUP_DIR/current_$(date '+%Y%m%d_%H%M%S')"
    mkdir -p "$current_backup"
    rsync -av --exclude="$BACKUP_DIR" --exclude=".git" --exclude="*.pyc" --exclude="__pycache__" . "$current_backup/"

    # 更新文件
    print_message $BLUE "更新文件..."
    rsync -av --delete "$temp_dir/" . --exclude=".git" --exclude="$BACKUP_DIR"

    if [ $? -eq 0 ]; then
        print_message $GREEN "代码更新成功！"
        print_message $GREEN "备份位置: $current_backup"

        # 更新MD5缓存
        echo "$(date '+%Y-%m-%d %H:%M:%S'):$new_md5" > "$MD5_FILE"
    else
        print_message $RED "代码更新失败"
        exit 1
    fi

    # 清理临时目录
    rm -rf "$temp_dir"
}

# 显示状态信息
show_status() {
    print_message $GREEN "=== SATS项目状态信息 ==="

    # Git状态
    print_message $BLUE "Git状态:"
    git status --short

    # 远程仓库信息
    print_message $BLUE "远程仓库:"
    git remote -v

    # 最近提交
    print_message $BLUE "最近提交:"
    git log --oneline -5

    # 备份信息
    if [ -d "$BACKUP_DIR" ]; then
        print_message $BLUE "备份列表:"
        if [ -f "$BACKUP_DIR/backup_list.txt" ]; then
            tail -5 "$BACKUP_DIR/backup_list.txt"
        else
            echo "暂无备份记录"
        fi

        print_message $BLUE "备份文件:"
        ls -la "$BACKUP_DIR" | grep "$BACKUP_PREFIX" | tail -5
    else
        print_message $YELLOW "备份目录不存在"
    fi

    # MD5信息
    if [ -f "$MD5_FILE" ]; then
        print_message $BLUE "当前MD5缓存:"
        cat "$MD5_FILE"
    fi
}

# 推送功能
push_function() {
    print_message $GREEN "=== 开始推送代码 ==="
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

# 下载功能
pull_function() {
    print_message $GREEN "=== 开始下载最新代码 ==="
    print_message $GREEN "开始时间: $(date '+%Y-%m-%d %H:%M:%S')"
    echo

    download_latest

    print_message $GREEN "=== 下载完成 ==="
    print_message $GREEN "结束时间: $(date '+%Y-%m-%d %H:%M:%S')"
}

# 同步功能
sync_function() {
    print_message $GREEN "=== 开始同步代码 ==="
    print_message $GREEN "开始时间: $(date '+%Y-%m-%d %H:%M:%S')"
    echo

    # 先推送
    push_function

    echo
    print_message $YELLOW "等待5秒后开始下载..."
    sleep 5

    # 再下载
    pull_function

    print_message $GREEN "=== 同步完成 ==="
    print_message $GREEN "结束时间: $(date '+%Y-%m-%d %H:%M:%S')"
}

# 主函数
main() {
    # 创建备份目录
    mkdir -p "$BACKUP_DIR"

    # 处理命令行参数
    case "${1:-}" in
        push)
            push_function
            ;;
        pull)
            pull_function
            ;;
        sync)
            sync_function
            ;;
        backup)
            create_backup
            ;;
        restore)
            restore_backup "$2"
            ;;
        status)
            show_status
            ;;
        -h|--help|help)
            show_help
            ;;
        "")
            show_help
            ;;
        *)
            print_message $RED "未知命令: $1"
            show_help
            exit 1
            ;;
    esac
}

# 执行主函数
main "$@" [root@localhost sats]# vim giteerun.sh
[root@localhost sats]# cat giteerun.sh
#!/bin/bash

# SATS项目Gitee自动化脚本
# 作者: sharksafe
# 日期: 2025-08-04
# 功能: 推送代码到Gitee + 下载最新代码 + MD5检查 + 自动备份

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 加载配置文件
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR"

if [ -f "$PROJECT_ROOT/config/gitee_config.sh" ]; then
    source "$PROJECT_ROOT/config/gitee_config.sh"
elif [ -f "$PROJECT_ROOT/gitee_config.sh" ]; then
    source "$PROJECT_ROOT/gitee_config.sh"
elif [ -f "gitee_config.sh" ]; then
    source gitee_config.sh
else
    echo "错误: 找不到配置文件 gitee_config.sh"
    echo "请检查以下路径:"
    echo "  - $PROJECT_ROOT/config/gitee_config.sh"
    echo "  - $PROJECT_ROOT/gitee_config.sh"
    echo "  - 当前目录/gitee_config.sh"
    exit 1
fi

# 配置信息（从配置文件加载）
# GITEE_USERNAME, GITEE_TOKEN, REPO_NAME, REMOTE_URL 从 gitee_config.sh 加载

# 备份配置
BACKUP_DIR="backups"
BACKUP_PREFIX="sats_backup_"
MD5_FILE=".md5_cache"

# 打印带颜色的消息
print_message() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
}

# 显示帮助信息
show_help() {
    echo "用法: $0 [命令] [选项]"
    echo ""
    echo "命令:"
    echo "  push              推送代码到Gitee"
    echo "  pull              下载最新代码"
    echo "  sync              同步（推送+下载）"
    echo "  backup            创建备份"
    echo "  restore <备份名>   恢复备份"
    echo "  status            显示状态信息"
    echo ""
    echo "选项:"
    echo "  -f, --force       强制操作（不询问）"
    echo "  -q, --quiet       静默模式"
    echo "  -h, --help        显示帮助信息"
    echo ""
    echo "示例:"
    echo "  $0 push           推送代码"
    echo "  $0 pull           下载最新代码"
    echo "  $0 sync           同步代码"
    echo "  $0 push -f        强制推送"
    echo "  $0 pull -q        静默下载"
    echo ""
    echo "备份管理:"
    echo "  $0 backup         创建备份"
    echo "  $0 restore backup_20250804_194500  恢复指定备份"
    echo "  $0 status         显示状态"
}

# 计算文件MD5值
calculate_md5() {
    local file_path="$1"
    if [ -f "$file_path" ]; then
        md5sum "$file_path" | cut -d' ' -f1
    else
        echo ""
    fi
}

# 计算目录MD5值
calculate_dir_md5() {
    local dir_path="$1"
    if [ -d "$dir_path" ]; then
        find "$dir_path" -type f -exec md5sum {} \; | sort | md5sum | cut -d' ' -f1
    else
        echo ""
    fi
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

    # 检查空文件夹变化
    local new_empty_dirs=""
    for item in $(find . -type d -empty -not -path "./.git*" -not -path "./backups*" -not -path "./__pycache__*" -not -path "./node_modules*" 2>/dev/null); do
        # 检查这个文件夹是否在Git中
        if ! git ls-files --error-unmatch "$item" >/dev/null 2>&1; then
            new_empty_dirs="$new_empty_dirs $item"
        fi
    done

    if [ -z "$changed_files" ] && [ -z "$staged_files" ] && [ -z "$untracked_files" ] && [ -z "$deleted_files" ] && [ -z "$new_empty_dirs" ]; then
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
        if [ -n "$new_empty_dirs" ]; then
            print_message $CYAN "新空文件夹:"
            echo "$new_empty_dirs" | while read dir; do
                if [ -n "$dir" ]; then
                    print_message $CYAN "  - $dir"
                fi
            done
        fi
    fi
}

# 处理文件夹操作
handle_folder_operations() {
    print_message $BLUE "检查文件夹操作..."

    # 获取所有变更的文件和目录
    local changed_files=$(git diff --name-only)
    local staged_files=$(git diff --cached --name-only)
    local untracked_files=$(git ls-files --others --exclude-standard)
    local deleted_files=$(git ls-files --deleted)

    # 检查是否有文件夹被删除
    local deleted_dirs=""
    for file in $deleted_files; do
        local dir=$(dirname "$file")
        if [ "$dir" != "." ]; then
            deleted_dirs="$deleted_dirs $dir"
        fi
    done

    # 去重
    deleted_dirs=$(echo "$deleted_dirs" | tr ' ' '\n' | sort -u | tr '\n' ' ')

    # 处理删除的文件夹
    for dir in $deleted_dirs; do
        if [ -n "$dir" ] && [ "$dir" != "." ]; then
            print_message $YELLOW "检测到删除的文件夹: $dir"
            # 确保文件夹被正确删除
            if [ -d "$dir" ]; then
                print_message $BLUE "删除文件夹: $dir"
                git rm -r "$dir" 2>/dev/null || true
            fi
        fi
    done

    # 检查新创建的文件夹（包括空文件夹）
    local new_dirs=""
    for file in $untracked_files; do
        local dir=$(dirname "$file")
        if [ "$dir" != "." ]; then
            new_dirs="$new_dirs $dir"
        fi
    done

    # 检查空文件夹
    for item in $(find . -type d -empty -not -path "./.git*" -not -path "./backups*" -not -path "./__pycache__*" -not -path "./node_modules*" 2>/dev/null); do
        # 检查这个文件夹是否在Git中
        if ! git ls-files --error-unmatch "$item" >/dev/null 2>&1; then
            new_dirs="$new_dirs $item"
        fi
    done

    # 去重
    new_dirs=$(echo "$new_dirs" | tr ' ' '\n' | sort -u | tr '\n' ' ')

    # 处理新创建的文件夹
    for dir in $new_dirs; do
        if [ -n "$dir" ] && [ "$dir" != "." ]; then
            print_message $YELLOW "检测到新文件夹: $dir"
            # 确保文件夹被添加到Git
            if [ -d "$dir" ]; then
                print_message $BLUE "添加文件夹: $dir"
                git add "$dir" 2>/dev/null || true
            fi
        fi
    done

    print_message $GREEN "文件夹操作处理完成"
}

# 执行数据库备份
execute_database_backup() {
    print_message $BLUE "执行数据库备份..."

    local export_script="$PROJECT_ROOT/scripts/export_database.py"

    if [ -f "$export_script" ]; then
        if [ -x "$export_script" ]; then
            python3 "$export_script"
            if [ $? -eq 0 ]; then
                print_message $GREEN "数据库备份成功"

                # 将备份文件添加到Git
                local sql_dir="$PROJECT_ROOT/sql"
                if [ -d "$sql_dir" ]; then
                    git add "$sql_dir"/*.sql 2>/dev/null || true

                    # 检查是否有新的SQL文件需要提交
                    if ! git diff --cached --quiet -- "$sql_dir"; then
                        print_message $BLUE "自动提交数据库备份文件..."
                        git commit -m "Auto backup database $(date '+%Y-%m-%d %H:%M:%S')" -- "$sql_dir"/*.sql 2>/dev/null || true
                    fi
                fi
            else
                print_message $YELLOW "数据库备份失败，继续执行其他操作"
            fi
        else
            print_message $YELLOW "数据库导出脚本不可执行，跳过备份"
        fi
    else
        print_message $YELLOW "数据库导出脚本不存在，跳过备份"
    fi
}

# 添加变化的文件到暂存区
add_files() {
    print_message $BLUE "检查变化的文件..."

    # 获取变化的文件列表
    local changed_files=$(git diff --name-only)
    local staged_files=$(git diff --cached --name-only)
    local untracked_files=$(git ls-files --others --exclude-standard)
    local deleted_files=$(git ls-files --deleted)

    # 检查是否有新创建的空文件夹
    local new_empty_dirs=""
    for item in $(find . -type d -empty -not -path "./.git*" -not -path "./backups*" -not -path "./__pycache__*" -not -path "./node_modules*" 2>/dev/null); do
        # 检查这个文件夹是否在Git中
        if ! git ls-files --error-unmatch "$item" >/dev/null 2>&1; then
            new_empty_dirs="$new_empty_dirs $item"
        fi
    done

    if [ -z "$changed_files" ] && [ -z "$staged_files" ] && [ -z "$untracked_files" ] && [ -z "$deleted_files" ] && [ -z "$new_empty_dirs" ]; then
        print_message $YELLOW "没有检测到文件变化"
        return 0
    fi

    # 处理文件夹操作
    handle_folder_operations

    # 执行数据库备份
    execute_database_backup

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

    if [ -n "$new_empty_dirs" ]; then
        echo "$new_empty_dirs" | while read dir; do
            print_message $CYAN "  新空文件夹: $dir"
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
    # 在静默模式下，直接使用默认提交信息
    if [ "$QUIET_MODE" = "true" ]; then
        commit_message="自动提交 - $(date '+%Y-%m-%d %H:%M:%S')"
    else
        print_message $BLUE "请输入提交信息 (默认: 自动提交 - $(date '+%Y-%m-%d %H:%M:%S')):"
        read -r commit_message

        if [ -z "$commit_message" ]; then
            commit_message="自动提交 - $(date '+%Y-%m-%d %H:%M:%S')"
        fi
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

    git push -u origin "$current_branch"

    if [ $? -eq 0 ]; then
        print_message $GREEN "推送成功！"
        print_message $GREEN "仓库地址: https://gitee.com/${GITEE_USERNAME}/${REPO_NAME}"
    else
        print_message $RED "推送失败"
        exit 1
    fi
}

# 创建备份
create_backup() {
    local backup_name="${BACKUP_PREFIX}$(date '+%Y%m%d_%H%M%S')"
    local backup_path="$BACKUP_DIR/$backup_name"

    print_message $BLUE "创建备份: $backup_name"

    # 创建备份目录
    mkdir -p "$backup_path"

    # 复制文件（排除备份目录和Git目录）
    rsync -av --exclude="$BACKUP_DIR" --exclude=".git" --exclude="*.pyc" --exclude="__pycache__" . "$backup_path/"

    if [ $? -eq 0 ]; then
        print_message $GREEN "备份创建成功: $backup_path"

        # 保存备份信息
        echo "$backup_name:$(date '+%Y-%m-%d %H:%M:%S')" >> "$BACKUP_DIR/backup_list.txt"

        # 计算备份MD5
        local backup_md5=$(calculate_dir_md5 "$backup_path")
        echo "$backup_name:$backup_md5" >> "$BACKUP_DIR/backup_md5.txt"

        print_message $GREEN "备份MD5: $backup_md5"
    else
        print_message $RED "备份创建失败"
        exit 1
    fi
}

# 恢复备份
restore_backup() {
    local backup_name="$1"
    local backup_path="$BACKUP_DIR/$backup_name"

    if [ -z "$backup_name" ]; then
        print_message $RED "请指定备份名称"
        print_message $BLUE "可用备份:"
        ls -1 "$BACKUP_DIR" | grep "^$BACKUP_PREFIX" | head -10
        exit 1
    fi

    if [ ! -d "$backup_path" ]; then
        print_message $RED "备份不存在: $backup_name"
        exit 1
    fi

    print_message $YELLOW "即将恢复备份: $backup_name"
    print_message $YELLOW "这将覆盖当前文件，是否继续？(y/n)"
    read -r response
    if [[ ! "$response" =~ ^[Yy]$ ]]; then
        print_message $BLUE "取消恢复"
        exit 0
    fi

    # 创建当前状态备份
    create_backup

    # 恢复文件
    rsync -av --delete "$backup_path/" . --exclude="$BACKUP_DIR" --exclude=".git"

    if [ $? -eq 0 ]; then
        print_message $GREEN "备份恢复成功: $backup_name"
    else
        print_message $RED "备份恢复失败"
        exit 1
    fi
}

# 下载最新代码
download_latest() {
    print_message $BLUE "下载最新代码..."

    # 创建临时目录
    local temp_dir="/tmp/sats_download_$$"
    mkdir -p "$temp_dir"

    # 克隆最新代码
    print_message $BLUE "克隆仓库到临时目录..."
    git clone "https://gitee.com/${GITEE_USERNAME}/${REPO_NAME}.git" "$temp_dir"

    if [ $? -ne 0 ]; then
        print_message $RED "克隆失败"
        rm -rf "$temp_dir"
        exit 1
    fi

    # 计算当前目录MD5
    local current_md5=$(calculate_dir_md5 ".")
    local new_md5=$(calculate_dir_md5 "$temp_dir")

    print_message $CYAN "当前目录MD5: $current_md5"
    print_message $CYAN "最新代码MD5: $new_md5"

    if [ "$current_md5" = "$new_md5" ]; then
        print_message $GREEN "代码无变化，无需更新"
        rm -rf "$temp_dir"
        return 0
    fi

    print_message $YELLOW "检测到代码变化，准备更新..."

    # 创建备份
    create_backup

    # 备份当前文件（排除备份目录和Git目录）
    local current_backup="$BACKUP_DIR/current_$(date '+%Y%m%d_%H%M%S')"
    mkdir -p "$current_backup"
    rsync -av --exclude="$BACKUP_DIR" --exclude=".git" --exclude="*.pyc" --exclude="__pycache__" . "$current_backup/"

    # 更新文件
    print_message $BLUE "更新文件..."
    rsync -av --delete "$temp_dir/" . --exclude=".git" --exclude="$BACKUP_DIR"

    if [ $? -eq 0 ]; then
        print_message $GREEN "代码更新成功！"
        print_message $GREEN "备份位置: $current_backup"

        # 更新MD5缓存
        echo "$(date '+%Y-%m-%d %H:%M:%S'):$new_md5" > "$MD5_FILE"
    else
        print_message $RED "代码更新失败"
        exit 1
    fi

    # 清理临时目录
    rm -rf "$temp_dir"
}

# 显示状态信息
show_status() {
    print_message $GREEN "=== SATS项目状态信息 ==="

    # Git状态
    print_message $BLUE "Git状态:"
    git status --short

    # 远程仓库信息
    print_message $BLUE "远程仓库:"
    git remote -v

    # 最近提交
    print_message $BLUE "最近提交:"
    git log --oneline -5

    # 备份信息
    if [ -d "$BACKUP_DIR" ]; then
        print_message $BLUE "备份列表:"
        if [ -f "$BACKUP_DIR/backup_list.txt" ]; then
            tail -5 "$BACKUP_DIR/backup_list.txt"
        else
            echo "暂无备份记录"
        fi

        print_message $BLUE "备份文件:"
        ls -la "$BACKUP_DIR" | grep "$BACKUP_PREFIX" | tail -5
    else
        print_message $YELLOW "备份目录不存在"
    fi

    # MD5信息
    if [ -f "$MD5_FILE" ]; then
        print_message $BLUE "当前MD5缓存:"
        cat "$MD5_FILE"
    fi
}

# 推送功能
push_function() {
    print_message $GREEN "=== 开始推送代码 ==="
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

# 下载功能
pull_function() {
    print_message $GREEN "=== 开始下载最新代码 ==="
    print_message $GREEN "开始时间: $(date '+%Y-%m-%d %H:%M:%S')"
    echo

    download_latest

    print_message $GREEN "=== 下载完成 ==="
    print_message $GREEN "结束时间: $(date '+%Y-%m-%d %H:%M:%S')"
}

# 同步功能
sync_function() {
    print_message $GREEN "=== 开始同步代码 ==="
    print_message $GREEN "开始时间: $(date '+%Y-%m-%d %H:%M:%S')"
    echo

    # 先推送
    push_function

    echo
    print_message $YELLOW "等待5秒后开始下载..."
    sleep 5

    # 再下载
    pull_function

    print_message $GREEN "=== 同步完成 ==="
    print_message $GREEN "结束时间: $(date '+%Y-%m-%d %H:%M:%S')"
}

# 主函数
main() {
    # 创建备份目录
    mkdir -p "$BACKUP_DIR"

    # 处理命令行参数
    case "${1:-}" in
        push)
            push_function
            ;;
        pull)
            pull_function
            ;;
        sync)
            sync_function
            ;;
        backup)
            create_backup
            ;;
        restore)
            restore_backup "$2"
            ;;
        status)
            show_status
            ;;
        -h|--help|help)
            show_help
            ;;
        "")
            show_help
            ;;
        *)
            print_message $RED "未知命令: $1"
            show_help
            exit 1
            ;;
    esac
}

# 执行主函数
main "$@" 