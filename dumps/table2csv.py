import csv
import os
import re
import string

from lxml import etree
from bs4 import BeautifulSoup

def convert(table, title, output_dir):
    name = "".join(x for x in title if x.isalnum())
    print name
    path = open(os.path.join(output_dir, name + '.txt'), 'w')
    table = etree.tostring(table)
    print >>path, table
    csv_file = csv.writer(
        open(os.path.join(output_dir, 'csv', name + '.csv'), 'w'))
    soup = BeautifulSoup(table)
    for row in soup.find_all('tr'):
        row = map(
            lambda t: re.sub('\s+',
                             ' ',
                             " ".join(t.stripped_strings)).encode('utf-8'),
            row.find_all(re.compile('t[dh]')))
        csv_file.writerow(row)

