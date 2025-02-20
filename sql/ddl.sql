create table tmdb_created_by
(
	id integer not null
		primary key,
	credit_id varchar not null,
	gender integer not null,
	name varchar not null,
	original_name varchar not null,
	profile_path varchar,
	created_at timestamp default CURRENT_TIMESTAMP not null,
	updated_at timestamp default CURRENT_TIMESTAMP not null
);

comment on column tmdb_created_by.credit_id is '信用 ID';

comment on column tmdb_created_by.gender is '性别';

comment on column tmdb_created_by.name is '姓名';

comment on column tmdb_created_by.original_name is '原名';

comment on column tmdb_created_by.profile_path is '头像路径';

create table tmdb_genres
(
	id integer not null
		primary key
);

create table tmdb_production_companies
(
	id integer not null
		primary key,
	logo_path varchar,
	name varchar,
	origin_country varchar,
	created_at timestamp default CURRENT_TIMESTAMP not null,
	updated_at timestamp default CURRENT_TIMESTAMP not null
);

comment on column tmdb_production_companies.logo_path is '标志路径';

comment on column tmdb_production_companies.name is '名称';

comment on column tmdb_production_companies.origin_country is '原产国';

create table tmdb_production_countries
(
	iso_3166_1 varchar not null
		primary key,
	name varchar,
	created_at timestamp default CURRENT_TIMESTAMP not null,
	updated_at timestamp default CURRENT_TIMESTAMP not null
);

comment on column tmdb_production_countries.iso_3166_1 is 'ISO 3166-1';

comment on column tmdb_production_countries.name is '名称';

create table tmdb_spoken_languages
(
	iso_639_1 varchar not null
		primary key,
	english_name varchar,
	name varchar,
	created_at timestamp default CURRENT_TIMESTAMP not null,
	updated_at timestamp default CURRENT_TIMESTAMP not null
);

comment on column tmdb_spoken_languages.iso_639_1 is 'ISO 639-1';

comment on column tmdb_spoken_languages.english_name is '英文名称';

comment on column tmdb_spoken_languages.name is '本地名称';

create table tmdb_movies
(
	id integer not null
		primary key,
	budget integer not null,
	imdb_id varchar,
	original_title varchar,
	release_date varchar,
	revenue integer not null,
	runtime integer,
	homepage varchar,
	overview varchar,
	tagline varchar,
	title varchar,
	video boolean not null,
	belongs_to_collection jsonb,
	adult boolean not null,
	backdrop_path varchar,
	origin_country character varying[],
	status varchar,
	original_language varchar not null,
	popularity double precision not null,
	poster_path varchar,
	vote_average double precision not null,
	vote_count integer not null,
	external_ids jsonb,
	keywords jsonb,
	created_at timestamp default CURRENT_TIMESTAMP not null,
	updated_at timestamp default CURRENT_TIMESTAMP not null
);

comment on column tmdb_movies.budget is '预算';

comment on column tmdb_movies.imdb_id is 'IMDb ID';

comment on column tmdb_movies.original_title is '原标题';

comment on column tmdb_movies.release_date is '上映日期';

comment on column tmdb_movies.revenue is '收入';

comment on column tmdb_movies.runtime is '时长（分钟）';

comment on column tmdb_movies.homepage is '主页URL';

comment on column tmdb_movies.overview is '概述';

comment on column tmdb_movies.tagline is '标语';

comment on column tmdb_movies.title is '标题';

comment on column tmdb_movies.video is '是否为视频';

comment on column tmdb_movies.belongs_to_collection is 'belongs_to_collection，作为JSON数组存储';

comment on column tmdb_movies.adult is '是否为成人';

comment on column tmdb_movies.backdrop_path is '背景图片路径';

comment on column tmdb_movies.origin_country is '原产国';

comment on column tmdb_movies.status is '状态';

comment on column tmdb_movies.original_language is '原语言';

comment on column tmdb_movies.popularity is '流行度';

comment on column tmdb_movies.poster_path is '海报路径';

comment on column tmdb_movies.vote_average is '平均评分';

comment on column tmdb_movies.vote_count is '评分人数';

comment on column tmdb_movies.external_ids is 'external_ids，作为JSON数组存储';

comment on column tmdb_movies.keywords is 'keywords，作为JSON数组存储';

