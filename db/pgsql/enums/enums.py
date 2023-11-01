from enum import Enum


def get_key_by_value(enum_class, value):
    enum_dict = {member.value: member.name for member in enum_class}
    return enum_dict.get(value)


class SourceType(Enum):
    """
    source type
    """
    Movie = 1
    Tv = 2


class ReleaseTypes(Enum):
    """Release types"""
    Premiere = 1  # 首映
    LimitedTheatrical = 2  # 戏剧（有限）
    Theatrical = 3  # 戏剧
    Digital = 4  # 数字
    Physical = 5  # 实体
    TV = 6  # 电视


class GenresType(Enum):
    """Movie And Tv Genres Types"""
    Action = 28
    Adventure = 12
    Animation = 16
    Comedy = 35
    Crime = 80
    Documentary = 99
    Drama = 18
    Family = 10751
    Fantasy = 14
    History = 36
    Horror = 27
    Music = 10402
    Mystery = 9648
    Romance = 10749
    ScienceFiction = 878
    TVMovie = 10770
    Thriller = 53
    War = 10752
    Western = 37
    ActionAdventure = 10759
    Kids = 10762
    News = 10763
    Reality = 10764
    SciFiFantasy = 10765
    Soap = 10766
    Talk = 10767
    WarPolitics = 10768


class VideoType(Enum):
    """Video type"""
    Trailer = "Trailer"
    Teaser = "Teaser"
    Clip = "Clip"
    Featurette = "Featurette"
    BehindTheScenes = "Behind the Scenes"
    Bloopers = "Bloopers"
    Interview = "Interview"
    OpeningCredits = "Opening Credits"
    EndingCredits = "Ending Credits"


class ImagesType(Enum):
    Logo = 1
    Poster = 2
    Backdrop = 3


class CreditType(Enum):
    cast = 1
    crew = 2


class Gender(Enum):
    female = 1
    male = 2


class VideoSiteUlr(Enum):
    """Video site url"""
    YouTube = "https://www.youtube.com/watch?v="
    Vimeo = "https://vimeo.com/"
