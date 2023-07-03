import json

import web3.constants
from tornado import gen
from tornado.log import app_log

from handlers.base_handler import BaseHandler


class EventLogListHandler(BaseHandler):
    """Event Log Of Nft"""

    @gen.coroutine
    def post(self):
        args = self.parse_json_arguments('contract_address', 'token_id', 'network')
        yield self.check_auth()
        if not web3.Web3.is_address(args.contract_address):
            self.fail(400)
        res = yield self.mg.query_nft_flow_logs(args.contract_address, args.token_id, args.network)
        res_dict = dict()
        if res:
            log_list = []
            for event in res:
                inner_dict = dict()
                if event["from"] == web3.constants.ADDRESS_ZERO:
                    inner_dict["event"] = "Mint"
                if event["to"] == web3.constants.ADDRESS_ZERO:
                    inner_dict["event"] = "Burn"
                inner_dict["from"] = event["from"]
                inner_dict["to"] = event["to"]
                inner_dict["transactionHash"] = event["transactionHash"]
                inner_dict["blockNumber"] = event["blockNumber"]
                inner_dict["operator"] = event["operator"]
                inner_dict["timestamp"] = event["timestamp"]
                log_list.append(inner_dict)
            res_dict["contractAddress"] = args.contract_address
            res_dict["tokenId"] = args.token_id
            res_dict["network"] = args.network
            res_dict["logs"] = log_list
        self.success(data=res_dict)

    def sort_key(self, params):
        """
        Sort list order by "blockNumber"
        :param params: dict
        :return:
        """
        return params["blockNumber"]
