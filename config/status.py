# coding:utf-8
"""Here is some status defination."""
from config import CFG as cfg
import yaml

# MS_CLIENT = MongoClient(cfg.mongo.client).__getattr__(
#     cfg.mongo.db)
#

class NormalStatus:
    """To be generated."""
    def __init__(self):
        try:
            with open('config/status.yaml', 'r', encoding='utf-8') as status:
                STATUS = yaml.load(status, Loader=yaml.FullLoader)
        except FileNotFoundError:
            exit(0)

        self._status = dict()

        for item in STATUS:
            self._status[item['code']] = item['msg']

    def get_status_message(self, code):
        if code == -1:
            return None
        status_dict = self._status
        try:
            return status_dict[code]
        except KeyError:
            raise KeyError(f'Unknown status {code}.')


NS = NormalStatus()