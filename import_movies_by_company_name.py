import tornado.gen
from tornado import ioloop

from lib.logger import init_log
from service.search_online import add_company_movies_to_emdb

init_log(log_name="import_movies_by_company_name")
# language = "zh"
# country = "CN"
company_name = "儒意"


if __name__ == '__main__':
    io_loop = ioloop.IOLoop.current()
    io_loop.run_sync(lambda: add_company_movies_to_emdb(company_name))
