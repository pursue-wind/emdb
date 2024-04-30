-- 新增字段
ALTER TABLE movies
ADD COLUMN source_type INT DEFAULT 1 NOT NULL,
ADD COLUMN tmdb_series_id INT DEFAULT NULL;

-- 修改字段默认值
ALTER TABLE movies
ALTER COLUMN budget SET DEFAULT 0,
ALTER COLUMN revenue SET DEFAULT 0,
ALTER COLUMN runtime SET DEFAULT 0;

-- 新增字段
ALTER TABLE movies
ALTER COLUMN video set DEFAULT false;

---- movie_translations table:
-- 删除旧索引
ALTER TABLE movie_translations DROP CONSTRAINT movie_translations_iso_3166_1_iso_639_1_key;
-- 创建新唯一索引
CREATE UNIQUE INDEX unique_movie_translations ON movie_translations (movie_id, iso_3166_1, iso_639_1);





-- 新增表
-- TVSeriesAdditional
CREATE TABLE tv_series_additional (
    id SERIAL PRIMARY KEY,
    tmdb_series_id INT NOT NULL UNIQUE,
    created_by JSONB,
    episode_run_time INT[],
    first_air_date TIMESTAMP,
    in_production BOOLEAN,
    last_air_date TIMESTAMP,
    last_episode_to_air JSONB,
    networks JSONB,
    overview TEXT,
    number_of_episodes INT,
    number_of_seasons INT,
    type VARCHAR(30),
    external_ids JSONB
);

-- TVSeasons
CREATE TABLE tv_seasons (
    id SERIAL PRIMARY KEY,
    tmdb_season_id INT NOT NULL UNIQUE,
    tmdb_series_id INT NOT NULL,
    air_date TIMESTAMP,
    episode_count INT,
    name VARCHAR,
    overview TEXT,
    season_number INT,
    external_ids JSONB
);

-- TVEpisodes
CREATE TABLE tv_episodes (
    id SERIAL PRIMARY KEY,
    tmdb_series_id INT NOT NULL,
    tmdb_season_id INT NOT NULL,
    tmdb_episode_id INT NOT NULL UNIQUE,
    air_date TIMESTAMP,
    episode_number INT,
    episode_type VARCHAR(20),
    name VARCHAR(200),
    overview TEXT,
    production_code VARCHAR,
    runtime INT,
    season_number INT,
    still_path VARCHAR,
    vote_average NUMERIC(10,5),
    vote_count INT
);



