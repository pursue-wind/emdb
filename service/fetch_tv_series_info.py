from tornado import gen
from tornado.log import app_log
import db.pgsql.movies as mv
import db.pgsql.tv_seasons as tv_seasons
import db.pgsql.tv_series_additional as tv_series
from db.pgsql.enums import enums
from db.pgsql.enums.enums import CreditType, ImagesType, SourceType
from db.pgsql.movie_alternative_titles import insert_movie_alternative_titles
from db.pgsql.movie_credits import insert_movie_credits, query_movie_credit_by_tmdb_id
from db.pgsql.movie_credits_relations import insert_batch_movie_credits_relation
from db.pgsql.movie_images import insert_movie_images
from db.pgsql.movie_key_words import insert_movie_key_words
from db.pgsql.movie_release_dates import insert_movie_release_dates
from db.pgsql.production_company import batch_insert_production_company
from db.pgsql.tv_episodes import insert_tv_episodes_list
from service import Tmdb
from service.fetch_moive_info import parse_credit_info, fetch_movie_videos, fetch_movie_translations


@gen.coroutine
def import_tv_emdb_by_series_id(tmdb_series_id_list, season_id_list, company_id=None, lang=None, country=None):
    for i in range(0, len(tmdb_series_id_list)):
        if tmdb_series_id_list[i] is None:
            break
        get_tv_detail_filter_season(tmdb_series_id_list[i],season_id_list[i], company_id)
        # get_tv_detail(tmdb_series_id_list[i])

    # for id in tmdb_series_id_list:
    #     get_tv_detail(id, company_id)


