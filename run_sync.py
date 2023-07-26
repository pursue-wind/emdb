from tornado import ioloop

from lib.logger import init_log
from service.fetch_moive_info import fetch_movie_info


init_log(log_name="run_sync")
movie_id = 758893
language = "zh"
country = "CN"
if __name__ == '__main__':
    io_loop = ioloop.IOLoop.current()
    io_loop.run_sync(lambda: fetch_movie_info(movie_id, language, country))
