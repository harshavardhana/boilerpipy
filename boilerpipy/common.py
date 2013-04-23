# -*- coding: utf-8 -*-
import sys

from lxml.etree import tostring
import lxml.html as html

from .expressions import htmlstrip, crufty_regexps_html
from .compat import (compat_urllib_parse_urlparse,
                             compat_html_parser, compat_str,
                             compat_http_client)
from .error import Unparseable

try:
    from bs4 import UnicodeDammit
except:
    print("Please install beautifulsoup4 --> easy_install -U beautifulsoup4")
    sys.exit(1)

def create_doc(content, base_href):
    # Work around: ValueError: Unicode strings with encoding
    # declaration are not supported by lxml
    if isinstance(content, compat_str):
        content = content.encode('utf-8')
    html_doc = html.fromstring(content, parser=html.HTMLParser(recover=True, remove_comments=True, no_network=True))
    if base_href:
        html_doc.make_links_absolute(base_href, resolve_base_href=True)
    else:
        html_doc.resolve_base_href()
    return html_doc

# Verify if the provided HTML has 'Content-Type' as HTML
def isvalidhtml(url):
    """
    Verify valid HTML content
    """

    if url is None:
        return False

    try:
        parsed = compat_urllib_parse_urlparse(url)
        h = compat_http_client.HTTPConnection(parsed.netloc)
        h.request('HEAD', parsed.path)
        response = h.getresponse()

        # Handle response status 301
        if response.status/100 == 3 and response.getheader('Location'):
            parsed = compat_urllib_parse_urlparse(response.getheader('Location'))
            h = compat_http_client.HTTPConnection(parsed.netloc)
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
        print(("Header returned error: %s, skip not a valid HTML" % err))
        return False

# helpers for parsing
def normalize_spaces(s):
    """replace any sequence of whitespace
    characters with a single space"""
    return ' '.join(s.split())

def _clean_crufty_html(content):
    for regexps in crufty_regexps_html:
        content = regexps.sub(content)
    return content

def clean_attributes(raw_html):
    while htmlstrip.search(raw_html):
        raw_html = htmlstrip.sub('<\\1\\2>', raw_html)
    return raw_html

def describe(node):
    if not hasattr(node, 'tag'):
        return "[text]"
    return "%s#%s.%s" % (
        node.tag, node.get('id', ''), node.get('class',''))

def snippet(node, n=40):
    """ return one-liner snippet of the text under the node """
    txt = node.text_content()
    txt = compat_str(' '.join(txt.split()))
    if len(txt)>n:
        txt = txt[:n] + compat_str("...")
    return txt

def parse(raw_content, base_href=None, notify=lambda *args: None):
    try:
        content = UnicodeDammit(raw_content, is_html=True).markup
        cleaned = _clean_crufty_html(content)
        return create_doc(cleaned, base_href)
    except compat_html_parser.HTMLParseError as e:
        notify("parsing failed:", e)
    raise Unparseable()

def get_title(doc):
    title = compat_str(getattr(doc.find('.//title'), 'text', ''))
    if not title:
        return None
    return normalize_spaces(title)

def get_body(doc):
    [ elem.drop_tree() for elem in doc.xpath('.//script | .//link | .//style') ]

    if doc.body is not None:
        raw_html = compat_str(tostring(doc.body))
    elif doc is not None:
        raw_html = compat_str(tostring(doc))

    try:
        cleaned = clean_attributes(raw_html)
        return cleaned
    except compat_html_parser.HTMLParseError:
        print ("cleansing broke html content: %s\n---------\n%s" % (raw_html, cleaned))
        return raw_html

def get_queried_tags(doc, tag):
    [ elem.drop_tree() for elem in doc.xpath('.//script | .//link | .//style') ]

    queried_results = []
    for i in doc.findall('.//%s' % tag):
        queried_results.append(compat_str(tostring(i).strip()))

    return queried_results
