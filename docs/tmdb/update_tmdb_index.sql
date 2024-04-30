drop index if exists ix_movies_tmdb_id;
CREATE UNIQUE INDEX ix_uni_movies_tmdb_id_source_type ON movies (tmdb_id,source_type);


ALTER TABLE movie_key_words ADD COLUMN source_type int not null default 1;
update movie_key_words mk set source_type=(select source_type from movies where id=mk.movie_id);


drop index if EXISTS ix_movie_key_words_tmdb_id;
CREATE UNIQUE INDEX ix_uni_movie_key_words_tmdb_id_source_type ON movie_key_words (tmdb_id,source_type);