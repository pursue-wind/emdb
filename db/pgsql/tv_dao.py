from db.pgsql.enums.enums import SourceType
from db.pgsql.mysql_models import Imgs, Movies, MovieKeyWords, ProductionCompany, MoviesCredits, MovieAlternativeTitles, \
    TVSeriesAdditional
from db.pgsql.base import exc_handler, datetime_handler, Session


async def exist_ids_by_tmdb_series_ids(tmdb_series_ids: [int]) -> set:
    results = Session().query(TVSeriesAdditional).filter(TVSeriesAdditional.tmdb_series_id.in_(tmdb_series_ids))
    existing_ids = set()
    for tv in results.all():
        existing_ids.add(tv.tmdb_series_id)
    return existing_ids
