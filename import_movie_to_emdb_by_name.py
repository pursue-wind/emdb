import logging

import tornado.gen
from tornado import ioloop

from lib.logger import init_log
from lib.utils.excels import read_excel
from service.search_online import add_company_movies_to_emdb, search_movie_by_name, add_movie_to_emdb
from config import CFG as cfg

init_log(log_name="import_movies_by_name")
language = "zh"
# country = "CN"
file_path = "docs/movies.xlsx"


@tornado.gen.coroutine
def import_movie_by_name():
    """import movie to emdb by movie name"""
    movies = read_excel(file_path, "movies")
    emdb_base_url = cfg.server.domain
    add_movie_url = emdb_base_url + "/api/movie/add"
    # print(movies)
    for mv in movies[1:]:
        movie_name = mv[1]
        logging.info(f"******** start search movie_name:{movie_name} ********")
        # add movies to emdb
        movies = yield search_movie_by_name(movie_name, language)
        logging.info(f"******** end add movie:{movie_name} to emdb ********")
        logging.info(f"total movies：{len(movies['data'])}")
        logging.info(movies)
        for movie in movies["data"]:
            tmdb_id = movie["id"]
            yield add_movie_to_emdb(tmdb_id, add_movie_url)


if __name__ == '__main__':
    io_loop = ioloop.IOLoop.current()
    io_loop.run_sync(import_movie_by_name)
