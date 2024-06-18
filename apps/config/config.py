# coding:utf-8
"""Convert YAML to Python Data."""
import sys
import os
import json
import yaml
from tornado.log import app_log


_ENV = os.getenv('ENV')
print(f"current ENV：{_ENV}")
app_log.info(f"current ENV：{_ENV}")
if not _ENV:
    #_ENV = 'local'
    raise EnvironmentError("ENV is not available！")
_PROJECT = os.getenv('PROJECTNAME', 'emdb-server')
cfg = None
config_file = "./apps/config/config.yaml"

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


class Arguments(dict):
    """Class to manage arguments of a requests."""

    def __init__(self, params):
        if isinstance(params, dict):
            super().__init__(params)
        elif not params:
            super().__init__(dict())
        else:
            raise TypeError(
                f"Arguments data should be a 'dict' not {type(params)}.")

    def __getattr__(self, name):
        attr = self.get(name)
        if isinstance(attr, dict):
            attr = self.__class__(attr)
        return attr

    def __setattr__(self, name, value):
        raise PermissionError('Can not set attribute to <class Arguments>.')

    def insert(self, key, value):
        """Add a variable to args."""
        if key in self:
            raise PermissionError(f'Key {key} is already exists.')
        else:
            self[key] = value

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
        cfg = Config(conf)
except FileNotFoundError:
    raise FileNotFoundError(f'Config File "{config_file}" Not Found.')
