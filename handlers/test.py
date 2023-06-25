import json
import time

import tornado
from tornado import gen
from tornado.log import app_log

from handlers.base_handler import BaseHandler


class IndexHandler(BaseHandler):

    @gen.coroutine
    def get(self, *args, **kwargs):
        result = yield self.fun()  # 异步查询数据

        # yield time.sleep(10)
        self.write(str(result))
        # self.finish()

    @gen.coroutine
    def post(self):
        app_log.info(f"request params: {json.loads(self.request.body.decode())}")
        # log = self.parse_json_arguments('log')
        # i = self.parse_json_arguments("i")
        args = self.parse_json_arguments(
            'user_id', 'coin_type', 'coin_amount', 'trade_type', 'trade_price',
            'trade_amount', 'user_sign', 'company_order_num', 'currency_type')

        print(args)
        res = yield self.mg.insert_logs(args.log)
        # res = self.wait(self.mg.insert_logs(log))
        print(res)
        self.success()
