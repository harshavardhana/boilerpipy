# -*- coding: utf-8 -*-
###  LIST of all the regexes supported by readability

import re

## Regex stolen from Arc90's readability.js
REGEXPS = {
    'unlikelyNodes': re.compile('ad_wrapper|adwrapper|combx|comment|community|disqus|extra|foot|header|menu|remark|rss|shoutbox|sidebar|sponsor|ad-break|agegate|pagination|pager|popup|tweet|twitter|facebook|pinterest', re.I),
    'okMaybeItsANode': re.compile('and|article|body|column|main|shadow', re.I),
    'positive': re.compile('article|body|content|entry|hentry|main|page|pagination|post|text|blog|story', re.I),
    'negative': re.compile('ad_wrapper|adwrapper|combx|comment|com-|contact|foot|footer|footnote|masthead|media|meta|outbrain|promo|related|scroll|shoutbox|sidebar|sponsor|shopping|tags|tool|widget|share|icon', re.I),
    'extraneous': re.compile('print|archive|comment|discuss|e[\-]?email|share|reply|all|login|sign|single', re.I),
    'divToPElements': re.compile('<(a|blockquote|dl|div|img|ol|p|pre|table|ul)', re.I),
    'replaceBrs': re.compile('(<br[^>]*>[ \n\r\t]*){2,}', re.I),
    'replaceFonts': re.compile('<(\/?)font[^>]*>', re.I),
    'trim': re.compile('^\s+|\s+$/'),
    'normalize': re.compile('\s{2,}/'),
    'killBreaks': re.compile('(<br\s*\/?>(\s|&nbsp;?)*){1,}/'),
    'videos': re.compile('http:\/\/(www\.)?(youtube|vimeo)\.com', re.I),
    'skipFootnoteLink': re.compile('^\s*(\[?[a-z0-9]{1,2}\]?|^|edit|citation needed)\s*$', re.I),
}

class Regexps():
    def __init__(self, desc, regex, processexps):
        self.desc = desc
        self.regex = regex
        self.processexps = processexps

    def sub(self, content):
        return self.regex.sub(self.processexps, content)

### Cruft in html from Arc90's readability.js
crufty_regexps_html = (
    Regexps('javascript',
            regex=re.compile('<script.*?</script[^>]*>', re.DOTALL | re.IGNORECASE),
            processexps=''),

    Regexps('double double-quoted attributes',
            regex=re.compile('(="[^"]+")"+'),
            processexps='\\1'),

    Regexps('unclosed tags',
            regex = re.compile('(<[a-zA-Z]+[^>]*)(<[a-zA-Z]+[^<>]*>)'),
            processexps='\\1>\\2'),

    Regexps('unclosed (numerical) attribute values',
            regex = re.compile('(<[^>]*[a-zA-Z]+\s*=\s*"[0-9]+)( [a-zA-Z]+="\w+"|/?>)'),
            processexps='\\1"\\2'),
    )

# Strip out HTML attributes - from Arc90's readability.js
bad_attrs = ['width','height','style','[-a-z]*color','background[-a-z]*']
single_quoted = "'[^']+'"
double_quoted = '"[^"]+"'
non_space = '[^ "\'>]+'
htmlstrip = re.compile("<" # Open tag
                       "([^>]+) " # starting prefix
                       "(?:%s) *" % ('|'.join(bad_attrs),) + # remove bad attributes
                       '= *(?:%s|%s|%s)' % (non_space, single_quoted, double_quoted) + # needed value
                       "([^>]*)"  # starting postfix
                       ">"        # end of tag
                       , re.I)
