import logging

import tornado.gen
from tornado import ioloop

from lib.logger import init_log
from lib.utils.excels import read_excel
from service.fetch_moive_info import fetch_movie_info
from service.search_online import add_company_movies_to_emdb, search_movie_by_name, add_movie_to_emdb
from config import CFG as cfg

init_log(log_name="import_movies_by_name")
language = "zh"
# country = "CN"
file_path = "docs/movies.xlsx"
sheet_name = "movie"

# @tornado.gen.coroutine
# def import_movie_by_name(company_id=None):
#     # company_id = 88888888
#
#     """import movie to emdb by movie name"""
#     movies = read_excel(file_path, sheet_name)
#     emdb_base_url = cfg.server.domain
#     # add_movie_url = emdb_base_url + "/api/movie/add"
#     # print(movies)
#     ids = [movie_id[0] for movie_id in movies[1:]]
#     for mv in movies[1:]:
#         movie_name = mv[1]
#         # logging.info(f"******** start search movie_name:{movie_name} ********")
#         # add movies to emdb
#         movies = yield search_movie_by_name(movie_name, language)
#         # logging.info(f"******** end add movie:{movie_name} to emdb ********")
#         # logging.info(f"total movies：{len(movies['data'])}")
#         for movie in movies["data"]:
#             tmdb_id = movie["id"]
#             if tmdb_id in ids:
#                 logging.info(f"success:{tmdb_id}")
#                 yield fetch_movie_info(tmdb_id, company_id,language

@tornado.gen.coroutine
def import_movie_by_ids(company_id=None):
    # company_id = 88888888

    """import movie to emdb by movie name"""
    movies = read_excel(file_path, sheet_name)
    emdb_base_url = cfg.server.domain
    # add_movie_url = emdb_base_url + "/api/movie/add"
    # print(movies)
    ids = [movie_id[0] for movie_id in movies[1:]]
    for mvId in ids:
        yield fetch_movie_info(mvId, company_id,language)

if __name__ == '__main__':
    company_id = None
    io_loop = ioloop.IOLoop.current()
    # io_loop.run_sync(lambda: import_movie_by_name(company_id))
    io_loop.run_sync(lambda: import_movie_by_ids(company_id))