create table tmdb_people
(
	id integer not null
		primary key,
	adult boolean not null,
	biography text,
	birthday varchar,
	deathday varchar,
	gender integer not null,
	homepage varchar,
	imdb_id varchar,
	known_for_department varchar,
	name varchar not null,
	place_of_birth varchar,
	popularity double precision not null,
	profile_path varchar,
	also_known_as character varying[],
	created_at timestamp default CURRENT_TIMESTAMP not null,
	updated_at timestamp default CURRENT_TIMESTAMP not null
);

comment on column tmdb_people.adult is '是否为成人';

comment on column tmdb_people.biography is '传记';

comment on column tmdb_people.birthday is '生日';

comment on column tmdb_people.deathday is '死亡日期';

comment on column tmdb_people.gender is '性别';

comment on column tmdb_people.homepage is '首页';

comment on column tmdb_people.imdb_id is 'IMDb ID';

comment on column tmdb_people.known_for_department is '知名部门';

comment on column tmdb_people.name is '名字';

comment on column tmdb_people.place_of_birth is '出生地';

comment on column tmdb_people.popularity is '流行度';

comment on column tmdb_people.profile_path is '头像路径';

comment on column tmdb_people.also_known_as is '别名';

create table tmdb_movie_genres
(
	movie_id integer not null
		references tmdb_movies,
	genre_id integer not null
		references tmdb_genres,
	primary key (movie_id, genre_id)
);

create table tmdb_movie_production_companies
(
	movie_id integer not null
		references tmdb_movies,
	production_company_id integer not null
		references tmdb_production_companies,
	primary key (movie_id, production_company_id)
);

create table tmdb_movie_production_countries
(
	movie_id integer not null
		references tmdb_movies,
	production_country_id varchar not null
		references tmdb_production_countries,
	primary key (movie_id, production_country_id)
);

create table tmdb_movie_spoken_languages
(
	movie_id integer not null
		references tmdb_movies,
	spoken_language_id varchar not null
		references tmdb_spoken_languages,
	primary key (movie_id, spoken_language_id)
);

create table tmdb_genres_translations
(
	genre_id integer not null
		references tmdb_genres,
	language varchar not null,
	name varchar not null,
	primary key (genre_id, language)
);

comment on column tmdb_genres_translations.language is '语言代码';

comment on column tmdb_genres_translations.name is '名称';

create table tmdb_movie_translations
(
	movie_id integer not null
		references tmdb_movies,
	iso_3166_1 varchar(2) not null,
	iso_639_1 varchar(2) not null,
	name varchar,
	english_name varchar,
	homepage varchar,
	overview varchar,
	runtime integer,
	tagline varchar,
	title varchar,
	created_at timestamp default CURRENT_TIMESTAMP not null,
	updated_at timestamp default CURRENT_TIMESTAMP not null,
	primary key (movie_id, iso_3166_1, iso_639_1)
);

comment on column tmdb_movie_translations.movie_id is '关联电影的ID';

comment on column tmdb_movie_translations.iso_3166_1 is '国家的ISO 3166-1代码';

comment on column tmdb_movie_translations.iso_639_1 is '语言的ISO 639-1代码';

comment on column tmdb_movie_translations.name is '语言的本地名称';

comment on column tmdb_movie_translations.english_name is '语言的英语名称';

comment on column tmdb_movie_translations.homepage is '翻译版本的主页URL';

comment on column tmdb_movie_translations.overview is '翻译版本的概述';

comment on column tmdb_movie_translations.runtime is '翻译版本的运行时长，以分钟为单位';

comment on column tmdb_movie_translations.tagline is '翻译版本的标语';

comment on column tmdb_movie_translations.title is '翻译版本的标题';

create table tmdb_movie_release_dates
(
	movie_id integer not null
		references tmdb_movies,
	iso_3166_1 varchar(2) not null,
	certification varchar,
	descriptors jsonb,
	iso_639_1 varchar(2) not null,
	note varchar,
	release_date timestamp with time zone not null,
	type integer not null,
	created_at timestamp default CURRENT_TIMESTAMP not null,
	updated_at timestamp default CURRENT_TIMESTAMP not null,
	primary key (movie_id, iso_3166_1, iso_639_1)
);

comment on column tmdb_movie_release_dates.movie_id is '关联电影的ID';

comment on column tmdb_movie_release_dates.iso_3166_1 is '国家的ISO 3166-1代码';

comment on column tmdb_movie_release_dates.certification is '电影在该国的分级认证';

