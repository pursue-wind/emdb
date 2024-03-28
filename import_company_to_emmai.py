import json
import logging
import time

import tornado.gen
from tornado import ioloop

from service import Tmdb
from config.config import CFG as cfg
from lib.logger import init_log
from lib.utils.excels import read_excel
from service.search_online import search_company_by_name, add_company_movies_to_emdb, search_company_movies
import requests

init_log(log_name="import-company_to_emmai")

file_path = "docs/movies.xlsx"
# emmai_server_base_url = "https://emmai-api.likn.co"
# emmai_server_base_url = "https://api.emmai.com"

# emmai_server_base_url = "http://localhost:8000"


@tornado.gen.coroutine
def add_companies_to_emmai():
    add_company_url = "/api/v1/company/import"
    company_data = read_excel(file_path, "newcpy")

    url = cfg.emmai.base_url + add_company_url
    print(f"request url:{url}")
    headers = {"Content-Type": "application/json"}

    for i in range(1, len(company_data)):
        company_name = company_data[i][1]
        logging.info(f"company_name:{company_name}")
        company_info = yield search_company_by_name(company_name)

        if company_info:
            companies = company_info.get("data")
            logging.info(f"companies:{companies}")
            if not companies:
                continue

            company_list = []
            for comp in companies:
                company_tmdb_id = comp.get("id")
                comp_name = comp["name"]
                movies_result = yield search_company_movies(company_tmdb_id)
                logging.info(f"movies_result:{movies_result}")
                if movies_result["code"] != 0:
                    logging.info(f"get movies error, company_tmdb_id:{company_tmdb_id}", company_tmdb_id)
                    continue
                movies = movies_result.get("data")
                # total_pages = movies["total_pages"]
                total_results = movies["total_results"]
                if total_results == 0:
                    print(f"company：{comp_name} has no movies")
                    continue
                company = {}
                company["country"] = comp["origin_country"]
                company["location"] = None
                company["title"] = comp_name
                company["sourceId"] = str(comp["id"])
                if comp["logo_path"]:
                    logo_path = Tmdb.IMAGE_BASE_URL + comp["logo_path"]
                else:
                    logo_path = None
                company["logoImage"] = logo_path
                company_list.append(company)
            logging.info(f"company_list:{company_list}")
            if len(company_list) > 0:
                data = {"productionCompanies": company_list}
                res = requests.post(url, json=data, headers=headers)
                logging.info(res.text)

def remove_empty_company(company_name):
    results = yield search_company_by_name(company_name)
    logging.info(f"search_company_by_name: {results}")
    companies = results.get("data")
    if not companies:
        return False
    for company in companies:
        company_tmdb_id = company.get("id")
        # page = 1
        # 2. get movies by tmdb company id
        movies_result = yield search_company_movies(company_tmdb_id)
        logging.info(f"movies_result:{movies_result}")
        if movies_result["code"] != 0:
            logging.info(f"get movies error, company_tmdb_id:{company_tmdb_id}", company_tmdb_id)
            continue
        movies = movies_result.get("data")
        # total_pages = movies["total_pages"]
        total_results = movies["total_results"]
        if total_results == 0:
            return


## import company to emmai by company name
if __name__ == '__main__':
    io_loop = ioloop.IOLoop.current()
    io_loop.run_sync(lambda: add_companies_to_emmai())