from handlers.base_handler import BaseHandler


class AddMovie(BaseHandler):
    """
    add movie by tmdb movie id
    """
    @gen.coroutine
    def post(self, *_args, **_kwargs):
        args = self.parse_form_arguments('tmdb_movie_id')
        tmdb_movie_id = args.tmdb_movie_id
        yield self.check_auth()
        res = yield query_movie_by_tmdb_id(tmdb_movie_id)
        if res['status'] == 0:
            if res["data"]["movie_info"]:
                movie_id = res["data"]["movie_info"]["id"]
                self.success(msg="Already Exist!", data=dict(movie_id=movie_id))
        ok, movie_id = yield fetch_movie_info(tmdb_movie_id)
        if ok:
            self.success(data=dict(movie_id=movie_id))
        else:
            self.fail(405)