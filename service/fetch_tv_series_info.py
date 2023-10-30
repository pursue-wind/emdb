from tornado import ioloop, gen
from tornado.log import app_log
import db.pgsql.movies as mv
import db.pgsql.tv_seasons as tv_seasons
import db.pgsql.tv_series_additional as tv_series
from db.pgsql.tv_episodes import insert_tv_episodes_list
from service import Tmdb


@gen.coroutine
def get_tv_detail(tmdb_series_id, lang=None, country=None):
    """
    get tv series deatil
    """
    if lang is None or country is None:
        language = None
    else:
        language = lang.lower() + "-" + country.upper()

    e_tmdb = Tmdb()
    img_base_url = e_tmdb.IMAGE_BASE_URL
    tv = e_tmdb.tv_series(tmdb_series_id)
    tv_series_detail = tv.info(language=language)
    print(tv_series_detail)
    # external ids
    external_ids = tv.external_ids()
    emdb_movie_id = 0
    for season_info in tv_series_detail["seasons"]:
        tv_detail = parse_tv_detail(tv_series_detail, season_info, external_ids, img_base_url)

        # 1.insert tv season detail to movie
        res = yield mv.insert_movies(tv_detail)
        print(f"insert movie table res：{res}")
        if res["status"] == 1:
            _movie_info = yield mv.query_movie_by_tmdb_id(tv_detail)
            emdb_movie_id = _movie_info["data"]["movie_info"].get("id")
        elif res["status"] == 0:
            emdb_movie_id = res["data"]["movie_id"]
        else:
            app_log.error(f"insert movie error: {res}")
            return
        # 2. insert tv adddition_info
        tv_additional_info = parse_tv_adddition_info(tv_series_detail)
        tv_additional_info["external_ids"] = external_ids
        res = yield tv_series.insert_tv_additional_info(tv_additional_info)
        print(f"insert_tv_additional_info res:{res}")

    if emdb_movie_id == 0:
        return
    # 4.insert seasons info
    tv_seasons_info = tv_series_detail["seasons"]
    for season_info in tv_seasons_info:
        tv_season_obj = e_tmdb.tv_season(tv_series_detail["id"], season_info["season_number"])
        tv_season_external_ids = tv_season_obj.external_ids()
        season_info["external_ids"] = tv_season_external_ids

        # 5. insert episodes
        season_episode_info = tv_season_obj.info()
        episodes_info = season_episode_info["episodes"]
        episodes = parse_tv_episode_info(episodes_info, tmdb_series_id, season_info["id"], img_base_url)
        yield insert_tv_episodes_list(episodes)

        # 6.credits
        credits = tv_season_obj.credits()



    yield save_tv_seasons_info(tv_seasons_info, emdb_movie_id, img_base_url)



def parse_tv_episode_info(season_episode_info, tmdb_series_id, tmdb_season_id, img_base_url):
    episodes = list()
    for episode_info in season_episode_info:
        print(episode_info["still_path"])
        if episode_info["still_path"]:
            still_path = img_base_url+episode_info["still_path"]
        else:
            still_path = None
        single_epidose = {
            'tmdb_series_id': tmdb_series_id,
            'tmdb_season_id': tmdb_season_id,
            'tmdb_episode_id': episode_info["id"],
            'air_date': episode_info["air_date"],
            'episode_number': episode_info["episode_number"],
            'episode_type': episode_info["episode_type"],
            'name': episode_info["name"],
            'overview': episode_info["overview"],
            'production_code': episode_info["production_code"],
            'runtime': episode_info["runtime"],
            'season_number': episode_info["season_number"],
            'still_path': still_path,
            'vote_average': episode_info["vote_average"],
            'vote_count': episode_info["vote_count"]
        }
        episodes.append(single_epidose)
    return episodes



