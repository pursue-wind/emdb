# EMDB 影视数据服务

> 同步 TMDb 数据到本地

---

## EMDB API

## 电影 API

### 导入电影

- **URL**: `/api/emdb/movie/{id}`
- **方法**: `POST`

### 获取电影详情

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

### 获取电影图片 (为了兼容之前的接口添加，做结果返回的参数转换)

- **URL**: `/api/movie/images`
- **方法**: `GET`
- **描述**: 获取电影的图片信息。

### 获取电影翻译 (为了兼容之前的接口添加，做结果返回的参数转换)

- **URL**: `/api/movie/translations`
- **方法**: `GET`
- **描述**: 获取电影的翻译信息。

### 获取电影的别名 (为了兼容之前的接口添加，做结果返回的参数转换)

- **URL**: `/api/movie/alternative_titles`
- **方法**: `GET`
- **描述**: 获取电影的别名信息。

### 获取电影演员/工作人员 (为了兼容之前的接口添加，做结果返回的参数转换)

- **URL**: `/api/movie/credits`
- **方法**: `GET`
- **描述**: 获取电影的演员表和工作人员信息。

### 获取电影上映日期 (为了兼容之前的接口添加，做结果返回的参数转换)

- **URL**: `/api/movie/release_dates`
- **方法**: `GET`
- **描述**: 获取电影的上映日期信息。

### 获取电影视频 (为了兼容之前的接口添加，做结果返回的参数转换)

- **URL**: `/api/movie/videos`
- **方法**: `GET`
- **描述**: 获取电影的相关视频（如预告片）。

## 电视节目 API

### 导入电视节目

- **URL**: `/api/emdb/tv/{id}`
- **方法**: `POST`

### 获取电视节目详情

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

### 获取电视节目图片 (为了兼容之前的接口添加，做结果返回的参数转换)

- **URL**: `/api/tv/images`
- **方法**: `GET`
- **描述**: 获取电视节目的图片信息。

### 获取电视节目的剧集 (为了兼容之前的接口添加，做结果返回的参数转换)

- **URL**: `/api/tv/episodes`
- **方法**: `GET`
- **描述**: 获取电视节目的剧集信息。

### 获取电视节目翻译 (为了兼容之前的接口添加，做结果返回的参数转换)

- **URL**: `/api/tv/translations`
- **方法**: `GET`
- **描述**: 获取电视节目的翻译信息。

### 获取电视节目的别名 (为了兼容之前的接口添加，做结果返回的参数转换)

- **URL**: `/api/tv/alternative_titles`
- **方法**: `GET`
- **描述**: 获取电视节目的别名信息。

### 获取电视节目演员/工作人员 (为了兼容之前的接口添加，做结果返回的参数转换)

- **URL**: `/api/tv/credits`
- **方法**: `GET`
- **描述**: 获取电视节目的演员表和工作人员信息。

### 获取电视节目上映日期 (为了兼容之前的接口添加，电视实际上没有上映日期，返回空列表)

- **URL**: `/api/tv/release_dates`
- **方法**: `GET`
- **描述**: 电视实际上没有上映日期，返回空列表。

### 获取电视节目视频 (为了兼容之前的接口添加，做结果返回的参数转换)

- **URL**: `/api/tv/videos`
- **方法**: `GET`
- **描述**: 获取电视节目的相关视频（如预告片）。

## EMMAI 服务使用接口

### 统计EMDB电影电视数量

- **URL**: `/api/media/count`
- **方法**: `GET`

### 从当前EMDB数据库中搜索TV

- **URL**: `/api/company/tv`
- **方法**: `POST`

### 从当前EMDB数据库中搜索MOVIE

- **URL**: `/api/company/movie`
- **方法**: `POST`

## EMMAI admin使用

### 推荐影视

- **URL**: `/api/emdb/discover`
- **方法**: `GET`

### 从TMDB搜索影视

- **URL**: `/api/emdb/search`
- **方法**: `GET`
- **描述**: 根据关键字搜索电影和电视节目。

---

## 待完善

- EMMAI导入数据改用新的api

- TMDb 数据导入错误记录到数据库

- 导入影视进度反馈给前端