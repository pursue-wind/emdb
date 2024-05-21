import string

from tornado import ioloop

from lib.utils.excels import read_excel
from service.fetch_tv_series_info import get_tv_detail, import_tv_emdb_by_series_id
language = "zh"
# country = "CN"
file_path = "docs/movies.xlsx"

company_id = 100000007
if __name__ == '__main__':
    io_loop = ioloop.IOLoop.current()
    # io_loop.run_sync(lambda: get_tv_detail(122790, None))

    """import movie to emdb by movie name"""
    tvs = read_excel(file_path, "tvs")
    # tvs = pd.read_excel(file_path, "tvs")

    tmdb_series_id_list = [serise_id[0] for serise_id in tvs[1:]]
    season_id_list = [season_id[2] for season_id in tvs[1:]]

    # for i in range(1, len(tvs)):
    #     series_name = str(tvs.iloc[i, 1])  # 读取电视剧名称，假设为第二列
    #     season = 1  # 默认季数为0，表示未知
    #
    #     # 使用关键词匹配判断季数信息
    #     if "第一季" in series_name or "S1" in series_name:
    #         season = 1
    #     elif "第二季" in series_name or "S2" in series_name:
    #         season = 2
    #     elif "第三季" in series_name or "S3" in series_name:
    #         season = 3
    #     elif "第四季" in series_name or "S4" in series_name:
    #         season = 4
    #     elif "第五季" in series_name or "S5" in series_name:
    #         season = 5
    #     elif "第六季" in series_name or "S6" in series_name:
    #         season = 6
    #     elif "第七季" in series_name or "S7" in series_name:
    #         season = 7
    #     elif "第八季" in series_name or "S8" in series_name:
    #         season = 8
    #     elif "第九季" in series_name or "S8" in series_name:
    #         season = 9
    #     elif "第十季" in series_name or "S8" in series_name:
    #         season = 10
    #
    #     # 填写第三列季数信息
    #     tvs.at[i, '季数'] = season

    # 保存修改后的 Excel 文件
    # tvs.to_excel(file_path, index=False)
    io_loop.run_sync(lambda: import_tv_emdb_by_series_id(tmdb_series_id_list,season_id_list, company_id))



