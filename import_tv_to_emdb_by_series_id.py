from tornado import ioloop

from service.fetch_tv_series_info import get_tv_detail


if __name__ == '__main__':
    io_loop = ioloop.IOLoop.current()
    io_loop.run_sync(lambda: get_tv_detail(84958))