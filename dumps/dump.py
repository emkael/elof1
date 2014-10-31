#!/usr/bin/env python

from sys import argv
from compile import compile
from table2csv import convert

if __name__ == "__main__":
    if len(argv) > 1:
        if argv[1] == 'compile':
            compile(argv[2:])
        elif len(argv) > 2:
            if argv[1] == 'fetch':
                argv.remove('fetch')
            fetch = __import__('_sites.' + argv[1], globals(), locals(), ['fetch'])
            for url in argv[2:]:
                title, tables = fetch.fetch(url)
                i = 1
                for table in tables:
                    convert(table, title + '-' + str(i), argv[1])
                    i += 1
