import json
import logging
import time

import tornado.gen
from tornado import ioloop

from service import Tmdb

from lib.logger import init_log
from lib.utils.excels import read_excel
from service.search_online import search_company_by_name, add_company_movies_to_emdb
import requests

init_log(log_name="import-company_to_emmai")

file_path = "docs/movies.xlsx"
emmai_server_base_url = "https://emmai-api.likn.co"
# emmai_server_base_url = "http://localhost:8000"


@tornado.gen.coroutine
def add_companies_to_emmai():
    add_company_url = "/api/v1/company/import"
    company_data = read_excel(file_path, "companys")

    url = emmai_server_base_url + add_company_url
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
                company = {}
                company["country"] = comp["origin_country"]
                company["location"] = None
                company["title"] = comp["name"]
                company["sourceId"] = str(comp["id"])
                if comp["logo_path"]:
                    logo_path = Tmdb.IMAGE_BASE_URL + comp["logo_path"]
                else:
                    logo_path = None
                company["logoImage"] = logo_path
                company_list.append(company)
            logging.info(f"company_list:{company_list}")

            data = {"productionCompanies": company_list}
            res = requests.post(url, json=data, headers=headers)
            logging.info(res.text)


if __name__ == '__main__':
    io_loop = ioloop.IOLoop.current()
    io_loop.run_sync(lambda: add_companies_to_emmai())