CREATE TABLE production_company (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) INDEX,
    tmdb_id INTEGER NOT NULL UNIQUE,
    headquarters VARCHAR(255),
    homepage VARCHAR(255),
    origin_country VARCHAR(20),
    parent_company VARCHAR(255),
    logo_path VARCHAR(120)
);

CREATE TABLE movies (
    id SERIAL PRIMARY KEY,
    tmdb_id INTEGER NOT NULL,
    imdb_id VARCHAR(10) INDEX,
    title VARCHAR(255) NOT NULL INDEX,
    backdrop_path VARCHAR(200),
    belongs_to_collection JSONB,
    budget INTEGER,
    genres INTEGER[],
    homepage VARCHAR(200),
    original_language VARCHAR(20) NOT NULL,
    original_title VARCHAR(128) NOT NULL,
    overview TEXT,
    adult BOOLEAN NOT NULL,
    popularity NUMERIC(10, 3),
    poster_path VARCHAR(128),
    production_companies INTEGER[] COMMENT '制片公司',
    production_countries VARCHAR(5)[],
    release_date TIMESTAMP,
    revenue INTEGER,
    runtime INTEGER,
    spoken_languages VARCHAR(5)[],
    status VARCHAR(32) NOT NULL,
    tagline TEXT,
    video BOOLEAN,
    vote_average NUMERIC(5, 3),
    vote_count INTEGER,
    source_type INTEGER,
    external_ids JSONB
);
drop index if exists ix_uni_movies_tmdb_id_source_type;
CREATE UNIQUE INDEX ix_uni_movies_tmdb_id_source_type ON movies (tmdb_id,source_type);


CREATE TABLE movie_key_words (
    id SERIAL PRIMARY KEY,
    tmdb_id INTEGER NOT NULL,
    movie_id INTEGER NOT NULL,
    name VARCHAR(255) NOT NULL,
    source_type INTEGER
);
drop index if EXISTS ix_uni_movie_key_words_tmdb_id_source_type;
CREATE UNIQUE INDEX ix_uni_movie_key_words_tmdb_id_source_type ON movie_key_words (tmdb_id,source_type);


CREATE TABLE movie_alternative_titles (
    id SERIAL PRIMARY KEY,
    movie_id INTEGER NOT NULL,
    iso_3166_1 VARCHAR(30),
    title VARCHAR(200) NOT NULL,
    type VARCHAR(200),
    UNIQUE(movie_id, iso_3166_1, title)
);

CREATE TABLE movie_translations (
    id SERIAL PRIMARY KEY,
    movie_id INTEGER NOT NULL,
    iso_3166_1 VARCHAR(30) INDEX,
    iso_639_1 VARCHAR(30) INDEX,
    name VARCHAR(255),
    english_name VARCHAR(255),
    homepage VARCHAR(500),
    overview TEXT,
    runtime INTEGER,
    tagline VARCHAR(300),
    title VARCHAR(300),
    UNIQUE(iso_3166_1, iso_639_1)
);

CREATE TABLE movie_credits_relation (
    id SERIAL PRIMARY KEY,
    movie_id INTEGER NOT NULL,
    credit_id INTEGER NOT NULL,
    tmdb_credit_id VARCHAR(255) NOT NULL UNIQUE,
    "order" INTEGER,
    character VARCHAR(255),
    department VARCHAR(255),
    job VARCHAR(255),
    type INTEGER INDEX COMMENT '1:cast，2：crew'
);

CREATE TABLE movie_credits (
    id SERIAL PRIMARY KEY,
    tmdb_id INTEGER NOT NULL UNIQUE,
    name VARCHAR(255) INDEX,
    original_name VARCHAR(255),
    popularity NUMERIC(10, 3),
    gender INTEGER,
    known_for_department VARCHAR(255),
    adult BOOLEAN,
    profile_path VARCHAR(255),
    cast_id INTEGER
);

CREATE TABLE movie_release_date (
    id SERIAL PRIMARY KEY,
    movie_id INTEGER NOT NULL,
    iso_3166_1 VARCHAR(30) COMMENT 'country',
    iso_639_1 VARCHAR(30) COMMENT 'language',
    certification VARCHAR(255),
    descriptors VARCHAR(20)[],
    note VARCHAR(255),
    release_date TIMESTAMP,
    type INTEGER NOT NULL,
    UNIQUE(iso_3166_1, release_date)
);

CREATE TABLE imgs (
    id SERIAL PRIMARY KEY,
    movie_id INTEGER NOT NULL,
    iso_639_1 VARCHAR(30),
    url VARCHAR(128),
    type INTEGER NOT NULL,
    UNIQUE(movie_id, iso_639_1, url)
);

CREATE TABLE videos (
    id SERIAL PRIMARY KEY,
    movie_id INTEGER NOT NULL,
    name VARCHAR(128) NOT NULL,
    type VARCHAR(20) COMMENT '视频类型',
    iso_3166_1 VARCHAR(30),
    iso_639_1 VARCHAR(30),
    url VARCHAR(128),
    site VARCHAR(32) COMMENT 'Vimeo/Youtube',
    "key" VARCHAR(128) NOT NULL COMMENT '第三方视频平台的key',
    size INTEGER,
    official BOOLEAN,
    published_at TIMESTAMP,
    tmdb_id VARCHAR(64) UNIQUE
);

CREATE TABLE movie_tasks (
    id SERIAL PRIMARY KEY,
    tmdb_movie_id INTEGER NOT NULL,
    movie_detail BOOLEAN NOT NULL DEFAULT FALSE,
    credits BOOLEAN NOT NULL DEFAULT FALSE,
    images BOOLEAN NOT NULL DEFAULT FALSE,
    videos BOOLEAN NOT NULL DEFAULT FALSE,
    keywords BOOLEAN NOT NULL DEFAULT FALSE,
    release_date BOOLEAN NOT NULL DEFAULT FALSE,
    translations BOOLEAN NOT NULL DEFAULT FALSE,
    production_companies BOOLEAN NOT NULL DEFAULT FALSE
);


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
    tmdb_episode_id INT NOT NULL,
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