comment on column tmdb_movie_release_dates.descriptors is '描述符，作为JSON数组存储';

comment on column tmdb_movie_release_dates.iso_639_1 is '语言的ISO 639-1代码';

comment on column tmdb_movie_release_dates.note is '有关发行的备注';

comment on column tmdb_movie_release_dates.release_date is '电影的发行日期和时间';

comment on column tmdb_movie_release_dates.type is '发行类型的标识符';

create table tmdb_movie_alternative_titles
(
	movie_id integer not null
		references tmdb_movies,
	iso_3166_1 varchar(2) not null,
	title varchar not null,
	type varchar,
	created_at timestamp default CURRENT_TIMESTAMP not null,
	updated_at timestamp default CURRENT_TIMESTAMP not null,
	primary key (movie_id, iso_3166_1)
);

comment on column tmdb_movie_alternative_titles.movie_id is '关联电影的ID';

comment on column tmdb_movie_alternative_titles.iso_3166_1 is '国家的ISO 3166-1代码';

comment on column tmdb_movie_alternative_titles.title is '电影的替代标题';

comment on column tmdb_movie_alternative_titles.type is '替代标题的类型';

create table tmdb_movie_images
(
	movie_id integer not null
		references tmdb_movies,
	iso_639_1 varchar(2),
	file_path varchar(255) not null
		primary key,
	image_type tmdbimagetypeenum not null,
	aspect_ratio double precision,
	height integer,
	width integer,
	vote_average double precision,
	vote_count integer,
	created_at timestamp default CURRENT_TIMESTAMP not null,
	updated_at timestamp default CURRENT_TIMESTAMP not null
);

create table tmdb_movie_videos
(
	movie_id integer not null
		references tmdb_movies,
	id varchar not null,
	iso_639_1 varchar(2) not null,
	iso_3166_1 varchar(2) not null,
	name varchar(255) not null,
	key varchar(255) not null,
	site varchar not null,
	size integer not null,
	type varchar not null,
	official boolean not null,
	published_at timestamp with time zone not null,
	tmdb_video_id varchar(255) not null,
	created_at timestamp default CURRENT_TIMESTAMP not null,
	updated_at timestamp default CURRENT_TIMESTAMP not null,
	primary key (movie_id, id)
);

create table tmdb_movie_crews
(
	movie_id integer not null
		references tmdb_movies,
	people_id integer not null
		references tmdb_people,
	department varchar not null,
	job varchar not null,
	credit_id varchar,
	created_at timestamp default CURRENT_TIMESTAMP not null,
	updated_at timestamp default CURRENT_TIMESTAMP not null,
	primary key (movie_id, people_id, department, job)
);

comment on column tmdb_movie_crews.department is '部门';

comment on column tmdb_movie_crews.job is '职务';

comment on column tmdb_movie_crews.credit_id is '信用ID';

create table tmdb_movie_cast
(
	movie_id integer not null
		references tmdb_movies,
	people_id integer not null
		references tmdb_people,
	"order" integer not null,
	character varchar,
	credit_id varchar,
	created_at timestamp default CURRENT_TIMESTAMP not null,
	updated_at timestamp default CURRENT_TIMESTAMP not null,
	primary key (movie_id, people_id, "order")
);

comment on column tmdb_movie_cast."order" is '排序';

comment on column tmdb_movie_cast.character is '角色';

comment on column tmdb_movie_cast.credit_id is '信用ID';

create table tmdb_tv
(
	id integer not null
		primary key,
	episode_run_time integer[] not null,
	first_air_date varchar,
	in_production boolean not null,
	languages character varying[] not null,
	last_air_date varchar,
	homepage varchar,
	overview varchar,
	tagline varchar,
	name varchar,
	next_episode_to_air jsonb,
	number_of_episodes integer not null,
	number_of_seasons integer not null,
	original_name varchar,
	type varchar,
	last_episode_to_air jsonb,
	networks jsonb,
	adult boolean not null,
	backdrop_path varchar,
	origin_country character varying[],
	status varchar,
	original_language varchar not null,
	popularity double precision not null,
	poster_path varchar,
	vote_average double precision not null,
	vote_count integer not null,
	external_ids jsonb,
	keywords jsonb,
	created_at timestamp default CURRENT_TIMESTAMP not null,
	updated_at timestamp default CURRENT_TIMESTAMP not null
);

