#!/usr/bin/env python

import csv
import string
from sys import argv

def compile(files):
    headers = set()
    values = []
    writer = csv.writer(open('races.csv', 'w'))
    race_id = 0
    for path in files:
        try:
            with open(path, 'r') as csvfile:
                reader = csv.reader(csvfile)
                header = next(reader)
                headers = set(headers | set(header))
                for row in reader:
                    data = {}
                    i = 0
                    for cell in row:
                        data[header[i]] = cell
                        data['Race'] = race_id
                        i += 1
                    values.append(data)
                writer.writerow([race_id, path, '', '', ''])
                race_id += 1
        except IOError:
            pass
    headers.add('Race')
    writer = csv.writer(open('compiled.csv', 'w'))
    writer.writerow(list(headers))
    for row in values:
        csvrow = []
        for name in headers:
            if name in row:
                csvrow.append(row[name])
            else:
                csvrow.append('')
        writer.writerow(csvrow)