@gen.coroutine
def get_tv_detail_filter_season(tmdb_series_id, season_id, company_id=None, lang=None, country=None):
    """
    get tv series deatil
    """
    if lang is None or country is None:
        language = None
    else:
        language = lang.lower() + "-" + country.upper()
    language = 'zh'
    e_tmdb = Tmdb()
    img_base_url = e_tmdb.IMAGE_BASE_URL
    tv = e_tmdb.tv_series(tmdb_series_id)

    tv_series_detail = tv.info(language=language)
    # print(tv_series_detail)
    # external ids
    external_ids = tv.external_ids()
    emdb_movie_id = 0
    tv_seasons_info = tv_series_detail["seasons"]
    for season_info in tv_seasons_info:
        if season_info['season_number'] != season_id:
            continue

        tv_detail = parse_tv_detail(tv_series_detail, season_info, external_ids, img_base_url)
        # if company_id is not None and season_info['season_number'] == season_id:
        #     tv_detail["production_companies"].append(company_id)
        print(".............................................." + str(tmdb_series_id) + ">>" + str(
            season_id) + ".....................................")

        # 1.insert tv season detail to movie
        res = yield mv.insert_movies(tv_detail)
        # print(f"insert movie table res：{res}")
        if res["status"] == 1:
            _movie_info = yield mv.query_movie_by_tmdb_id(season_info["id"])
            emdb_movie_id = _movie_info["data"]["movie_info"].get("id")
        elif res["status"] == 0:
            emdb_movie_id = res["data"]["movie_id"]
        else:
            print("emdb_movie_id errror")
            app_log.error(f"insert movie error: {res}")
            return
        # 2. insert tv adddition_info
        tv_additional_info = parse_tv_adddition_info(tv_series_detail)
        tv_additional_info["external_ids"] = external_ids
        res = yield tv_series.insert_tv_additional_info(tv_additional_info)
        # print(f"insert_tv_additional_info res:{res}")

        # 4.insert seasons info
        # for season_info in tv_seasons_info:
        tv_season_obj = e_tmdb.tv_season(tv_series_detail["id"], season_info["season_number"])
        tv_season_external_ids = tv_season_obj.external_ids()
        season_info["external_ids"] = tv_season_external_ids

        # 5. insert episodes
        season_episode_info = tv_season_obj.info()
        episodes_info = season_episode_info["episodes"]
        episodes = parse_tv_episode_info(episodes_info, tmdb_series_id, season_info["id"], img_base_url)
        yield insert_tv_episodes_list(episodes)

        # 6.credits
        tv_season_credits = tv_season_obj.credits()
        # movie_credits = movie.credits()
        origin_credits_info_list = list()
        insert_credits_list = list()
        # cast info
        _cast_list = tv_season_credits["cast"]

        for cast in _cast_list:
            cast["type"] = CreditType.cast.value
            origin_credits_info_list.append(cast)

            cast_info = parse_credit_info(cast)
            insert_credits_list.append(cast_info)
        # crew info
        _crew_list = tv_season_credits["crew"]
        for crew in _crew_list:
            crew["type"] = CreditType.crew.value
            origin_credits_info_list.append(crew)
            crew_info = parse_credit_info(crew)

            insert_credits_list.append(crew_info)
        credits_ids = yield insert_movie_credits(insert_credits_list)
        tv_credits_relation = list()
        for credit in origin_credits_info_list:
            emdb_credit_id = credits_ids["data"].get(credit["id"], None)
            if emdb_credit_id is None:
                query_credit_info_res = yield query_movie_credit_by_tmdb_id(credit["id"])
                emdb_credit_id = query_credit_info_res["data"].get("id")
            temp_dict = dict(
                movie_id=emdb_movie_id,
                credit_id=emdb_credit_id,
                order=credit.get("order", None),
                character=credit.get("character", None),
                department=credit.get("department", None),
                job=credit.get("job", None),
                type=credit.get("type"),
                tmdb_credit_id=credit.get("credit_id")
            )
            tv_credits_relation.append(temp_dict)

        yield [insert_batch_movie_credits_relation(tv_credits_relation),
               save_alternative_titles(tv, emdb_movie_id),
               save_movie_images(tv_season_obj, tv, emdb_movie_id),
               fetch_movie_videos(tv_season_obj, emdb_movie_id),
               fetch_movie_translations(tv, emdb_movie_id)]
    # here the save_tv_seasons_info because of 'season_info["external_ids"] = tv_season_external_ids'

    yield save_tv_seasons_info(tv_seasons_info, tmdb_series_id, img_base_url)

    # 7.save production company
    production_companies = tv_series_detail.get("production_companies")
    _production_company_list = []
    for pc in production_companies:
        pc["tmdb_id"] = pc.pop("id")
        if pc["logo_path"]:
            pc["logo_path"] = img_base_url + pc["logo_path"]
        _production_company_list.append(pc)
    yield batch_insert_production_company(_production_company_list)

    # 8.save keywords
    key_words = tv.keywords()
    _key_words_list = key_words["results"]
    if emdb_movie_id != 0:
        key_words_list = [{"tmdb_id": d["id"], "name": d["name"], "movie_id": emdb_movie_id} for d in _key_words_list]

        yield insert_movie_key_words(key_words_list)

    # 9. save content_ratings
    yield save_content_ratings(tv, emdb_movie_id)

    return


