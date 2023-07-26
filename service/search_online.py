import logging

import requests
from tornado import gen

from service import handle_exceptions
from service.fetch_moive_info import Tmdb


@gen.coroutine
@handle_exceptions
def search_company_movies(company_id):
    e_tmdb = Tmdb()
    company = e_tmdb.company(company_id)
    movies = company.movies()
    return movies

