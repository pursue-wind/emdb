import tmdbsimple as tmdb
import requests
import functools
import requests.exceptions
import logging


class Tmdb:
    """
    Get moive info from tmdb
    """
    IMAGE_BASE_URL = "https://image.tmdb.org/t/p/original"
    # tmdb.API_KEY = "fb5642b7e0b6d36ad5ebcdf78a52f14c"
    tmdb.API_KEY = "f7cae5cb2f797c78f8efd0e550c182a6"
    tmdb.REQUESTS_TIMEOUT = 10
    tmdb.REQUESTS_SESSION = requests.Session()
    search = tmdb.Search()
    discover = tmdb.Discover()
    tmdb = tmdb

    def discover_company_tv(self, **kwargs):
        tv_series = self.discover.tv(**kwargs)
        return tv_series

    def tv_series(tv_series_id):
        _tv_series = tmdb.TV(tv_series_id)
        return _tv_series

    def tv_season(self, tv_series_id, season_number):
        _tv_seasons = tmdb.TV_Seasons(tv_series_id, season_number)
        return _tv_seasons

    def moive(self, moive_id):
        _movie = tmdb.Movies(moive_id)
        return _movie

    def company(self, compony_id):
        _company = tmdb.Companies(compony_id)
        return _company

    def search_moive(self, **kwargs):
        res_list = self.search.movie(**kwargs)
        return res_list

    def search_company(self, **kwargs):
        res_list = self.search.company(**kwargs)
        return res_list


def handle_exceptions(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
            return {"code": 0, "data": result}
        except requests.exceptions.HTTPError as e:
            logging.error(f"HTTPError: {e}")
            if e.response is not None:
                status_code = e.response.status_code
                logging.error(f"Status Code: {status_code}")
            return {"code": e.response.status_code if e.response is not None else -1}
        except Exception as e:
            logging.error(f"Unhandled Exception: {e}")
            return {"code": 500}

    return wrapper
