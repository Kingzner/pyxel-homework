#!/bin/zsh
set -eu
task_project_dir="$(cd -- "$(dirname -- "$0")" && pwd)"
cd "$task_project_dir"

if [[ ! -x .venv/bin/python ]]; then
    print '请先按 README 的环境说明创建 .venv，再双击 play.command。'
    exit 1
fi

exec .venv/bin/python -m game.main
