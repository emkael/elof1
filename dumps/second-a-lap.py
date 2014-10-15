#!/usr/bin/env python

import csv
import json
import os
import pprint
import re
import string
import urllib
import urllib2
import urlparse
from sys import argv

from lxml import etree, html

from bs4 import BeautifulSoup


def fetch(url):
    print url
    contents = json.loads(urllib2.urlopen('http://second-a-lap.blogspot.com/feeds/posts/default?'+urllib.urlencode({ 'alt': 'json', 'v': 2, 'dynamicviews': 1, 'path': url })).read())
    title = contents['feed']['entry'][0]['title']['$t']
    print title
    text = contents['feed']['entry'][0]['content']['$t']
    tree = html.fromstring(text)
    tables = tree.xpath("//table[@bordercolor]")
    i = 1
    for table in tables:
        name = "".join(x for x in title if x.isalnum()) + '-' + str(i)
        print name
        path = open(os.path.join('second-a-lap', name + '.txt'), 'w')
        table = etree.tostring(table)
        print >>path, table
        csv_file = csv.writer(open(os.path.join('second-a-lap', 'csv', name + '.csv'), 'w'))
        soup = BeautifulSoup(table)
        for row in soup.find_all('tr'):
            row = map(lambda t: re.sub('\s+', ' ', " ".join(t.stripped_strings)).encode('utf-8'), row.find_all(re.compile('t[dh]')))
            csv_file.writerow(row)
        i += 1

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
                writer.writerow([race_id,path,'','',''])
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

if __name__ == "__main__":
    if len(argv) > 1:
        if argv[1] == 'fetch' and len(argv) > 2:
            for url in argv[2:]:
                fetch(urlparse.urlparse(url).path)
        elif argv[1] == 'compile':
            compile(argv[2:])
        else:
            fetch(urlparse.urlparse(argv[1]).path)
