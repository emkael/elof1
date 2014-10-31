import json
import urllib
import urllib2
import urlparse

from lxml import html

def fetch(url):
    url = urlparse.urlparse(url).path
    contents = json.loads(urllib2.urlopen('http://second-a-lap.blogspot.com/feeds/posts/default?' +
                          urllib.urlencode({'alt': 'json', 'v': 2, 'dynamicviews': 1, 'path': url})).read())
    title = contents['feed']['entry'][0]['title']['$t']
    text = contents['feed']['entry'][0]['content']['$t']
    tree = html.fromstring(text)
    tables = tree.xpath("//table[@bordercolor]")
    print url
    print title
    return title, tables
