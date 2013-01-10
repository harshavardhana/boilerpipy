import sys

try:
    import urllib.request as compat_urllib_request
except ImportError: # Python 2
    import urllib2 as compat_urllib_request

try:
    import urllib.error as compat_urllib_error
except ImportError: # Python 2
    import urllib2 as compat_urllib_error

try:
    import urllib.parse as compat_urllib_parse
except ImportError: # Python 2
    import urllib as compat_urllib_parse

try:
    from urllib.parse import urlparse as compat_urllib_parse_urlparse
except ImportError: # Python 2
    from urlparse2 import urlparse as compat_urllib_parse_urlparse

try:
    import html.parser as compat_html_parser
except ImportError: # Python 2
    import HTMLParser as compat_html_parser

try:
    import http.client as compat_http_client
except ImportError: # Python 2
    import httplib as compat_http_client

try:
    compat_str = unicode # Python 2
except NameError:
    compat_str = str

try:
    compat_chr = unichr # Python 2
except NameError:
    compat_chr = chr

def preferredencoding():
    """Get preferred encoding.

    Returns the best encoding scheme for the system, based on
    locale.getpreferredencoding() and some further tweaks.
    """
    try:
        pref = locale.getpreferredencoding()
        u'TEST'.encode(pref)
    except:
        pref = 'UTF-8'
    return pref

if sys.version_info < (3,0):
    def compat_print(s):
        print(s.encode(preferredencoding(), 'xmlcharrefreplace'))
else:
    def compat_print(s):
        assert isinstance(s, unicode)
        print(s)
