# coding:utf-8
"""Convert YAML to Python Data."""
import sys
import os
import json
import yaml
from tornado.log import app_log

from lib.arguments import Arguments

_ENV = os.getenv('ENV', "dev")
print(f"current ENV：{_ENV}")
app_log.info(f"current ENV：{_ENV}")
if not _ENV:
    raise EnvironmentError("ENV is not available！")
_PROJECT = os.getenv('PROJECTNAME', 'Event-Tracker')
CFG = None
config_file = "config/config.yaml"

commen_config = dict(
    application=dict(
        template_path='templates',
        static_path='files',
        cookie_secret='hqnXBfcqxGoTBXGwm6+JihCDCZp8V+S0zierfVT8kdw=',
        autoreload=False,
        serve_traceback=False,  # Whether return traceback info to client
        debug=True,
    ),
    httpserver=dict(xheaders=True))

class Config(Arguments):
    def __init__(self, params):
        super().__init__(self.convert(params))

    def traverse(self, pre=''):
        new_dict = dict()
        for key in self:
            if isinstance(self[key], dict):
                new_dict.update(
                    self.__getattr__(key).traverse(pre + key + '.'))
            else:
                new_dict[pre + key] = self[key]
        return new_dict

    def convert(self, params):
        new_dict = dict()
        for key in params:
            if isinstance(params[key], dict):
                if _ENV in params[key]:
                    new_dict[key] = params[key][_ENV]
                else:
                    new_dict[key] = self.convert(params[key])
            else:
                new_dict[key] = params[key]
        return new_dict

    def show(self):
        sys.stdout.write('\nconfig:\n')
        json.dump(self.traverse(), sys.stdout, indent=4, sort_keys=True)
        sys.stdout.write('\n\n\n')
        sys.stdout.flush()


try:
    with open(config_file, 'r', encoding='utf-8') as config:
        conf = yaml.load(config, Loader=yaml.FullLoader)
        conf.update(commen_config)
        CFG = Config(conf)
except FileNotFoundError:
    raise FileNotFoundError(f'Config File "{config_file}" Not Found.')