@gen.coroutine
def get_tv_detail(tmdb_series_id, company_id=None, lang=None, country=None):
    """
    get tv series deatil
    """
    if lang is None or country is None:
        language = None
    else:
        language = lang.lower() + "-" + country.upper()
    language = 'zh'
    e_tmdb = Tmdb()
    img_base_url = e_tmdb.IMAGE_BASE_URL
    tv = e_tmdb.tv_series(tmdb_series_id)

    tv_series_detail = tv.info(language=language)
    # print(tv_series_detail)
    # external ids
    external_ids = tv.external_ids()
    # emdb_movie_id = 0
    tv_seasons_info = tv_series_detail["seasons"]
    for season_info in tv_seasons_info:

        tv_detail = parse_tv_detail(tv_series_detail, season_info, external_ids, img_base_url)
        if company_id is not None:
            tv_detail["production_companies"].append(company_id)

        # 1.insert tv season detail to movie
        res = yield mv.insert_movies(tv_detail)
        # print(f"insert movie table res：{res}")
        if res["status"] == 1:
            _movie_info = yield mv.query_movie_by_tmdb_id(season_info["id"])
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
        # print(f"insert_tv_additional_info res:{res}")

        # 4.insert seasons info
        # for season_info in tv_seasons_info:
        tv_season_obj = e_tmdb.tv_season(tv_series_detail["id"], season_info["season_number"])
        tv_season_external_ids = tv_season_obj.external_ids()
        season_info["external_ids"] = tv_season_external_ids

        # 5. insert episodes
        season_episode_info = tv_season_obj.info()
        episodes_info = season_episode_info["episodes"]
        episodes = parse_tv_episode_info(episodes_info, tmdb_series_id, season_info["id"], img_base_url)
        yield insert_tv_episodes_list(episodes)

        # 6.credits
        tv_season_credits = tv_season_obj.credits()
        # movie_credits = movie.credits()
        origin_credits_info_list = list()
        insert_credits_list = list()
        # cast info
        _cast_list = tv_season_credits["cast"]

        for cast in _cast_list:
            cast["type"] = CreditType.cast.value
            origin_credits_info_list.append(cast)

            cast_info = parse_credit_info(cast)
            insert_credits_list.append(cast_info)
        # crew info
        _crew_list = tv_season_credits["crew"]
        for crew in _crew_list:
            crew["type"] = CreditType.crew.value
            origin_credits_info_list.append(crew)
            crew_info = parse_credit_info(crew)

            insert_credits_list.append(crew_info)
        credits_ids = yield insert_movie_credits(insert_credits_list)
        tv_credits_relation = list()
        for credit in origin_credits_info_list:
            emdb_credit_id = credits_ids["data"].get(credit["id"], None)
            if emdb_credit_id is None:
                query_credit_info_res = yield query_movie_credit_by_tmdb_id(credit["id"])
                emdb_credit_id = query_credit_info_res["data"].get("id")
            temp_dict = dict(
                movie_id=emdb_movie_id,
                credit_id=emdb_credit_id,
                order=credit.get("order", None),
                character=credit.get("character", None),
                department=credit.get("department", None),
                job=credit.get("job", None),
                type=credit.get("type"),
                tmdb_credit_id=credit.get("credit_id")
            )
            tv_credits_relation.append(temp_dict)

        yield [insert_batch_movie_credits_relation(tv_credits_relation),
               save_alternative_titles(tv, emdb_movie_id),
               save_movie_images(tv_season_obj, tv, emdb_movie_id),
               fetch_movie_videos(tv_season_obj, emdb_movie_id),
               fetch_movie_translations(tv, emdb_movie_id)]
    # here the save_tv_seasons_info because of 'season_info["external_ids"] = tv_season_external_ids'
    yield save_tv_seasons_info(tv_seasons_info, tmdb_series_id, img_base_url)

    # 7.save production company
    production_companies = tv_series_detail.get("production_companies")
    _production_company_list = []
    for pc in production_companies:
        pc["tmdb_id"] = pc.pop("id")
        if pc["logo_path"]:
            pc["logo_path"] = img_base_url + pc["logo_path"]
        _production_company_list.append(pc)
    yield batch_insert_production_company(_production_company_list)

    # 8.save keywords
    key_words = tv.keywords()
    _key_words_list = key_words["results"]
    key_words_list = [{"tmdb_id": d["id"], "name": d["name"], "movie_id": emdb_movie_id} for d in _key_words_list]
    yield insert_movie_key_words(key_words_list)

    # 9. save content_ratings
    yield save_content_ratings(tv, emdb_movie_id)

    return


@gen.coroutine
def save_content_ratings(tv_obj, emdb_movie_id):
    content_ratings = tv_obj.content_ratings()
    content_rating_list = list()
    for cr in content_ratings["results"]:
        content_rate = dict()
        country = cr["iso_3166_1"]
        content_rate["movie_id"] = emdb_movie_id
        content_rate['iso_3166_1'] = country
        content_rate["descriptors"] = cr["descriptors"]
        content_rate["certification"] = cr["rating"]
        content_rate["type"] = enums.ReleaseTypes.Default.value
        content_rating_list.append(content_rate)
    yield insert_movie_release_dates(content_rating_list)


