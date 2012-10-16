# -*- coding: utf-8 -*-
import sys
import HTMLParser

from lxml.etree import tostring, tounicode, ParserError, iterwalk
from lxml.html.clean import Cleaner
import lxml.html as html
from lxml.etree import tostring
from urlparse2 import urlparse
import httplib

from expressions import *

try:
    from bs4 import UnicodeDammit
except:
    print "Please install beautifulsoup4 --> easy_install -U beautifulsoup4"
    sys.exit(1)

def create_doc(content, base_href):
    # Work around: ValueError: Unicode strings with encoding
    # declaration are not supported by lxml
    if isinstance(content, unicode):
        content.encode('utf-8')
    html_doc = html.fromstring(content, parser=html.HTMLParser(recover=True, remove_comments=True, no_network=True))
    if base_href:
        html_doc.make_links_absolute(base_href, resolve_base_href=True)
    else:
        html_doc.resolve_base_href()
    return html_doc

# Verify if the provided HTML has 'Content-Type' as HTML
def isValidhtml(url):
    
    if url is None:
        return False

    try:
        parsed = urlparse(url)
        h = httplib.HTTPConnection(parsed.netloc)
        h.request('HEAD', parsed.path)
        response = h.getresponse()

        # Handle response status 301
        if response.status/100 == 3 and response.getheader('Location'):
            parsed = urlparse(response.getheader('Location'))
            h = httplib.HTTPConnection(parsed.netloc)
            h.request('HEAD', parsed.path)
            response = h.getresponse()
            if response.status/100 == 3:
                # Multiple re-directs throw away the HTML
                return False

        # Make sure response is not None
        if response.getheader('content-type') is None:
            return False

        # Only html if valid Header
        if response.getheader('content-type').find('text/html') != -1:
            return True

        return False
    except Exception as err:
        print("Header returned error: %s, skip not a valid HTML" % err)
        return False

# helpers for parsing
def normalize_spaces(s):
    """replace any sequence of whitespace
    characters with a single space"""
    return ' '.join(s.split())

def _remove_crufty_html(content):
    for processexps in lousy_regexps:
        content = processexps.sub(content)
    return content

def clean_attributes(html):
    while htmlstrip.search(html):
        html = htmlstrip.sub('<\\1\\2>', html)
    return html

def describe(node):
    if not hasattr(node, 'tag'):
        return "[text]"
    return "%s#%s.%s" % (
        node.tag, node.get('id', ''), node.get('class',''))

def snippet(node,n=40):
    """ return one-liner snippet of the text under the node """
    txt = node.text_content()
    txt = u' '.join(txt.split())
    if len(txt)>n:
        txt = txt[:n] + u"..."
    return txt

def parse(raw_content, base_href=None, notify=lambda *args: None):
    try:
        content = UnicodeDammit(raw_content, is_html=True).markup
        cleaned = _remove_crufty_html(content)
        return create_doc(cleaned, base_href)
    except HTMLParser.HTMLParseError, e:
        notify("parsing failed:", e)
    raise Unparseable()

def get_title(doc):
    title = unicode(getattr(doc.find('.//title'), 'text', ''))
    if not title:
        return None
    return normalize_spaces(title)

def get_body(doc):
    [ elem.drop_tree() for elem in doc.xpath('.//script | .//link | .//style') ]
    raw_html = unicode(tostring(doc.body is not None or doc is not None))
    cleaned = clean_attributes(raw_html)
    try:
        return cleaned
    except HTMLParser.HTMLParseError:
        error("cleansing broke html content: %s\n---------\n%s" % (raw_html,cleaned))
        return raw_html