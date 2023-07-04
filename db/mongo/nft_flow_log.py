# coding:utf-8
"""Predefination of mongo schema."""
from datetime import datetime

import web3.constants
from tornado import gen
from tornado.log import app_log

from db.mongo.base import MongoBase


class NftFlowLog(MongoBase):
    """Nft Flow Logs"""

    @gen.coroutine
    def query_nft_flow_logs(self, address, token_id, network):
        result = self.nft_flow_log.find(
            dict(contractAddress=address, tokenId=token_id, network=network), projection=dict(_id=0)).sort("timestamp",
                                                                                                           -1)
        res_list = yield result.to_list(length=1000)
        return res_list

    @gen.coroutine
    def query_nft_flow_to_user(self, contract_addr, token_id, network, user_addr):
        """查询创建nft的地址"""
        filter_param = {
            "contractAddress": contract_addr,
            "tokenId": token_id,
            "network": network,
            "from": web3.constants.ADDRESS_ZERO,
            "to": user_addr
        }
        result = self.nft_flow_log.find(filter_param, projection=dict(_id=0))
        res_list = yield result.to_list(length=None)
        return res_list

    @gen.coroutine
    def query_proxy_address(self):
        result = self.nft_flow_log.find({"event": "Create1155RaribleUserProxy"})
        res_list = yield result.to_list(length=None)
        return res_list

    @gen.coroutine
    def query_collected_nft(self, owner_address, contract_address, token_id):
        query_conditions = {"from": owner_address, "contractAddress": contract_address, "tokenId": token_id}
        # return a MotorCursor Object
        result = self.nft_flow_log.find(query_conditions, projection=dict(_id=0))
        res_list = yield result.to_list(length=None)
        return res_list

    @gen.coroutine
    def update_nft_flow_logs(self, nft_logs):
        if "tokenId" in nft_logs.keys():
            yield self.nft_flow_log.update_one(
                dict(network=nft_logs["network"], contractAddress=nft_logs["contractAddress"],
                     tokenId=nft_logs["tokenId"]),
                {'$addToSet': {
                    'logs': nft_logs["logs"]
                }, "$set": {"updateTime": datetime.utcnow()}},
                upsert=True)
        else:
            self.nft_flow_log.update_one(
                dict(network=nft_logs["network"], contractAddress=nft_logs["contractAddress"]),
                {'$addToSet': {
                    'logs': nft_logs
                }, "$set": {"updateTime": datetime.utcnow()}}, upsert=True)

    @gen.coroutine
    def insert_nft_flow_logs(self, nft_logs):
        yield self.nft_flow_log.insert_many(nft_logs)

    @gen.coroutine
    def insert_one_nft_flow_log(self, nft_logs):
        try:
            yield self.nft_flow_log.insert_one(nft_logs)
        except Exception as e:
            app_log.error(e)
