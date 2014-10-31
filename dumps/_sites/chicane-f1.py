import urllib
import urllib2
import urlparse

from lxml import html

def fetch(url):
    contents = urllib2.urlopen(url).read()
    tree = html.fromstring(contents)
    title = tree.xpath("//h1")[0].text + ' - ' + tree.xpath('//span[@class="subtitle"]')[0].text
    tables = tree.xpath("//table[@cellpadding=6]")
    print url
    print title
    return title, tables
