#!/bin/bash
export WORKON_HOME=$HOME/.virtualenvs
export VIRTUALENVWRAPPER_PYTHON=/usr/local/bin/python3.9
source /usr/local/bin/virtualenvwrapper.sh

APP_NAME="emdb"
APP_PATH="/data/emdb/emdb"
LOGPATH="/data/emdb/logs/start.log"

VENV_NAME="emdb"

start() {
    workon "$VENV_NAME"  # 切换到虚拟环境

    pip install -r requirements.txt

    echo "work in VENV: $VENV_NAME, ENV: $ENV"
    if [ "$2" = "main" ]; then
        cd "$APP_PATH" || exit
        python3 main.py  >$LOGPATH 2>&1 &
        echo "Started $APP_NAME"
    elif [ "$2" = "run_sync" ]; then
        cd "$APP_PATH" || exit
        python3 run_sync.py >/dev/null 2>&1 &
        echo "Started run_sync"
    elif [ "$2" = "all" ]; then
      cd "$APP_PATH" || exit
      python3 main.py  >/dev/null 2>&1 &
      echo "Started $APP_NAME"
      python3 run_sync.py  >/dev/null 2>&1 &
      echo "Started run_sync"
    else
        echo "Invalid process specified"
        exit 1
    fi
}
stop() {
    if [ "$2" = "main" ]; then
        pkill -f "python3 main.py"
        echo "Stopped $APP_NAME"
    elif [ "$2" = "run_sync" ]; then
        pkill -f "python3 run_sync.py"
        echo "Stopped run_sync"
    elif [ "$2" = "all" ]; then
      pkill -f "python3 main.py"
      echo "Stopped $APP_NAME"
      pkill -f "python3 run_sync.py"
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
    if [ "$2" = "main" ] && pgrep -f "python3 main.py" >/dev/null; then
        echo "$APP_NAME is running"
    elif [ "$2" = "run_sync" ] && pgrep -f "python3 run_sync.py" >/dev/null; then
        echo "run_sync is running"
    elif [ "$2" = "all" ] && pgrep -f "python3 main.py" >/dev/null && pgrep -f "python3 run_sync.py" >/dev/null; then
        echo "$APP_NAME and run_sync are running"
    else
        echo "Process is not running"
    fi
}

case "$1" in
    start)
        start "$@" ;;
    stop)
        stop "$@" ;;
    restart)
        restart "$@" ;;
    status)
        status "$@" ;;
    *)
        echo "Usage: $0 {start|stop|restart|status} {main|run_sync|all}"
        exit 1 ;;
esac