comment on column tmdb_tv.episode_run_time is '每集时长';

comment on column tmdb_tv.first_air_date is '首播日期';

comment on column tmdb_tv.in_production is '是否在制作中';

comment on column tmdb_tv.languages is '语言';

comment on column tmdb_tv.last_air_date is '最近播放日期';

comment on column tmdb_tv.homepage is '主页URL';

comment on column tmdb_tv.overview is '概述';

comment on column tmdb_tv.tagline is '标语';

comment on column tmdb_tv.name is '标题';

comment on column tmdb_tv.next_episode_to_air is '下一集';

comment on column tmdb_tv.number_of_episodes is '集数';

comment on column tmdb_tv.number_of_seasons is '季数';

comment on column tmdb_tv.original_name is '原名称';

comment on column tmdb_tv.type is '类型';

comment on column tmdb_tv.last_episode_to_air is 'last_episode_to_air，作为JSON数组存储';

comment on column tmdb_tv.networks is 'networks，作为JSON数组存储';

comment on column tmdb_tv.adult is '是否为成人';

comment on column tmdb_tv.backdrop_path is '背景图片路径';

comment on column tmdb_tv.origin_country is '原产国';

comment on column tmdb_tv.status is '状态';

comment on column tmdb_tv.original_language is '原语言';

comment on column tmdb_tv.popularity is '流行度';

comment on column tmdb_tv.poster_path is '海报路径';

comment on column tmdb_tv.vote_average is '平均评分';

comment on column tmdb_tv.vote_count is '评分人数';

comment on column tmdb_tv.external_ids is 'external_ids，作为JSON数组存储';

comment on column tmdb_tv.keywords is 'keywords，作为JSON数组存储';

create table tmdb_tv_created_by
(
	tv_id integer not null
		references tmdb_tv,
	created_by_id integer not null
		references tmdb_created_by,
	primary key (tv_id, created_by_id)
);

create table tmdb_tv_genres
(
	tv_id integer not null
		references tmdb_tv,
	genre_id integer not null
		references tmdb_genres,
	primary key (tv_id, genre_id)
);

create table tmdb_tv_production_companies
(
	tv_id integer not null
		references tmdb_tv,
	production_company_id integer not null
		references tmdb_production_companies,
	primary key (tv_id, production_company_id)
);

create table tmdb_tv_production_countries
(
	tv_id integer not null
		references tmdb_tv,
	production_country_id varchar not null
		references tmdb_production_countries,
	primary key (tv_id, production_country_id)
);

create table tmdb_tv_spoken_languages
(
	tv_id integer not null
		references tmdb_tv,
	spoken_language_id varchar not null
		references tmdb_spoken_languages,
	primary key (tv_id, spoken_language_id)
);

create table tmdb_tv_translations
(
	tv_id integer not null
		references tmdb_tv,
	iso_3166_1 varchar(2) not null,
	iso_639_1 varchar(2) not null,
	lang_name varchar,
	english_name varchar,
	homepage varchar,
	overview varchar,
	tagline varchar,
	name varchar,
	created_at timestamp default CURRENT_TIMESTAMP not null,
	updated_at timestamp default CURRENT_TIMESTAMP not null,
	primary key (tv_id, iso_3166_1, iso_639_1)
);

comment on column tmdb_tv_translations.iso_3166_1 is '国家的ISO 3166-1代码';

comment on column tmdb_tv_translations.iso_639_1 is '语言的ISO 639-1代码';

comment on column tmdb_tv_translations.lang_name is '语言的本地名称';

comment on column tmdb_tv_translations.english_name is '语言的英语名称';

comment on column tmdb_tv_translations.homepage is '翻译版本的主页URL';

comment on column tmdb_tv_translations.overview is '翻译版本的概述';

comment on column tmdb_tv_translations.tagline is '翻译版本的标语';

comment on column tmdb_tv_translations.name is '翻译版本的标题';

create table tmdb_tv_alternative_titles
(
	tv_id integer not null
		references tmdb_tv,
	iso_3166_1 varchar(2) not null,
	title varchar not null,
	type varchar,
	created_at timestamp default CURRENT_TIMESTAMP not null,
	updated_at timestamp default CURRENT_TIMESTAMP not null,
	primary key (tv_id, iso_3166_1)
);

comment on column tmdb_tv_alternative_titles.tv_id is '关联TV的ID';

