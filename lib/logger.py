# coding:utf-8
import os
import sys
import logging
import tornado
from tornado.options import options
from config.config import CFG as cfg

def dump(sign, color, show_all, *args):
    sys.stdout.write(f'\n\033[0;{color}m')
    for arg in args:
        if show_all:
            sys.stdout.write('\n' + arg)
        else:
            sys.stdout.write('\n' + arg[:1000])
            if len(arg) > 1000:
                sys.stdout.write(' ...')
    sys.stdout.write(f'\n\033[0m')
    sys.stdout.flush()


def dump_in(*args):
    dump('<', 32, False, *args)


def dump_out(*args):
    dump('>', 33, False, *args)


def dump_error(*args):
    dump('%', 31, True, *args)


class LogFormatter(tornado.log.LogFormatter):
    def __init__(self):
        super(LogFormatter, self).__init__(
            fmt='%(color)s %(asctime)s %(levelname)1.1s %(end_color)s  %(message)s',
            # fmt="\033[0;33m[%(levelname)1.1s %(asctime)s %(module)s:%(lineno)d]%(end_color)s %(message)s",
            datefmt='%Y-%m-%d %H:%M:%S',
            color=True
        )
        logging.basicConfig(stream=sys.stdout, level=logging.INFO)


def init_log():
    options.logging = cfg.log.level
    options.log_file_prefix = os.path.join(os.path.dirname(__file__), '../../logs/tornado_main.log')  # 存储路径
    options.log_rotate_mode = "time"  # 切割方式：按时间
    options.log_rotate_when = "D"  # 切割单位：天
    options.log_rotate_interval = 1  # 间隔值：1天
    options.log_to_stderr = True   # 输出到控制台
    options.parse_command_line()
    # [handler.setFormatter(LogFormatter()) for handler in logging.getLogger().handlers]  # 自定义格式化日志， 必须放在 配置解析 后
    logging.getLogger().handlers[0].setFormatter(LogFormatter())

