# EMDB 影视数据服务
> 同步 TMDb 数据到本地

## 安装依赖
```shell
pip install -r requirements.txt
```

## 项目启动
```shell
python3 main.py
```

### 根据环境变量`ENV`读取 setting.yaml 内的配置
- ENV：
  - local
  - dev
  - test
  - release

> script.sh 是重构前的启动脚本，可以不用也可以继续使用
---

## EMDB API
> APIFOX 链接: https://pursue-wind.apifox.cn  访问密码: likn1234
 
新版本只有下面4个接口，其他接口都是为了兼容重构之前版本的接口返回做了数据转换
- GET /api/emdb/movie/{id}
- POST /api/emdb/movie/{id}
- GET /api/emdb/tv/{id}
- POST /api/emdb/tv/{id}

### 电影 API

#### 导入电影

- **URL**: `/api/emdb/movie/{id}`
- **方法**: `POST`

#### 获取电影详情

- **URL**: `/api/emdb/movie/{id}`
- **方法**: `GET`
- **描述**: 根据电影 ID 获取电影的详细信息。
    - 支持lang参数获取对应语言的数据
        - zh-CN
        - zh-TW
        - en
        - ...
    - 支持join参数关联movie相关的表
        - genres
        - production_companies
        - production_countries
        - cast
        - crew
        - release_dates
        - images
        - videos

```shell
curl --location --request GET 'http://127.0.0.1:8088/api/emdb/movie/993621?lang=zh-TW&join=belongs_to_collectionfr&join=genres&join=spoken_languages&join=cast&join=crew&join=images&join=videos' \
--header 'Authorization: Bearer MmdxY3ZkbGtxYnJtNTY6ZmVlZDBmMjRlMzFhMjM1Z2Q4YjdlNGJlZDFmZWM0ZGQyNjU1' \
--header 'User-Agent: Apifox/1.0.0 (https://apifox.com)'
```

#### 获取电影图片 (为了兼容之前的接口添加，做结果返回的参数转换)

- **URL**: `/api/movie/images`
- **方法**: `GET`
- **描述**: 获取电影的图片信息。

#### 获取电影翻译 (为了兼容之前的接口添加，做结果返回的参数转换)

- **URL**: `/api/movie/translations`
- **方法**: `GET`
- **描述**: 获取电影的翻译信息。

#### 获取电影的别名 (为了兼容之前的接口添加，做结果返回的参数转换)

- **URL**: `/api/movie/alternative_titles`
- **方法**: `GET`
- **描述**: 获取电影的别名信息。

#### 获取电影演员/工作人员 (为了兼容之前的接口添加，做结果返回的参数转换)

- **URL**: `/api/movie/credits`
- **方法**: `GET`
- **描述**: 获取电影的演员表和工作人员信息。

#### 获取电影上映日期 (为了兼容之前的接口添加，做结果返回的参数转换)

- **URL**: `/api/movie/release_dates`
- **方法**: `GET`
- **描述**: 获取电影的上映日期信息。

#### 获取电影视频 (为了兼容之前的接口添加，做结果返回的参数转换)

- **URL**: `/api/movie/videos`
- **方法**: `GET`
- **描述**: 获取电影的相关视频（如预告片）。

### 电视节目 API

#### 导入电视节目

- **URL**: `/api/emdb/tv/{id}`
- **方法**: `POST`

#### 获取电视节目详情

- **URL**: `/api/emdb/tv/{id}`
- **方法**: `GET`
- **描述**: 根据电视节目 ID 获取详细信息。
    - 支持lang参数获取对应语言的数据
        - zh-CN
        - zh-TW
        - en
        - ...
    - 支持join参数关联movie相关的表
        - created_by
        - genres
        - networks
        - production_companies
        - production_countries
        - seasons
        - episodes
        - season_cast
        - season_crew
        - spoken_languages

```shell
curl --location --request GET 'http://127.0.0.1:8088/api/emdb/tv/68006?lang=zh-CN&join=belongs_to_collectionfr&join=genres&join=spoken_languages&join=seasons&join=images&join=videos&join=episodes' \
--header 'Authorization: Bearer MmdxY3ZkbGtxYnJtNTY6ZmVlZDBmMjRlMzFhMjM1Z2Q4YjdlNGJlZDFmZWM0ZGQyNjU1' \
--header 'User-Agent: Apifox/1.0.0 (https://apifox.com)'
```

#### 获取电视节目图片 (为了兼容之前的接口添加，做结果返回的参数转换)

- **URL**: `/api/tv/images`
- **方法**: `GET`
- **描述**: 获取电视节目的图片信息。

#### 获取电视节目的剧集 (为了兼容之前的接口添加，做结果返回的参数转换)

- **URL**: `/api/tv/episodes`
- **方法**: `GET`
- **描述**: 获取电视节目的剧集信息。

#### 获取电视节目翻译 (为了兼容之前的接口添加，做结果返回的参数转换)

- **URL**: `/api/tv/translations`
- **方法**: `GET`
- **描述**: 获取电视节目的翻译信息。

#### 获取电视节目的别名 (为了兼容之前的接口添加，做结果返回的参数转换)

- **URL**: `/api/tv/alternative_titles`
- **方法**: `GET`
- **描述**: 获取电视节目的别名信息。

#### 获取电视节目演员/工作人员 (为了兼容之前的接口添加，做结果返回的参数转换)