@gen.coroutine
def save_alternative_titles(tv_obj, emdb_movie_id):
    # movie_id: emdb movie id
    _alternative_titles = tv_obj.alternative_titles()
    alternative_titles = list()
    for at in _alternative_titles["results"]:
        at["movie_id"] = emdb_movie_id
        alternative_titles.append(at)
    yield insert_movie_alternative_titles(alternative_titles)


@gen.coroutine
def save_movie_images(tv_season_obj, tv_obj, emdb_movie_id):
    images = tv_season_obj.images()
    tv_series_images = tv_obj.images()
    backdrops = tv_series_images["backdrops"]
    logos = tv_series_images["logos"]
    posters = images["posters"]
    all_images = backdrops + logos + posters
    images_list = list()
    for img in all_images:
        img_dict = dict()
        img_dict["movie_id"] = emdb_movie_id
        if img["iso_639_1"] is None:
            img_dict["iso_639_1"] = "all"
        else:
            img_dict["iso_639_1"] = img["iso_639_1"]
        img_dict["url"] = Tmdb.IMAGE_BASE_URL + img.get("file_path")
        if img in logos:
            img_dict['type'] = ImagesType.Logo.value
        elif img in posters:
            img_dict['type'] = ImagesType.Poster.value
        elif img in backdrops:
            img_dict['type'] = ImagesType.Backdrop.value
        images_list.append(img_dict)
    yield insert_movie_images(images_list)


def parse_tv_episode_info(season_episode_info, tmdb_series_id, tmdb_season_id, img_base_url):
    episodes = list()
    for episode_info in season_episode_info:
        if episode_info["still_path"]:
            still_path = img_base_url + episode_info["still_path"]
        else:
            still_path = None
        single_epidose = {
            'tmdb_series_id': tmdb_series_id,
            'tmdb_season_id': tmdb_season_id,
            'tmdb_episode_id': episode_info["id"],
            'air_date': episode_info["air_date"] if episode_info["air_date"] else None,
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
def save_tv_seasons_info(tv_seasons_info, tmdb_series_id, img_base_url):
    tv_seasons_list = list()
    for season in tv_seasons_info:
        season["tmdb_series_id"] = tmdb_series_id
        season["tmdb_season_id"] = season["id"]
        # if season["poster_path"]:
        #     season["poster_path"] = img_base_url + season["poster_path"]
        del season["id"]
        del season["poster_path"]
        del season["vote_average"]
        tv_seasons_list.append(season)
    res = yield tv_seasons.insert_tv_seasons(tv_seasons_list)
    # print(f"insert_tv_seasons res:{res}")


def parse_tv_adddition_info(tv_series_detail):
    tv_detail = dict()
    tv_detail["tmdb_series_id"] = tv_series_detail["id"]
    tv_detail["created_by"] = tv_series_detail.get("created_by")
    tv_detail["episode_run_time"] = tv_series_detail.get("episode_run_time")
    tv_detail["in_production"] = tv_series_detail.get("in_production")
    if tv_series_detail.get("first_air_date"):
        tv_detail["first_air_date"] = tv_series_detail.get("first_air_date")
    if tv_series_detail.get("last_air_date"):
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
    if season_info["poster_path"]:
        tv_detail["poster_path"] = img_base_url + season_info["poster_path"]
    elif tv_series_detail["poster_path"]:
        tv_detail["poster_path"] = img_base_url + tv_series_detail["poster_path"]

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
    if len(tv_series_detail["episode_run_time"]) > 0:
        tv_detail["runtime"] = tv_series_detail["episode_run_time"][0]
    else:
        tv_detail["runtime"] = 0
    tv_detail["status"] = tv_series_detail.get("status")
    tv_detail["tagline"] = tv_series_detail.get("tagline")
    tv_detail["vote_count"] = tv_series_detail.get("vote_count")
    if season_info["air_date"]:
        tv_detail["release_date"] = season_info["air_date"]
    tv_detail["vote_average"] = season_info.get("vote_average")
    tv_detail["overview"] = season_info.get("overview")
    tv_detail["source_type"] = SourceType.Tv.value
    return tv_detail
