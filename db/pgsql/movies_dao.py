import json
from operator import or_

from sqlalchemy import cast, Integer, and_, func
from sqlalchemy.dialects.postgresql import insert, ARRAY
from tornado import gen

from db.pgsql.enums.enums import SourceType
from db.pgsql.mysql_models import Imgs, Movies, MovieKeyWords, ProductionCompany, MoviesCredits, MovieAlternativeTitles
from db.pgsql.base import exc_handler, datetime_handler, Session


async def exist_ids_by_tmdb_ids(tmdb_movie_ids: [int], source_type=SourceType.Movie.value) -> set:
    results = Session().query(Movies).filter(Movies.tmdb_id.in_(tmdb_movie_ids),
                                             Movies.source_type == source_type)
    existing_ids = set()
    for movie in results.all():
        existing_ids.add(movie.tmdb_id)
    return existing_ids