- **URL**: `/api/tv/credits`
- **方法**: `GET`
- **描述**: 获取电视节目的演员表和工作人员信息。

#### 获取电视节目上映日期 (为了兼容之前的接口添加，电视实际上没有上映日期，返回空列表)

- **URL**: `/api/tv/release_dates`
- **方法**: `GET`
- **描述**: 电视实际上没有上映日期，返回空列表。

#### 获取电视节目视频 (为了兼容之前的接口添加，做结果返回的参数转换)

- **URL**: `/api/tv/videos`
- **方法**: `GET`
- **描述**: 获取电视节目的相关视频（如预告片）。

### EMMAI 服务使用接口

#### 统计EMDB电影电视数量

- **URL**: `/api/media/count`
- **方法**: `GET`

#### 从当前EMDB数据库中搜索TV

- **URL**: `/api/company/tv`
- **方法**: `POST`

#### 从当前EMDB数据库中搜索MOVIE

- **URL**: `/api/company/movie`
- **方法**: `POST`

### EMMAI admin使用

#### 推荐影视

- **URL**: `/api/emdb/discover`
- **方法**: `GET`

#### 从TMDB搜索影视

- **URL**: `/api/emdb/search`
- **方法**: `GET`
- **描述**: 根据关键字搜索电影和电视节目。

---

## 待完善

- EMMAI导入数据改用新的api

## 生产环境数据库替换
- 导出数据为sql文件
```shell
psql postgresql://emmai:fsv33inhTeHkhY5@8.218.184.1:54321/emdb -f /path/to/yourfile.sql
# 把sql的schema去除
find /data/emdb/emdb/sql_temp/data -name "tmdb*.sql" | xargs -I {} sed -i 's/public\.//g' {}
# 使用sed命令将 , order, 替换为 , "order", 
find /data/emdb/emdb/sql_temp/data -name "tmdb*cast.sql" | xargs -I {} sed -i 's/, order,/, "order",/g' {}
find /data/emdb/emdb/sql_temp/data -name "tmdb*crew.sql" | xargs -I {} sed -i 's/, order,/, "order",/g' {}
find /data/emdb/emdb/sql_temp/data -name "tmdb_tv_episode_guest_stars.sql" | xargs -I {} sed -i 's/, order,/, "order",/g' {}

# 按照关联顺序导入数据，此处配置为测试环境的配置
find /data/emdb/emdb/sql_temp/data -name "tmdb_genres*.sql" | xargs -I {} psql postgresql://emmai:fsv33inhTeHkhY5@8.218.184.1:54321/emdb -f {}
find /data/emdb/emdb/sql_temp/data -name "tmdb_people.sql" | xargs -I {} psql postgresql://emmai:fsv33inhTeHkhY5@8.218.184.1:54321/emdb -f {}

find /data/emdb/emdb/sql_temp/data -name "tmdb_production_companies.sql" | xargs -I {} psql postgresql://emmai:fsv33inhTeHkhY5@8.218.184.1:54321/emdb -f {}
find /data/emdb/emdb/sql_temp/data -name "tmdb_production_countries.sql" | xargs -I {} psql postgresql://emmai:fsv33inhTeHkhY5@8.218.184.1:54321/emdb -f {}
find /data/emdb/emdb/sql_temp/data -name "tmdb_spoken_languages.sql" | xargs -I {} psql postgresql://emmai:fsv33inhTeHkhY5@8.218.184.1:54321/emdb -f {}

find /data/emdb/emdb/sql_temp/data -name "tmdb_movies.sql" | xargs -I {} psql postgresql://emmai:fsv33inhTeHkhY5@8.218.184.1:54321/emdb -f {}
find /data/emdb/emdb/sql_temp/data -name "tmdb_tv.sql" | xargs -I {} psql postgresql://emmai:fsv33inhTeHkhY5@8.218.184.1:54321/emdb -f {}


find /data/emdb/emdb/sql_temp/data -name "tmdb*cast.sql" | xargs -I {} psql postgresql://emmai:fsv33inhTeHkhY5@8.218.184.1:54321/emdb -f {}
find /data/emdb/emdb/sql_temp/data -name "tmdb*crew.sql" | xargs -I {} psql postgresql://emmai:fsv33inhTeHkhY5@8.218.184.1:54321/emdb -f {}

find /data/emdb/emdb/sql_temp/data -name "tmdb_movie_*.sql" | xargs -I {} psql postgresql://emmai:fsv33inhTeHkhY5@8.218.184.1:54321/emdb -f {}

find /data/emdb/emdb/sql_temp/data -name "tmdb_tv_episodes.sql" | xargs -I {} psql postgresql://emmai:fsv33inhTeHkhY5@8.218.184.1:54321/emdb -f {}
find /data/emdb/emdb/sql_temp/data -name "tmdb_tv_seasons.sql" | xargs -I {} psql postgresql://emmai:fsv33inhTeHkhY5@8.218.184.1:54321/emdb -f {}

find /data/emdb/emdb/sql_temp/data -name "tmdb_tv_*.sql" | xargs -I {} psql postgresql://emmai:fsv33inhTeHkhY5@8.218.184.1:54321/emdb -f {}

```

根据这个帖子：TMDB season/episode ID 不会重复
https://www.themoviedb.org/talk/552e997ac3a36804cd0013ab