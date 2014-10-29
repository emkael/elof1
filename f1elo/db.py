import json
from os import path

import __main__
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

config = json.load(open(path.join(path.dirname(__main__.__file__), 'config', 'db.json')))
if config['engine'] == 'mysql':
    engine = create_engine("mysql://{0[user]}:{0[pass]}@{0[host]}/{0[db]}?charset=utf8".format(config))
elif config['engine'] == 'sqlite':
    engine = create_engine("sqlite:///{0[file]}".format(config))
    def fk_pragma(conn, record):
        conn.execute('PRAGMA FOREIGN_KEYS=ON');
    event.listen(engine, 'connect', fk_pragma)

Session = sessionmaker(bind=engine)
