import json
import logging
import time

import tornado.gen
from tornado import ioloop

from lib.logger import init_log
from lib.utils.excels import read_excel
from service.search_online import search_company_by_name, add_company_movies_to_emdb

init_log(log_name="import-movie")

file_path = "docs/movies.xlsx"
# emmai_server_base_url = "https://emmai-api.likn.co"
emmai_server_base_url = "https://api.emmai.com"
# emmai_server_base_url = "http://localhost:8000"


"""
import movie to emdb by company name
"""
@tornado.gen.coroutine
def import_movie_to_emdb():
    # company_list = []
    # add_company_url = "/api/v1/company/import"
    company_data = read_excel(file_path, "companys")
    for i in range(1, len(company_data)):
        company_name = company_data[i][1]
        logging.info(f"company_name:{company_name}")
        logging.info(f"******** start add movie to emdb ********")
        # add company's movies to emdb
        yield add_company_movies_to_emdb(company_name)
        logging.info(f"******** end add movie to emdb ********")


if __name__ == '__main__':
    io_loop = ioloop.IOLoop.current()
    io_loop.run_sync(lambda: import_movie_to_emdb())