# -*- coding: utf-8 -*-
###  LIST of all the regexes supported by readability

import re

## Regex stolen from Arc90's readability.js
REGEXPS = {
    'unlikelyNodes': re.compile(r'ad_wrapper|adwrapper|combx|comment|community|disqus|extra|foot|header|menu|remark|rss|shoutbox|sidebar|sponsor|ad-break|agegate|pagination|pager|popup|tweet|twitter|facebook|pinterest', re.I),
    'okMaybeItsANode': re.compile(r'and|article|body|column|main|shadow', re.I),
    'positive': re.compile(r'article|body|content|entry|hentry|main|page|pagination|post|text|blog|story', re.I),
    'negative': re.compile(r'ad_wrapper|adwrapper|combx|comment|com-|contact|foot|footer|footnote|masthead|media|meta|outbrain|promo|related|scroll|shoutbox|sidebar|sponsor|shopping|tags|tool|widget|share|icon', re.I),
    'extraneous': re.compile(r'print|archive|comment|discuss|e[\-]?email|share|reply|all|login|sign|single', re.I),
    'divToPElements': re.compile(r'<(a|blockquote|dl|div|img|ol|p|pre|table|ul)', re.I),
    'replaceBrs': re.compile(r'(<br[^>]*>[ \n\r\t]*){2,}', re.I),
    'replaceFonts': re.compile(r'<(\/?)font[^>]*>', re.I),
    'trim': re.compile(r'^\s+|\s+$/'),
    'normalize': re.compile(r'\s{2,}/'),
    'killBreaks': re.compile(r'(<br\s*\/?>(\s|&nbsp;?)*){1,}/'),
    'videos': re.compile(r'http:\/\/(www\.)?(youtube|vimeo)\.com', re.I),
    'skipFootnoteLink': re.compile(r'^\s*(\[?[a-z0-9]{1,2}\]?|^|edit|citation needed)\s*$', re.I),
}

# Strip out HTML attributes - from Arc90's readability.js
BADATTRS = ['width', 'height', 'style', '[-a-z]*color', 'background[-a-z]*']
SINGLEQUOTED = "'[^']+'"
DOUBLEQUOTED = '"[^"]+"'
NONSPACE = '[^ "\'>]+'
HTMLSTRIP = re.compile("<" # Open tag
                       "([^>]+) " # starting prefix
                       "(?:%s) *" % ('|'.join(BADATTRS),) + # remove bad attributes
                       '= *(?:%s|%s|%s)' % (NONSPACE, SINGLEQUOTED, DOUBLEQUOTED) + # needed value
                       "([^>]*)"  # starting postfix
                       ">"        # end of tag
                       , re.I)

class Regexps:
    """
    Class to remove HTML cruft
    """
    def __init__(self, desc, regex, processexps):
        self.desc = desc
        self.regex = regex
        self.processexps = processexps

    def sub(self, content):
        """
        Substitute regex expressions
        """
        return self.regex.sub(self.processexps, content)

### Cruft in html from Arc90's readability.js
CRUFTY_REGEXPS_HTML = (
    Regexps('javascript',
            regex=re.compile(r'<script.*?</script[^>]*>', re.DOTALL | re.IGNORECASE),
            processexps=''),

    Regexps('double double-quoted attributes',
            regex=re.compile(r'(="[^"]+")"+'),
            processexps='\\1'),

    Regexps('unclosed tags',
            regex = re.compile(r'(<[a-zA-Z]+[^>]*)(<[a-zA-Z]+[^<>]*>)'),
            processexps='\\1>\\2'),

    Regexps('unclosed (numerical) attribute values',
            regex = re.compile(r'(<[^>]*[a-zA-Z]+\s*=\s*"[0-9]+)( [a-zA-Z]+="\w+"|/?>)'),
            processexps='\\1"\\2'),
    )
