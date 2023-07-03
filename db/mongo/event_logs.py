# coding:utf-8
"""Predefination of mongo schema."""
from datetime import datetime

from tornado import gen

from db.mongo.base import MongoBase


class LogsTasks(MongoBase):
    """Event Logs"""

    @gen.coroutine
    def query_address_logs(self, address):
        result = yield self.logs.find_one(
            dict(address=address), projection=dict(_id=0, timestamp=0))
        return result

    @gen.coroutine
    def update_logs(self, address, logs):
        self.logs.update_one(
            dict(address=address),
            {'$set': {
                'log': logs,
                'time': datetime.utcnow()
            }},
            upsert=True)

    @gen.coroutine
    def insert_logs(self, logs):
        yield self.logs.insert_many(logs)



