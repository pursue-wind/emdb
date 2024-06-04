import logging

import requests
from tornado import gen

from service import handle_exceptions
from service.fetch_moive_info import Tmdb, fetch_movie_info
from config.config import CFG as cfg


@gen.coroutine
@handle_exceptions
def search_movie_by_name(movie_name, lang='en', page=1, typ=1):
    e_tmdb = Tmdb()
    search_method = e_tmdb.search.movie if typ is None or typ == 1 else e_tmdb.search.tv
    result = search_method(language=lang, query=movie_name, page=page)

    # logging.info(f"search movies results:{result}")
    # result:{'page': 1, 'results': [], 'total_pages': 1, 'total_results': 0}
    movies = result.get("results", [])
    if not movies:
        return []
    total_results = result.get("total_results")
    total_pages = result.get("total_pages")
    page = result.get("page")
    # logging.info(f"current page: {page}, total_pages:{total_pages}, total_results:{total_results}")
    while total_pages and page < total_pages:
        page += 1
        result = e_tmdb.search.movie(language=lang, query=movie_name, page=page)
        # logging.info(f"search movies results:{result}")
        # result:{'page': 1, 'results': [], 'total_pages': 1, 'total_results': 0}
        next_page_movies = result.get("results", [])
        # logging.info(f"current_page:{page}, result:{next_page_movies}")
        movies.extend(next_page_movies)
    return movies


@gen.coroutine
@handle_exceptions
def search_company_by_name(company_name):
    e_tmdb = Tmdb()
    result = e_tmdb.search_company(query=company_name)
    companies = result.get("results")
    if not companies:
        return None
    return companies


@gen.coroutine
@handle_exceptions
def search_company_movies(company_id, **kwargs):
    e_tmdb = Tmdb()
    company = e_tmdb.company(company_id)
    movies = company.movies(**kwargs)
    return movies


@gen.coroutine
def add_movie_to_emdb(tmdb_movie_id, emdb_url, company_id=None):
    # # emdb_url = "https://embd.likn.co/api/movie/add"
    # emdb_url = "https://emdb.emmai.com/api/movie/add"
    # # emdb_url = "http://127.0.0.1:8088/api/movie/add"
    params = {"tmdb_movie_id": tmdb_movie_id, "company_id": company_id}
    headers = {'Authorization': 'Basic MmdxY3ZkbGtxYnJtNTY6ZmVlZDBmMjRlMzFhMjM1Z2Q4YjdlNGJlZDFmZWM0ZGQyNjU1'}
    res = requests.post(emdb_url, data=params, headers=headers)
    logging.info(f"add movie response: {res.text}")


@gen.coroutine
def add_company_movies_to_emdb(company_name):
    """
    add movie to emdb by company name
    """
    emdb_add_movie_url = cfg.server.domain + "/api/movie/add"
    # 1. search company by name
    results = yield search_company_by_name(company_name)
    logging.info(f"search_company_by_name: {results}")
    companies = results.get("data")
    if not companies:
        return False
    for company in companies:
        company_tmdb_id = company.get("id")
        page = 1
        # 2. get movies by tmdb company id
        movies_result = yield search_company_movies(company_tmdb_id, page=page)
        logging.info(f"movies_result:{movies_result}")
        if movies_result["code"] != 0:
            logging.info(f"get movies error, company_tmdb_id:{company_tmdb_id}", company_tmdb_id)
            continue
        movies = movies_result.get("data")
        total_pages = movies["total_pages"]
        total_results = movies["total_results"]

        logging.info(f"total_pages:{total_pages}, total_results:{total_results}, len:{len(movies['results'])}")
        # 3. add movie to emdb
        for movie in movies.get("results"):
            movie_tmdb_id = movie["id"]
            # yield fetch_movie_info(movie_tmdb_id)

            yield add_movie_to_emdb(movie_tmdb_id, emdb_add_movie_url)

        while total_pages > 1 and total_pages > page:
            page += 1
            movies_result = yield search_company_movies(company_tmdb_id, page=page)
            movies = movies_result.get("data")
            logging.info(f"len:{len(movies['results'])}")
            for movie in movies.get("results"):
                movie_tmdb_id = movie["id"]
                # yield fetch_movie_info(movie_tmdb_id)
                yield add_movie_to_emdb(movie_tmdb_id, emdb_add_movie_url)
