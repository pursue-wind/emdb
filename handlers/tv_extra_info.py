import json

from tornado import gen

from db.pgsql.movie_alternative_titles import query_alternative_title
from db.pgsql.movie_credits_relations import query_movie_credits_by_movie_id
from db.pgsql.movie_images import query_movie_images
from db.pgsql.movie_release_dates import query_movie_release_dates
from db.pgsql.movie_translations import query_movie_translations
from db.pgsql.movie_videos import query_movie_videos
from handlers.base_handler import BaseHandler


class TVAlternativeTitles(BaseHandler):
    """
    search all movies of a company by company id in tmdb
    :returns movies list
    """
    @gen.coroutine
    def get(self, *_args, **_kwargs):
        args = self.parse_form_arguments('tv_id')
        tv_id = args.tv_id
        yield self.check_auth()
        res = yield query_alternative_title(movie_id=tv_id, lang=None)

        self.success(data=dict(alternative_titles=res["data"]))


class TVCredits(BaseHandler):
    """
    Get cast and crew
    :returns credits
    """
    @gen.coroutine
    def get(self, *_args, **_kwargs):
        args = self.parse_form_arguments('tv_id')
        tv_id = args.tv_id
        yield self.check_auth()
        res = yield query_movie_credits_by_movie_id(tv_id, lang=None)

        self.success(data=dict(credits=res["data"]))


class TVReleaseDates(BaseHandler):
    """
    Get movie release datas
    :returns release dates list
    """
    @gen.coroutine
    def get(self, *_args, **_kwargs):
        args = self.parse_form_arguments('tv_id')
        tv_id = args.tv_id
        yield self.check_auth()
        result = yield query_movie_release_dates(tv_id)
        self.success(data=result["data"])



class TVImages(BaseHandler):
    """
    Get movie release datas
    :returns release dates list
    """
    @gen.coroutine
    def get(self, *_args, **_kwargs):
        args = self.parse_form_arguments('tv_id')
        tv_id = args.tv_id
        yield self.check_auth()
        result = yield query_movie_images(tv_id)
        self.success(data=result["data"])


class TVVideos(BaseHandler):
    """
    Get movie release datas
    :returns release dates list
    """
    @gen.coroutine
    def get(self, *_args, **_kwargs):
        args = self.parse_form_arguments('tv_id')
        tv_id = args.tv_id
        yield self.check_auth()
        result = yield query_movie_videos(tv_id)
        self.success(data=result["data"])


class TVTranslations(BaseHandler):
    """
    movie translations
    """
    @gen.coroutine
    def get(self,*_args, **_kwargs):
        args = self.parse_form_arguments('tv_id')
        tv_id = args.tv_id
        yield self.check_auth()
        result = yield query_movie_translations(tv_id)
        self.success(data=result['data'])


class GetTVRealeseCertifications(BaseHandler):
    """
    get all movie release certification by country
    """
    @gen.coroutine
    def get(self, *_args, **_kwargs):
        yield self.check_auth()
        args = self.parse_form_arguments('country')
        country = args.country
        with open("docs/tmdb/movie_certifications.json", "r") as file:
            data = json.load(file)
        res = data['certifications'].get(country)
        certifications = list()
        if res:
            for ct in res:
                certifications.append(ct.get("certification"))
        self.success(data=certifications)


















