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
