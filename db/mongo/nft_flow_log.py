# coding:utf-8
"""Predefination of mongo schema."""
from datetime import datetime

from tornado import gen

from db.mongo.base import MongoBase


class NftFlowLog(MongoBase):
    """Nft Flow Logs"""

    @gen.coroutine
    def query_nft_flow(self, address, token_id, network):
        result = yield self.nftFlowLog.find_one(
            dict(contractAddress=address, tokenId=token_id, network=network), projection=dict(_id=0, updateTime=0))
        return result

    @gen.coroutine
    def update_nft_flow_logs(self, nft_logs):
        # print(f"update_nft_flow_logs: {nft_logs}")
        if "tokenId" in nft_logs.keys():
            self.nftFlowLog.update_one(
                dict(network=nft_logs["network"], contractAddress=nft_logs["contractAddress"], tokenId=nft_logs["tokenId"]),
                {'$addToSet': {
                    'logs': nft_logs["logs"]
                }, "$set": {"updateTime": datetime.utcnow()}},
                upsert=True)
        else:
            self.nftFlowLog.update_one(
                dict(network=nft_logs["network"], contractAddress=nft_logs["contractAddress"]),
                    {'$addToSet': {
                        'logs': nft_logs
                    }, "$set": {"updateTime": datetime.utcnow()}},
                    upsert=True)



