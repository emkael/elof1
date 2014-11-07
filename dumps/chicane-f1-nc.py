#!/usr/bin/env python
import urllib
import urllib2
import urlparse

from lxml import html

for year in range(1954,2015):
    url = 'http://chicanef1.com/calendar.pl?' + urllib.urlencode({'year':year,'nc':1})
    contents = urllib2.urlopen(url).read()
    tree = html.fromstring(contents)
    links = tree.xpath('//table[@cellpadding=6]//tr/td[2]/center[text()="Non-championship"]/../..//td[1]//a')
    for link in links:
        url = urlparse.urlparse(link.attrib['href'])
        url = url._replace(path='race.pl')
        query = dict(urlparse.parse_qsl(url.query))
        for type in ['h1q', 'heat1', 'heat2', 'agg', 'final', 'qual', 'res']:
            query['type'] = type
            url = url._replace(query=urllib.urlencode(query))
            print urlparse.urljoin('http://chicanef1.com', urlparse.urlunparse(url))