comment on column tmdb_tv_alternative_titles.iso_3166_1 is '国家的ISO 3166-1代码';

comment on column tmdb_tv_alternative_titles.title is '电影的替代标题';

comment on column tmdb_tv_alternative_titles.type is '替代标题的类型';

create table tmdb_tv_images
(
	tv_id integer not null
		references tmdb_tv,
	iso_639_1 varchar(2),
	file_path varchar(255) not null
		primary key,
	image_type tmdbimagetypeenum not null,
	aspect_ratio double precision,
	height integer,
	width integer,
	vote_average double precision,
	vote_count integer,
	created_at timestamp default CURRENT_TIMESTAMP not null,
	updated_at timestamp default CURRENT_TIMESTAMP not null
);

create table tmdb_tv_videos
(
	tv_id integer not null
		references tmdb_tv,
	id varchar not null,
	iso_639_1 varchar(2) not null,
	iso_3166_1 varchar(2) not null,
	name varchar(255) not null,
	key varchar(255) not null,
	site varchar not null,
	size integer not null,
	type varchar not null,
	official boolean not null,
	published_at timestamp with time zone not null,
	tmdb_video_id varchar(255) not null,
	created_at timestamp default CURRENT_TIMESTAMP not null,
	updated_at timestamp default CURRENT_TIMESTAMP not null,
	primary key (tv_id, id)
);

create table tmdb_tv_seasons
(
	id integer not null
		primary key,
	overview varchar,
	name varchar,
	air_date varchar,
	episode_count integer,
	poster_path varchar,
	season_number integer not null,
	vote_average double precision not null,
	tv_show_id integer not null
		references tmdb_tv,
	created_at timestamp default CURRENT_TIMESTAMP not null,
	updated_at timestamp default CURRENT_TIMESTAMP not null
);

comment on column tmdb_tv_seasons.overview is '概述';

comment on column tmdb_tv_seasons.name is '标题';

comment on column tmdb_tv_seasons.air_date is '播放日期';

comment on column tmdb_tv_seasons.episode_count is '集数';

comment on column tmdb_tv_seasons.poster_path is '海报路径';

comment on column tmdb_tv_seasons.season_number is '季数';

comment on column tmdb_tv_seasons.vote_average is '平均评分';

create table tmdb_tv_season_translations
(
	tv_season_id integer not null
		references tmdb_tv_seasons,
	iso_3166_1 varchar(2) not null,
	iso_639_1 varchar(2) not null,
	lang_name varchar,
	english_name varchar,
	overview varchar,
	name varchar,
	created_at timestamp default CURRENT_TIMESTAMP not null,
	updated_at timestamp default CURRENT_TIMESTAMP not null,
	primary key (tv_season_id, iso_3166_1, iso_639_1)
);

comment on column tmdb_tv_season_translations.iso_3166_1 is '国家的ISO 3166-1代码';

comment on column tmdb_tv_season_translations.iso_639_1 is '语言的ISO 639-1代码';

comment on column tmdb_tv_season_translations.lang_name is '语言的本地名称';

comment on column tmdb_tv_season_translations.english_name is '语言的英语名称';

comment on column tmdb_tv_season_translations.overview is '翻译版本的概述';

comment on column tmdb_tv_season_translations.name is '翻译版本的标题';

create table tmdb_tv_episodes
(
	id serial
		primary key,
	overview varchar,
	name varchar,
	air_date varchar,
	episode_number integer,
	episode_type varchar,
	production_code varchar,
	runtime integer,
	season_number integer,
	show_id integer,
	vote_average integer,
	vote_count integer,
	tv_season_id integer not null
		references tmdb_tv_seasons,
	created_at timestamp default CURRENT_TIMESTAMP not null,
	updated_at timestamp default CURRENT_TIMESTAMP not null
);

comment on column tmdb_tv_episodes.overview is '概述';

comment on column tmdb_tv_episodes.name is '标题';

comment on column tmdb_tv_episodes.air_date is '播放日期';

comment on column tmdb_tv_episodes.episode_number is '集数';

comment on column tmdb_tv_episodes.episode_type is '类型';

comment on column tmdb_tv_episodes.production_code is '制作代码';

comment on column tmdb_tv_episodes.runtime is '时长（分钟）';

comment on column tmdb_tv_episodes.season_number is '季数';

comment on column tmdb_tv_episodes.show_id is '剧集 ID';

