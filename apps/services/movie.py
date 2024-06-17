import tmdbsimple as tmdb
import tornado.ioloop
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from apps.domain.models import *
from apps.services.people import PeopleService

# 配置 TMDB API 密钥
tmdb.API_KEY = 'fb5642b7e0b6d36ad5ebcdf78a52f14c'


class MovieService(PeopleService):
    def __init__(self, session: AsyncSession):
        super().__init__(session)

    async def fetch_and_store_movie(self, movie_id: int):
        movie = tmdb.Movies(movie_id)
        lang = self._language()
        details = await self._fetch(lambda: movie.info(language=lang))
        movie_credits = await self._fetch(lambda: movie.credits(language=lang))
        await self._store_movie(details, movie_credits)

    async def get_movie(self, movie_id: int):
        result = await self.session.execute(
            select(TMDBMovie).options(
                joinedload(TMDBMovie.genres),
                joinedload(TMDBMovie.production_companies),
                joinedload(TMDBMovie.production_countries),
                # joinedload(TMDBMovie.movie_cast).joinedload(TMDBMovieCast.people),
                # joinedload(TMDBMovie.movie_crew),
            ).where(TMDBMovie.id == movie_id)
        )
        r = result.unique().scalar_one_or_none()
        return self.to_primitive(r)

    async def _fetch_movie_details(self, movie):
        return await tornado.ioloop.IOLoop.current().run_in_executor(None,
                                                                     lambda: movie.info(language=self._language()))

    async def _fetch_movie_credits(self, movie):
        return await tornado.ioloop.IOLoop.current().run_in_executor(None,
                                                                     lambda: movie.credits(language=self._language()))

    async def _store_movie(self, details, credits):
        async with self.session.begin():
            movie = TMDBMovie(
                id=details['id'],
                adult=details['adult'],
                backdrop_path=details.get('backdrop_path'),
                budget=details['budget'],
                imdb_id=details.get('imdb_id'),
                original_language=details['original_language'],
                original_title=details.get('original_title'),
                popularity=details['popularity'],
                poster_path=details.get('poster_path'),
                release_date=details.get('release_date'),
                revenue=details.get('revenue'),
                runtime=details.get('runtime'),
                status=details.get('status'),
                video=details['video'],
                vote_average=details['vote_average'],
                vote_count=details['vote_count']
            )

            # 关联 collection
            if details.get('belongs_to_collection'):
                collection_data = details['belongs_to_collection']
                collection = await self._get_or_create(
                    TMDBBelongsToCollection, collection_data['id'], {
                        'name': collection_data['name'],
                        'poster_path': collection_data.get('poster_path'),
                        'backdrop_path': collection_data.get('backdrop_path')
                    })
                movie.belongs_to_collection = collection

            # 关联 genres
            movie.genres = await self._get_or_create_list(
                TMDBGenre,
                details.get('genres', []),
                lambda x: {'id': x['id'], 'name': x['name']},
                merge=True
            )
            # 关联 production_companies
            movie.production_companies = await self._get_or_create_list(
                TMDBProductionCompany,
                details.get('production_companies', []),
                lambda x: {
                    'id': x.get('id'),
                    'logo_path': x.get('logo_path'),
                    'name': x['name'],
                    'origin_country': x['origin_country']
                }
            )
            # 关联 production_countries
            movie.production_countries = await self._get_or_create_list(
                TMDBProductionCountry,
                details.get('production_countries', []),
                lambda x: {
                    'iso_3166_1': x['iso_3166_1'],
                    'name': x['name']
                }, key='iso_3166_1'
            )

            # 关联 spoken_languages
            movie.spoken_languages = await self._get_or_create_list(
                TMDBSpokenLanguage, details.get('spoken_languages', []),
                lambda x: {
                    'iso_639_1': x['iso_639_1'],
                    'english_name': x.get('english_name'),
                    'name': x['name']
                }, key='iso_639_1'
            )

            translation = TMDBMovieTranslation(
                movie_id=details['id'],
                language=self._language(),
                title=details['title'],
                overview=details['overview'],
                tagline=details['tagline'],
                homepage=details['homepage'],
            )

            await self.session.merge(movie)
            await self.session.merge(translation)
            await self.session.flush()

            # 处理演员信息
            await self._process_casts(movie, credits['cast'])
            # 处理剧组信息
            await self._process_crews(movie, credits['crew'])

    async def _process_casts(self, movie, casts):
        for cast_data in casts:
            people = await self.update_or_create_people(cast_data['id'])
            cast = TMDBMovieCast(
                movie_id=movie.id,
                people_id=people.id,
                character=cast_data.get('character'),
                order=cast_data.get('order'),
                credit_id=cast_data.get('credit_id'),
                cast_id=cast_data.get('cast_id')
            )
            self.session.add(cast)

    async def _process_crews(self, movie, crews):
        for crew_data in crews:
            people = await self.update_or_create_people(crew_data['id'])
            crew = TMDBMovieCrew(
                movie_id=movie.id,
                people_id=people.id,
                department=crew_data.get('department'),
                job=crew_data.get('job'),
                credit_id=crew_data.get('credit_id')
            )
            self.session.add(crew)
