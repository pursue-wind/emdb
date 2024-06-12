import os.path
import string

from tornado import gen
from tornado.log import app_log

import db.pgsql.movies as mv
from db.pgsql.enums.enums import CreditType, ImagesType, VideoSiteUlr,SourceType
from db.pgsql.movie_alternative_titles import insert_movie_alternative_titles
from db.pgsql.movie_credits_relations import insert_batch_movie_credits_relation
from db.pgsql.movie_images import insert_movie_images
from db.pgsql.movie_key_words import insert_movie_key_words
from db.pgsql.movie_translations import insert_movie_translations
from db.pgsql.movie_videos import insert_movie_videos
from db.pgsql.production_company import batch_insert_production_company
from db.pgsql.movie_credits import insert_movie_credits, query_movie_credit_by_tmdb_id
from db.pgsql.movie_release_dates import insert_movie_release_dates
from . import Tmdb


@gen.coroutine
def fetch_movie_info(tmdb_mv_id, company_id=None, lang=None, country=None):


    e_tmdb = Tmdb()
    movie = e_tmdb.moive(tmdb_mv_id)
    # try:
    mv_detail = movie.info(language=lang)

    mv_detail["tmdb_id"] = tmdb_mv_id
    del mv_detail["id"]

    genres = mv_detail.get("genres")  # 电影类型，喜剧、动作等
    production_companies = mv_detail.get("production_companies")
    production_countries = mv_detail.get("production_countries")
    spoken_languages = mv_detail.get("spoken_languages")

    # parse list id
    genres_ids = [item["id"] for item in genres]
    production_company_ids = [item["id"] for item in production_companies]
    spoken_languages_iso6391 = [item["iso_639_1"] for item in spoken_languages]
    production_country_ids = [item["iso_3166_1"] for item in production_countries]
    release_date = mv_detail["release_date"]
    if release_date == "":
        mv_detail["release_date"] = None
    mv_detail["genres"] = genres_ids
    mv_detail["production_companies"] = production_company_ids
    if company_id is not None:
        mv_detail["production_companies"].append(company_id)
    mv_detail["production_countries"] = production_country_ids
    mv_detail["spoken_languages"] = spoken_languages_iso6391
    if mv_detail["backdrop_path"]:
        mv_detail["backdrop_path"] = e_tmdb.IMAGE_BASE_URL + mv_detail["backdrop_path"]
    if mv_detail["poster_path"]:
        mv_detail["poster_path"] = e_tmdb.IMAGE_BASE_URL + mv_detail["poster_path"]

    # external ids
    external_ids = movie.external_ids()
    mv_detail["external_ids"] = external_ids
    mv_detail["source_type"] = SourceType.Movie.value

    del mv_detail["origin_country"]
    res = yield mv.insert_movies(mv_detail)
    if res["status"] == 1:
        _movie_info = yield mv.query_movie_by_tmdb_id(tmdb_mv_id, SourceType.Movie.value)
        emdb_movie_id = _movie_info["data"]["movie_info"].get("id")
    elif res["status"] == 0:
        emdb_movie_id = res["data"]["movie_id"]
    else:
        app_log.error(f"insert movie error: {res}")
        return

    # save key words
    key_words = movie.keywords()
    _key_words_list = key_words["keywords"]
    key_words_list = [{"tmdb_id": d["id"], "name": d["name"], "movie_id": emdb_movie_id} for d in _key_words_list]
    yield insert_movie_key_words(key_words_list)#used

    # save production company
    # _production_company_list = []
    # for pc in production_companies:
    #     pc["tmdb_id"] = pc.pop("id")
    #     if pc["logo_path"]:
    #         pc["logo_path"] = e_tmdb.IMAGE_BASE_URL + pc["logo_path"]
    #     _production_company_list.append(pc)
    # yield batch_insert_production_company(_production_company_list)#used

    ## save cast/crew
    movie_credits = movie.credits()
    origin_credits_info_list = list()
    insert_credits_list = list()
    # cast info
    _cast_list = movie_credits["cast"]

    for cast in _cast_list:
        cast["type"] = CreditType.cast.value
        origin_credits_info_list.append(cast)

        cast_info = parse_credit_info(cast)
        insert_credits_list.append(cast_info)
    # crew info
    _crew_list = movie_credits["crew"]
    for crew in _crew_list:
        crew["type"] = CreditType.crew.value
        origin_credits_info_list.append(crew)
        crew_info = parse_credit_info(crew)

        insert_credits_list.append(crew_info)
    credits_ids = yield insert_movie_credits(insert_credits_list)
    movie_credits_relation = list()
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
        movie_credits_relation.append(temp_dict)

    # save relationships of movie and credits
    # yield insert_batch_movie_credits_relation(movie_credits_relation)
    # # save alternative titles
    # yield fetch_alternative_titles(movie, emdb_movie_id)
    # # save images
    # yield fetch_movie_images(movie, emdb_movie_id)
    # # save videos
    # yield fetch_movie_videos(movie, emdb_movie_id)
    # # save release dates
    # yield fetch_movie_release_dates(movie, emdb_movie_id)
    # # save movie translations
    # yield fetch_movie_translations(movie, emdb_movie_id)

    # all used
    yield [insert_batch_movie_credits_relation(movie_credits_relation),
           fetch_alternative_titles(movie, emdb_movie_id),
           fetch_movie_images(movie, emdb_movie_id),
           fetch_movie_videos(movie, emdb_movie_id),
           fetch_movie_release_dates(movie, emdb_movie_id),
           fetch_movie_translations(movie, emdb_movie_id)]
    # yield fetch_movie_images(movie, emdb_movie_id)//now
    return True, emdb_movie_id
    # except Exception as e:
    #     app_log.error(e)
    #     return False, None


