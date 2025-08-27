#!/bin/bash

# Gitee配置文件
# 请根据实际情况修改以下配置

# Gitee账户信息
GITEE_USERNAME="dony"
GITEE_TOKEN="947bcda7efac65d5cd6c234098d6a764"
REPO_NAME="sost"

# 远程仓库URL
REMOTE_URL="https://${GITEE_USERNAME}:${GITEE_TOKEN}@gitee.com/${GITEE_USERNAME}/${REPO_NAME}.git"

# 导出变量供其他脚本使用
export GITEE_USERNAME
export GITEE_TOKEN
export REPO_NAME
export REMOTE_URL