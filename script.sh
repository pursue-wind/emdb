#!/bin/bash
export WORKON_HOME=$HOME/.virtualenvs
export VIRTUALENVWRAPPER_PYTHON=/usr/bin/python3
source /usr/local/bin/virtualenvwrapper.sh

APP_NAME="event-tracker"
APP_PATH="/data/event-tracker/event-tracker"

VENV_NAME="event-tracker"

start() {

    workon "$VENV_NAME"  # 切换到虚拟环境

    if [ "$2" = "main" ]; then
        cd "$APP_PATH" || exit
        python3 main.py &
        echo "Started $APP_NAME"
    elif [ "$2" = "run_sync" ]; then
        cd "$APP_PATH" || exit
        python3 run_sync.py &
        echo "Started run_sync"
    else
        echo "Invalid process specified"
        exit 1
    fi
}

stop() {
    if [ "$2" = "main" ]; then
        pkill -f "python main.py"
        echo "Stopped $APP_NAME"
    elif [ "$2" = "run_sync" ]; then
        pkill -f "python run_sync.py"
        echo "Stopped run_sync"
    else
        echo "Invalid process name"
        exit 1
    fi
}

restart() {
    stop "$2"
    start "$2"
}

status() {
    if [ "$2" = "main" ] && pgrep -f "python main.py" >/dev/null; then
        echo "$APP_NAME is running"
    elif [ "$2" = "run_sync" ] && pgrep -f "python run_sync.py" >/dev/null; then
        echo "run_sync is running"
    elif [ "$2" = "all" ] && pgrep -f "python main.py" >/dev/null && pgrep -f "python run_sync.py" >/dev/null; then
        echo "$APP_NAME and run_sync are running"
    else
        echo "Process is not running"
    fi
}
