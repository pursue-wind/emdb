from tornado import ioloop

from lib.logger import init_log
from tasks.fetch_event_log import fetch_event_log

init_log(log_name="run_sync")

if __name__ == '__main__':
    io_loop = ioloop.IOLoop.current()
    io_loop.run_sync(fetch_event_log)
