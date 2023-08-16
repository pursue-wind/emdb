import json
import logging

import requests
from tornado import gen

from service import handle_exceptions
from service.fetch_moive_info import Tmdb, fetch_movie_info


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
def add_movie_to_emdb(tmdb_movie_id):
    # emdb_url = "http://embd.likn.co/api/movie/add"
    emdb_url = "http://127.0.0.1:8088/api/movie/add"
    params = {"tmdb_movie_id": tmdb_movie_id}
    headers = {'Authorization': 'Basic MmdxY3ZkbGtxYnJtNTY6ZmVlZDBmMjRlMzFhMjM1Z2Q4YjdlNGJlZDFmZWM0ZGQyNjU1'}
    res = requests.post(emdb_url, data=params, headers=headers)
    print(res.content)


@gen.coroutine
def add_company_movies_to_emdb(company_name):
    """
    add movie to emdb by company name
    """

    # 1. search company by name
    results = yield search_company_by_name(company_name)
    print(f"search_company_by_name: {results}")
    companies = results.get("data")
    if not companies:
        return False
    for company in companies:
        company_tmdb_id = company.get("id")
        page = 1
        # 2. get movies by tmdb company id
        movies_result = yield search_company_movies(company_tmdb_id, page=page)
        print(f"movies_result:{movies_result}")
        if movies_result["code"] != 0:
            print(f"get movies error, company_tmdb_id:{company_tmdb_id}", company_tmdb_id)
            continue
        movies = movies_result.get("data")
        total_pages = movies["total_pages"]
        total_results = movies["total_results"]

        print(f"total_pages:{total_pages}, total_results:{total_results}, len:{len(movies['results'])}")
        # 3. add movie to emdb
        for movie in movies.get("results"):
            movie_tmdb_id = movie["id"]
            # yield fetch_movie_info(movie_tmdb_id)

            yield add_movie_to_emdb(movie_tmdb_id)

        while total_pages > 1 and total_pages > page:
            page += 1
            movies_result = yield search_company_movies(company_tmdb_id, page=page)
            movies = movies_result.get("data")
            print(f"len:{len(movies['results'])}")
            for movie in movies.get("results"):
                movie_tmdb_id = movie["id"]
                # yield fetch_movie_info(movie_tmdb_id)
                yield add_movie_to_emdb(movie_tmdb_id)
























