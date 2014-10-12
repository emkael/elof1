#!/usr/bin/env python

from sys import argv
import urlparse, urllib, urllib2
import json, pprint
from lxml import html, etree
import os, string

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
        name = "".join(x for x in title if x.isalnum()) + '-' + str(i) + '.txt'
        print name
        path = open('second-a-lap/' + name, 'w')
        print >>path, etree.tostring(table)
        i += 1

if __name__ == "__main__":
    if len(argv) > 1:
        url = urlparse.urlparse(argv[1])
        fetch(url.path)
