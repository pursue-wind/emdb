from tornado import ioloop

from service.fetch_tv_series_info import get_tv_detail, import_tv_emdb_by_series_id


tmdb_series_id_list = [118357, 157732, 117488, 52814, 238312, 56295, 77184, 234785, 61634, 60879, 61736, 48080, 204103, 129506, 38493, 54400, 230986, 99966, 235249, 133490, 4920, 3810, 2211, 66871, 1274, 84847, 126443, 1663, 28160, 210200, 100565, 17789, 95555, 28681, 114730, 63927, 229876, 96704, 59104, 13833, 60909, 62522, 224231, 43982, 154379, 123343, 43499, 39628]
company_id = 100000002
if __name__ == '__main__':
    io_loop = ioloop.IOLoop.current()
    # io_loop.run_sync(lambda: get_tv_detail(122790, None))
    io_loop.run_sync(lambda: import_tv_emdb_by_series_id(tmdb_series_id_list, company_id))



