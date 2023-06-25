# coding:utf-8
"""Predefination of mongo schema."""
from datetime import datetime

from tornado import gen

from db.mongo.base import MongoBase


class BlockHeight(MongoBase):
    """Record scaned block and current block height"""

    @gen.coroutine
    def query_scaned_block_height(self, event_name, network):
        result = yield self.blockHeight.find_one({"eventName": event_name, "network": network})
        return result

    @gen.coroutine
    def update_block_height(self, filter_params, scaned_block_height):
        self.blockHeight.update_one(filter_params, {'$set': scaned_block_height}, upsert=True)

    @gen.coroutine
    def insert_block_height(self, logs):
        self.blockHeight.insert(logs)