@gen.coroutine
def save_tv_seasons_info(tv_seasons_info, emdb_movie_id, img_base_url):
    tv_seasons_list = list()
    for season in tv_seasons_info:
        season["season_id"] = emdb_movie_id
        season["tmdb_season_id"] = season["id"]
        season["poster_path"] = img_base_url + season["poster_path"]
        del season["id"]
        del season["poster_path"]
        del season["vote_average"]
        tv_seasons_list.append(season)
    res = yield tv_seasons.insert_tv_seasons(tv_seasons_list)
    print(f"insert_tv_seasons res:{res}")


def parse_tv_adddition_info(tv_series_detail):
    tv_detail = dict()
    tv_detail["tmdb_series_id"] = tv_series_detail["id"]
    tv_detail["created_by"] = tv_series_detail.get("created_by")
    tv_detail["episode_run_time"] = tv_series_detail.get("episode_run_time")
    tv_detail["first_air_date"] = tv_series_detail.get("first_air_date")
    tv_detail["in_production"] = tv_series_detail.get("in_production")
    tv_detail["last_air_date"] = tv_series_detail.get("last_air_date")
    tv_detail["last_episode_to_air"] = tv_series_detail.get("last_episode_to_air")
    tv_detail["networks"] = tv_series_detail.get("networks")
    tv_detail["number_of_episodes"] = tv_series_detail.get("number_of_episodes")
    tv_detail["number_of_seasons"] = tv_series_detail.get("number_of_seasons")
    tv_detail["type"] = tv_series_detail.get("type")
    tv_detail["overview"] = tv_series_detail.get("overview")
    return tv_detail


def parse_tv_detail(tv_series_detail, season_info, external_ids, img_base_url):
    tv_detail = dict()
    tv_detail["tmdb_id"] = season_info["id"]

    tv_detail["tmdb_series_id"] = tv_series_detail["id"]
    if tv_series_detail["backdrop_path"]:
        tv_detail["backdrop_path"] = img_base_url + tv_series_detail["backdrop_path"]
    if tv_series_detail["poster_path"]:
        tv_detail["poster_path"] = img_base_url + season_info["poster_path"]
    tv_detail["external_ids"] = external_ids

    genres = tv_series_detail.get("genres")  # 电影类型，喜剧、动作等
    production_companies = tv_series_detail.get("production_companies")
    production_countries = tv_series_detail.get("production_countries")
    spoken_languages = tv_series_detail.get("spoken_languages")

    genres_ids = [item["id"] for item in genres]
    production_company_ids = [item["id"] for item in production_companies]
    spoken_languages_iso6391 = [item["iso_639_1"] for item in spoken_languages]
    production_country_ids = [item["iso_3166_1"] for item in production_countries]
    tv_detail["genres"] = genres_ids
    tv_detail["production_companies"] = production_company_ids
    tv_detail["production_countries"] = production_country_ids
    tv_detail["spoken_languages"] = spoken_languages_iso6391
    tv_detail["adult"] = tv_series_detail.get("adult")
    tv_detail["title"] = tv_series_detail.get("name")
    # tv_detail["backdrop_path"] = tv_series_detail.get("backdrop_path")
    tv_detail["budget"] = tv_series_detail.get("budget")
    tv_detail["homepage"] = tv_series_detail.get("homepage")
    tv_detail["original_language"] = tv_series_detail.get("original_language")
    tv_detail["original_title"] = tv_series_detail.get("original_name")
    tv_detail["popularity"] = tv_series_detail.get("popularity")
    # tv_detail["poster_path"] = tv_series_detail.get("poster_path")
    tv_detail["revenue"] = tv_series_detail.get("revenue")
    tv_detail["runtime"] = tv_series_detail["episode_run_time"][0]
    tv_detail["status"] = tv_series_detail.get("status")
    tv_detail["tagline"] = tv_series_detail.get("tagline")
    tv_detail["vote_count"] = tv_series_detail.get("vote_count")
    tv_detail["release_date"] = season_info["air_date"]
    tv_detail["vote_average"] = season_info.get("vote_average")
    tv_detail["overview"] = season_info.get("overview")
    return tv_detail
