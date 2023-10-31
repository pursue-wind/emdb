import json
import logging

import requests
from tornado import ioloop, gen

from lib.utils.excels import read_excel
from service.fetch_tv_series_info import get_tv_detail
from service.search_online import search_company_by_name, add_company_movies_to_emdb
from service import Tmdb

@gen.coroutine
def import_tv_to_emdb_by_company_name():
    file_path = "docs/movies.xlsx"
    tmdb_api_key = 'fb5642b7e0b6d36ad5ebcdf78a52f14c'

    company_data = read_excel(file_path, "companys")
    for i in range(1, len(company_data)):
        company_name = company_data[i][1]
        logging.info(f"company_name:{company_name}")
        logging.info(f"******** start add tv to emdb ********")
        logging.info(f"search company：{company_name}")
        companyies = yield search_company_by_name(company_name)
        logging.info(f"companyies:{companyies}")

        if companyies["code"] != 0:
            continue
        if not companyies["data"]:
            logging.info(f"{company_name} :Do Not Find The Company")
            continue
        company_ids = list()
        # total_result1 = 0
        for company in companyies["data"]:
            company_id = company["id"]
            company_ids.append(company_id)

            page = 1
            tmdb = Tmdb()
            company_tv_result = tmdb.discover_company_tv(with_companies=company_ids, page=page)
            total_result = company_tv_result["total_results"]
            total_pages = company_tv_result["total_pages"]
            print(f"Search Company's Tv result：{company_tv_result}")
            print(f"total_result:{total_result},total_pages:{total_pages} ")
            if total_result == 0:
                continue
            company_ts_shows = company_tv_result["results"]
            for tv in company_ts_shows:
                tmdb_tv_series_id = tv["id"]
                logging.info(f"tmdb_tv_series_id:{tmdb_tv_series_id}")
                yield get_tv_detail(tmdb_tv_series_id)
            while total_pages > 1 and total_pages > page:
                page += 1
                company_tv_result = tmdb.discover_company_tv(with_companies=company_ids, page=page)
                company_ts_shows = company_tv_result["results"]
                for tv in company_ts_shows:
                    tmdb_tv_series_id = tv["id"]
                    logging.info(f"tmdb_tv_series_id:{tmdb_tv_series_id}")
                    yield get_tv_detail(tmdb_tv_series_id)


if __name__ == '__main__':
    io_loop = ioloop.IOLoop.current()
    io_loop.run_sync(import_tv_to_emdb_by_company_name)