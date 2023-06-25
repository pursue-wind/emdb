import json

import web3.constants
from tornado import gen
from tornado.log import app_log

from handlers.base_handler import BaseHandler


class EventLogListHandler(BaseHandler):
    """Event Log Of Nft"""

    @gen.coroutine
    def post(self):
        app_log.info(f"request params: {json.loads(self.request.body.decode())}")
        args = self.parse_json_arguments('contract_address', 'token_id')
        yield self.check_auth()
        if not web3.Web3.is_address(args.contract_address):
            self.fail(400)
        res = yield self.mg.query_nft_flow(args.contract_address, args.token_id)
        if res is not None:
            log_list = []
            event_logs = res['logs']
            for e in event_logs:
                if e["from"] == web3.constants.ADDRESS_ZERO:
                    e["event"] = "Mint"
                if e["to"] == web3.constants.ADDRESS_ZERO:
                    e["event"] = "Burn"
                log_list.append(e)
            res["logs"] = log_list
        app_log.info(f"res: {type(res)},{res}")
        self.success(data=res)
