from tornado import ioloop
from tasks.fetch_event_log import fetch_event_log

if __name__ == '__main__':
    io_loop = ioloop.IOLoop.current()
    io_loop.run_sync(fetch_event_log)
