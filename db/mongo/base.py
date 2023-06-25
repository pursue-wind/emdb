# coding:utf-8
"""Predefination of mongo schema."""
from motor import MotorGridFSBucket, motor_tornado
from pymongo import MongoClient

from config import CFG as cfg

MC = motor_tornado.MotorClient(cfg.mongo.client).__getattr__(cfg.mongo.db)
MS_CLIENT = MongoClient(cfg.mongo.client).__getattr__(cfg.mongo.db)


class MongoBase():
    """Mongo Client Set."""
    m_client = MC
    ms_client = MS_CLIENT
    session = MC.session

    def __init__(self):
        self._init_collection()

    def _init_collection(self):
        # nft event logs collection
        self.logs = MC.logs
        self.blockHeight = MC.blockHeight
        self.account = MC.account
        self.nftFlowLog = MC.nftFlowLog
        self.status_message = MC.statusMessage