comment on column tmdb_tv_episodes.vote_average is '平均评分';

comment on column tmdb_tv_episodes.vote_count is '评分人数';

create table tmdb_tv_season_crews
(
	tv_season_id integer not null
		references tmdb_tv_seasons,
	people_id integer not null
		references tmdb_people,
	department varchar not null,
	job varchar not null,
	credit_id varchar,
	created_at timestamp default CURRENT_TIMESTAMP not null,
	updated_at timestamp default CURRENT_TIMESTAMP not null,
	primary key (tv_season_id, people_id, department, job)
);

comment on column tmdb_tv_season_crews.department is '部门';

comment on column tmdb_tv_season_crews.job is '职务';

comment on column tmdb_tv_season_crews.credit_id is '信用ID';

create table tmdb_tv_season_cast
(
	tv_season_id integer not null
		references tmdb_tv_seasons,
	people_id integer not null
		references tmdb_people,
	"order" integer not null,
	character varchar,
	credit_id varchar,
	created_at timestamp default CURRENT_TIMESTAMP not null,
	updated_at timestamp default CURRENT_TIMESTAMP not null,
	primary key (tv_season_id, people_id, "order")
);

comment on column tmdb_tv_season_cast."order" is '排序';

comment on column tmdb_tv_season_cast.character is '角色';

comment on column tmdb_tv_season_cast.credit_id is '信用ID';

create table tmdb_tv_episodes_translations
(
	tv_episode_id integer not null
		references tmdb_tv_episodes,
	iso_3166_1 varchar(2) not null,
	iso_639_1 varchar(2) not null,
	lang_name varchar,
	english_name varchar,
	overview varchar,
	name varchar,
	created_at timestamp default CURRENT_TIMESTAMP not null,
	updated_at timestamp default CURRENT_TIMESTAMP not null,
	primary key (tv_episode_id, iso_3166_1, iso_639_1)
);

comment on column tmdb_tv_episodes_translations.iso_3166_1 is '国家的ISO 3166-1代码';

comment on column tmdb_tv_episodes_translations.iso_639_1 is '语言的ISO 639-1代码';

comment on column tmdb_tv_episodes_translations.lang_name is '语言的本地名称';

comment on column tmdb_tv_episodes_translations.english_name is '语言的英语名称';

comment on column tmdb_tv_episodes_translations.overview is '翻译版本的概述';

comment on column tmdb_tv_episodes_translations.name is '翻译版本的标题';

create table tmdb_tv_episode_guest_stars
(
	tv_episode_id integer not null
		references tmdb_tv_episodes,
	people_id integer not null
		references tmdb_people,
	"order" integer not null,
	character varchar,
	credit_id varchar,
	created_at timestamp default CURRENT_TIMESTAMP not null,
	updated_at timestamp default CURRENT_TIMESTAMP not null,
	primary key (tv_episode_id, people_id, "order")
);

comment on column tmdb_tv_episode_guest_stars."order" is '排序';

comment on column tmdb_tv_episode_guest_stars.character is '角色';

comment on column tmdb_tv_episode_guest_stars.credit_id is '信用ID';

create table tmdb_tv_episode_crews
(
	tv_episode_id integer not null
		references tmdb_tv_episodes,
	people_id integer not null
		references tmdb_people,
	department varchar not null,
	job varchar not null,
	credit_id varchar,
	created_at timestamp default CURRENT_TIMESTAMP not null,
	updated_at timestamp default CURRENT_TIMESTAMP not null,
	primary key (tv_episode_id, people_id, department, job)
);

comment on column tmdb_tv_episode_crews.department is '部门';

comment on column tmdb_tv_episode_crews.job is '职务';

comment on column tmdb_tv_episode_crews.credit_id is '信用ID';

create table tmdb_tv_episodes_crew
(
	tv_episodes_id integer not null
		references tmdb_tv_episodes,
	people_id integer not null
		references tmdb_people,
	"order" integer not null,
	character varchar,
	credit_id varchar,
	created_at timestamp default CURRENT_TIMESTAMP not null,
	updated_at timestamp default CURRENT_TIMESTAMP not null,
	primary key (tv_episodes_id, people_id, "order")
);

comment on column tmdb_tv_episodes_crew."order" is '排序';

comment on column tmdb_tv_episodes_crew.character is '角色';

comment on column tmdb_tv_episodes_crew.credit_id is '信用ID';

