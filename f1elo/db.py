import json
from os import path

import __main__
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

config = json.load(open(path.join(path.dirname(__main__.__file__), 'config', 'db.json')))
if config['engine'] == 'mysql':
    engine = create_engine("mysql://{0[user]}:{0[pass]}@{0[host]}/{0[db]}?charset=utf8".format(config))
else:
    engine = create_engine("sqlite:///{0[file]}".format(config))

Session = sessionmaker(bind=engine)
