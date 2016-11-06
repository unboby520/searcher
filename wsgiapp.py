#coding:utf8
"""
Created on Jun 18, 2014

@author: ilcwd
"""
import logging.config
import logging
import os

import yaml

from searcher.core import application, misc
_parent = os.path.join(os.path.dirname(__file__), 'deployment')
logging_config_path = os.path.join(_parent, 'logging.yaml')
app_config_path = os.path.join(_parent, 'config.json')

# register APIs after `C.load_config()`
from searcher.views import default
from searcher.apis import searcher
from searcher.apis import searcher_admin

application.register_blueprint(searcher.app, url_prefix='/searcher')
application.register_blueprint(searcher_admin.app, url_prefix='/searcher_admin')

if __name__ != '__main__':
    with open(logging_config_path, 'r') as f:
        logging.config.dictConfig(yaml.load(f))

def main():
    """Debug Mode"""
    import sys
    _logger = logging.getLogger()
    _logger.setLevel(logging.DEBUG)
    _logger.addHandler(logging.StreamHandler(stream=sys.stdout))

    host, port = '0.0.0.0', 8080
    application.run(host, port, debug=True, use_reloader=False)


if __name__ == '__main__':
    main()
