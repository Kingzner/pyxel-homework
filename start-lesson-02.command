#!/bin/zsh
set -eu
task_project_dir="$(cd -- "$(dirname -- "$0")" && pwd)"
cd "$task_project_dir"

if [[ ! -x .venv/bin/python ]]; then
    print '还没有准备好 Python 环境，请按 README 中的步骤创建 .venv。'
    exit 1
fi

exec .venv/bin/python lessons/lesson_02.py
