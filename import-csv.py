import csv
import sys

from f1elo.db import Session
from f1elo.model import find_driver
from f1elo.model import *

session = Session()

with open(sys.argv[1]) as f:
    reader = csv.reader(f)
    for row in reader:
        driver = None
        if len(row) == 6:
            entry = Entry()
            entry._race = row[0]
            entry.result = row[1]
            entry.car_no = row[2]
            entry.result_group = row[5]
            session.add(entry)
            driver = find_driver(row[4].strip(), row[3].strip(), session)
            entry.drivers.append(driver)
        elif len(row) == 2:
            driver = find_driver(row[1].strip(), row[0].strip(), session)
            entry.drivers.append(driver)
        else:
            print row

session.commit()