def parse_credit_info(credit):
    cast_info = {}
    if credit["profile_path"]:
        cast_info["profile_path"] = Tmdb.IMAGE_BASE_URL + credit["profile_path"]
    else:
        cast_info["profile_path"] = None
    cast_info["tmdb_id"] = credit["id"]
    cast_info["name"] = credit["name"]
    cast_info["original_name"] = credit["original_name"]
    cast_info["popularity"] = credit["popularity"]
    cast_info["gender"] = credit["gender"]
    cast_info["known_for_department"] = credit["known_for_department"]
    cast_info["adult"] = credit["adult"]
    cast_info["cast_id"] = credit.get("cast_id")
    return cast_info


@gen.coroutine
def fetch_movie_translations(movie_obj, emdb_movie_id):
    _translations = movie_obj.translations()
    translations_list = list()
    for tr in _translations["translations"]:
        tr["movie_id"] = emdb_movie_id
        tr.update(tr.pop("data"))
        translations_list.append(tr)
    yield insert_movie_translations(translations_list)


@gen.coroutine
def fetch_movie_release_dates(movie_obj, emdb_movie_id):
    _release_dates = movie_obj.release_dates()
    release_dates_list = list()
    for rd in _release_dates["results"]:
        country = rd["iso_3166_1"]
        for rdl in rd["release_dates"]:
            rdl["movie_id"] = emdb_movie_id
            rdl['iso_3166_1'] = country
            if len(rdl["iso_639_1"]) > 5:
                rdl["iso_639_1"] = None
            if 'note' not in rdl.keys():
                rdl["note"] = ""
            release_dates_list.append(rdl)
    yield insert_movie_release_dates(release_dates_list)


@gen.coroutine
def fetch_movie_videos(movie_obj, emdb_movie_id):
    _videos = movie_obj.videos()
    videos_list = list()
    for v in _videos["results"]:
        v["movie_id"] = emdb_movie_id
        v["tmdb_id"] = v.pop("id")
        base_url = None
        if v["site"] == VideoSiteUlr.YouTube.name:
            base_url = VideoSiteUlr.YouTube.value
        elif v["site"] == VideoSiteUlr.Vimeo.name:
            base_url = VideoSiteUlr.Vimeo.value
        if base_url:
            v["url"] = base_url + v["key"]
        videos_list.append(v)
    yield insert_movie_videos(videos_list)


@gen.coroutine
def fetch_alternative_titles(movie_obj, emdb_movie_id):
    # movie_id: emdb movie id
    _alternative_titles = movie_obj.alternative_titles()
    alternative_titles = list()
    for at in _alternative_titles["titles"]:
        at["movie_id"] = emdb_movie_id
        alternative_titles.append(at)
    yield insert_movie_alternative_titles(alternative_titles)


@gen.coroutine
def fetch_movie_images(movie_obj, emdb_movie_id):
    images = movie_obj.images()
    backdrops = images["backdrops"]
    logos = images["logos"]
    posters = images["posters"]
    all_images = backdrops + logos + posters
    images_list = list()
    for img in all_images:
        img_dict = dict()
        img_dict["movie_id"] = emdb_movie_id
        img_dict["height"] = img["height"]
        img_dict["width"] = img["width"]
        img_dict["ext"] = os.path.splitext(img.get("file_path"))[-1][1:].lower()
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


