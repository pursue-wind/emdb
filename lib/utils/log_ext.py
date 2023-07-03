# -*-coding:UTF-8-*-
import logging
import os
import time


class Logger(object):
    """
    终端打印不同颜色的日志，在pycharm中如果强行规定了日志的颜色， 这个方法不会起作用， 但是
    对于终端，这个方法是可以打印不同颜色的日志的。
    """

    # 在这里定义StreamHandler，可以实现单例， 所有的logger()共用一个StreamHandler
    ch = logging.StreamHandler()

    def __init__(self):
        self.logger = logging.getLogger()
        if not self.logger.handlers:
            # 如果self.logger没有handler， 就执行以下代码添加handler
            self.logger.setLevel(logging.INFO)
            # from serviceProgram.utils.FileUtil import FileUtil
            # rootPath = FileUtil.getProgrameRootPath()
            self.log_path = os.path.join(os.path.dirname(__file__), '../../../logs')

            if not os.path.exists(self.log_path):
                os.makedirs(self.log_path)
            print(self.log_path)
            # 创建一个handler,用于写入日志文件
            # fh = logging.FileHandler(self.log_path + '/run_sync' + '.log.' + time.strftime("%Y-%m-%d", time.localtime()),
            #                          encoding='utf-8')
            fh = logging.FileHandler(self.log_path + '/run_sync' + '.log', encoding='utf-8')
            fh.setLevel(logging.INFO)
            # 定义handler的输出格式
            formatter = logging.Formatter('%(asctime)s %(levelname)1.1s %(message)s')
            fh.setFormatter(formatter)
            # 给logger添加handler
            self.logger.addHandler(fh)

    def debug(self, message):
        self.fontColor('\033[0;32m%s\033[0m')
        self.logger.debug(message)

    def info(self, message):
        self.fontColor('\033[0;34m%s\033[0m')
        self.logger.info(message)

    def warning(self, message):
        self.fontColor('\033[0;37m%s\033[0m')
        self.logger.warning(message)

    def error(self, message):
        self.fontColor('\033[0;31m%s\033[0m')
        self.logger.error(message)

    def critical(self, message):
        self.fontColor('\033[0;35m%s\033[0m')
        self.logger.critical(message)

    def fontColor(self, color):
        # 不同的日志输出不同的颜色
        formatter = logging.Formatter(color % '[%(asctime)s] - [%(levelname)s] - %(message)s')
        self.ch.setFormatter(formatter)
        self.logger.addHandler(self.ch)


logger = Logger()

