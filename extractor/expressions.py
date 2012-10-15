# -*- coding: utf-8 -*-
###  LIST of all the regexes supported by readability

import re

REGEXPS = {
    'unlikelyCandidates': re.compile('ad_wrapper|adwrapper|combx|comment|community|disqus|extra|foot|header|menu|remark|rss|shoutbox|sidebar|sponsor|ad-break|agegate|pagination|pager|popup|tweet|twitter|facebook|pinterest', re.I),
    'okMaybeItsACandidate': re.compile('and|article|body|column|main|shadow', re.I),
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

class Replacement(object):
    def __init__(self, desc, regex, replacement):
        self.desc = desc
        self.regex = regex
        self.replacement = replacement

    def apply(self, content):
        return self.regex.sub(self.replacement, content)

lousy_regexes = (
    Replacement('javascript',
                regex=re.compile('<script.*?</script[^>]*>', re.DOTALL | re.IGNORECASE),
                replacement=''),

    Replacement('double double-quoted attributes',
                regex=re.compile('(="[^"]+")"+'),
                replacement='\\1'),

    Replacement('unclosed tags',
                regex = re.compile('(<[a-zA-Z]+[^>]*)(<[a-zA-Z]+[^<>]*>)'),
                replacement='\\1>\\2'),

    Replacement('unclosed (numerical) attribute values',
                regex = re.compile('(<[^>]*[a-zA-Z]+\s*=\s*"[0-9]+)( [a-zA-Z]+="\w+"|/?>)'),
                replacement='\\1"\\2'),
    )

# strip out a set of nuisance html attributes that can mess up rendering in RSS feeds
bad_attrs = ['width','height','style','[-a-z]*color','background[-a-z]*']
single_quoted = "'[^']+'"
double_quoted = '"[^"]+"'
non_space = '[^ "\'>]+'
htmlstrip = re.compile("<" # open
                       "([^>]+) " # prefix
                       "(?:%s) *" % ('|'.join(bad_attrs),) + # undesirable attributes
                       '= *(?:%s|%s|%s)' % (non_space, single_quoted, double_quoted) + # value
                       "([^>]*)"  # postfix
                       ">"        # end
                       , re.I)
