# coding:utf-8
"""Here is some status defination."""
from config import CFG as cfg
from pymongo import MongoClient
import yaml

MS_CLIENT = MongoClient(cfg.mongo.client).__getattr__(
    cfg.mongo.db)


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

        for status in STATUS:
            self._set_status(
                status['code'],
                dict(
                    msg=status.get('msg')))
        self._update_status()

    def _set_status(self, status, message_dict):
        MS_CLIENT.status_message.update_one(
            dict(status=status), {'$set': message_dict}, upsert=True)

    def _get_status(self, status):
        result = MS_CLIENT.status_message.find_ones(
            dict(status=status), projection=dict(_id=0))
        return result

    def _update_status(self):
        self.cn_status = dict()
        result = MS_CLIENT.status_message.find(
            dict(
                status={'$exists': True},
                msg={'$exists': True}),
            projection=dict(_id=0, status=1, msg=1))
        for item in result:
            self._status[item['status']] = item['msg']

    def get_status_message(self, code):
        if code == -1:
            return None
        status_dict = self._status
        try:
            return status_dict[code]
        except KeyError:
            raise KeyError(f'Unknown status {code}.')


NS = NormalStatus()