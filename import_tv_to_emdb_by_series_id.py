from tornado import ioloop

from service.fetch_tv_series_info import get_tv_detail, import_tv_emdb_by_series_id


tmdb_series_id_list = [121012]
company_id = 100000007
if __name__ == '__main__':
    io_loop = ioloop.IOLoop.current()
    # io_loop.run_sync(lambda: get_tv_detail(122790, None))
    io_loop.run_sync(lambda: import_tv_emdb_by_series_id(tmdb_series_id_list, company_id))



