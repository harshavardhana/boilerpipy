# -*- coding: utf-8 -*-
import re

from collections import defaultdict

from lxml.etree import tostring, tounicode, ParserError, iterwalk
from lxml.html.clean import Cleaner
import lxml.html as html

from .expressions import *
from .common import *
from .error import *
from .compat import *

import logging
FORMAT = '%(asctime)-15s %(message)s'
logging.basicConfig(format=FORMAT, datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger('extractor')
# Default
logger.setLevel(logging.INFO)
__version__ = "0.2.1beta"
__license__ = "Apache 2.0"

def setLogLevel(level):
    if not isinstance(level, int):
        raise ValueError
    logger.setLevel(level)

class Extractor:
    def __init__(self, input, notify=None, tag=None, **options):
        self.input = input.replace('\r','')
        self.options = defaultdict(lambda: None)
        for k, v in list(options.items()):
            self.options[k] = v
        self.notify = notify or logger.debug
        self.html = None
        self.TEXT_LENGTH_THRESHOLD = 25
        self.RETRY_LENGTH = 250
        setLogLevel(self.options.get('loglevel'))
        self.tag = tag

    def normalize_html(self, force=False):
        # Use lxml 'Cleaner' class to normalize html to a feasible value
        if force or self.html is None:
            cleaner = Cleaner(scripts=True, javascript=True, comments=True,
                              style=True, links=True, meta=False, add_nofollow=False,
                              page_structure=False, processing_instructions=True, embedded=False,
                              frames=False, forms=False, annoying_tags=False, remove_tags=None,
                              remove_unknown_tags=False, safe_attrs_only=False)
            if isinstance(self.input, compat_str):
                # Work around: ValueError: Unicode strings with encoding
                # declaration are not supported by lxml
                self.input = self.input.encode('utf-8')
            self.html = parse(cleaner.clean_html(self.input), self.options['url'], notify=self.notify)
        return self.html

    def content(self):
        return get_body(self.normalize_html())

    def title(self):
        return get_title(self.normalize_html())

    def query(self):
        if self.tag is None:
            raise ValueError('Please provide tag value before calling this function')

        return get_queried_tags(self.normalize_html(), self.tag)

    def extracted(self):
        try:
            single_pass = True
            while True:
                self.normalize_html(True)
                [i.drop_tree() for i in self.tags(self.html, 'script', 'style', 'noscript')]

                if single_pass:
                    self.remove_unlikely_nodes()

                self.transform_misused_divs_into_paragraphs()
                nodes = self.score_paragraphs(self.options.get('min_text_length', self.TEXT_LENGTH_THRESHOLD))

                best_node = self.select_best_node(nodes)
                if best_node:
                    article = self.get_article(nodes, best_node)
                else:
                    if single_pass:
                        single_pass = False
                        logger.info("Ended up stripping too much - going for a safer parsing scheme")
                        # try again
                        continue
                    else:
                        logger.info("Ruthless and simple parsing did not work. Returning unprocessed raw html")
                        if self.html.find('body') is not None:
                            article = self.html.find('body')
                        else:
                            article = self.html

                content_scores = []

                for x in nodes:
                    if nodes[x]['content_score'] < 0:
                        continue
                    content_scores.append(nodes[x]['content_score'])

                cleaned_article = self.sanitize(article, nodes)
                at_acceptable_length = len(cleaned_article) >= self.RETRY_LENGTH

                if single_pass and not at_acceptable_length:
                    single_pass = False
                    continue # try again
                else:
                    return cleaned_article
        except (Exception, ParserError) as e:
            logger.info('error getting summary: %s' % e)
            return None

        except lxml.etree.XMLSyntaxError:
            logger.info('error getting summary: %s' % e)
            return None

    def get_article(self, nodes, best_node):
        # Now that we have the top node, look through its siblings for content that might also be related.
        # Things like preambles, content split by ads that we removed, etc.

        sibling_score_threshold = max([10, best_node['content_score'] * 0.2])
        output = parse("<div/>")
        for sibling in best_node['elem'].getparent().getchildren():
            append = False
            if sibling is best_node['elem']:
                append = True
            sibling_key = sibling
            if sibling_key in nodes and nodes[sibling_key]['content_score'] >= sibling_score_threshold:
                append = True

            if sibling.tag == "p":
                link_density = self.get_link_density(sibling)
                node_content = sibling.text or ""
                node_length = len(node_content)

                if node_length > 80 and link_density < 0.25:
                    append = True
                elif node_length < 80 and link_density == 0 and re.search(r'\.( |$)', node_content):
                    append = True

            if append:
                output.append(sibling)
        if output is not None: output.append(best_node['elem'])
        return output

    def select_best_node(self, nodes):
        sorted_nodes = sorted(list(nodes.values()), key=lambda x: x['content_score'], reverse=True)
        logger.debug("Top 5 nodes:")
        for node in sorted_nodes[:5]:
            elem = node['elem']
            logger.debug("Node %s with score %s '%s...'" % (describe(elem), node['content_score'], snippet(elem)))

        if len(sorted_nodes) == 0:
            return None
        best_node = sorted_nodes[0]
        logger.debug("Best node %s with score %s" % (describe(best_node['elem']), best_node['content_score']))
        return best_node

    def get_link_density(self, elem):
        link_length = len("".join([i.text_content() or "" for i in elem.findall(".//a")]))
        text_length = len(elem.text_content())
        return float(link_length) / max(text_length, 1)

    def score_paragraphs(self, min_text_length):
        nodes = {}
        logger.debug(str([describe(node) for node in self.tags(self.html, "div")]))
        elems = self.tags(self.html, "div", "p", "td", 'li', "a")

        for elem in elems:
            parent_node = elem.getparent()
            grand_parent_node = parent_node.getparent()
            elem_key = elem
            parent_key = parent_node
            grand_parent_key = grand_parent_node

            inner_text = elem.text_content()

            # If this paragraph is less than 25 characters, don't even count it.
            if (not inner_text) or len(inner_text) < min_text_length:
                continue

            if parent_key not in nodes:
                nodes[parent_key] = self.score_node(parent_node)
            if grand_parent_node is not None and grand_parent_key not in nodes:
                nodes[grand_parent_key] = self.score_node(grand_parent_node)

            content_score = 1
            content_score += len(inner_text.split(','))
            content_score += min([(len(inner_text) / 100), 3])
            if elem not in nodes:
                nodes[elem_key] = self.score_node(elem)
            nodes[elem_key]['content_score'] += content_score
            nodes[parent_key]['content_score'] += content_score
            if grand_parent_node is not None:
                nodes[grand_parent_key]['content_score'] += content_score / 2.0

        # Scale the final nodes score based on link density. Good content should have a
        # relatively small link density (5% or less) and be mostly unaffected by this operation.
        for elem, node in list(nodes.items()):
            link_density = self.get_link_density(elem)
            node['content_score'] *= (1 - link_density)
            if node['content_score'] > 0:
                logger.debug("node %s scored %s (linkd: %s) '%s'" % (describe(elem),
                                                                        node['content_score'],
                                                                        link_density,
                                                                        snippet(elem,30)))

        return nodes

    def class_weight(self, e):
        weight = 0
        if e.get('class', None):
            if REGEXPS.get('negative').search(e.get('class')):
                weight -= 25

            if REGEXPS.get('positive').search(e.get('class')):
                weight += 25

        if e.get('id', None):
            if REGEXPS.get('negative').search(e.get('id')):
                weight -= 25

            if REGEXPS.get('positive').search(e.get('id')):
                weight += 25

        return weight

    def score_node(self, elem):
        content_score = self.class_weight(elem)
        tag = elem.tag.lower()
        if tag == "div":
            content_score += 5
        elif tag == "blockquote":
            content_score += 3
        elif tag == "form":
            content_score -= 3
        elif tag == "th":
            content_score -= 5
        return { 'content_score': content_score, 'elem': elem }

    def remove_unlikely_nodes(self):
        remove_list = []
        context = iterwalk(self.html)
        for action, elem in context:
            s = "%s%s" % (elem.get('class', ''), elem.get('id', ''))
            if REGEXPS['unlikelyNodes'].search(s) and (not REGEXPS['okMaybeItsANode'].search(s)) and elem.tag != 'body':
                logger.debug("Removing unlikely node - %s" % (s,))
                remove_list.append(elem)
        [e.drop_tree() for e in remove_list if e.tag != 'html']

    def transform_misused_divs_into_paragraphs(self):
        for elem in self.html.iter():
            if elem.tag.lower() == "div":
                # transform <div>s that do not contain other block elements into <p>s
                if not REGEXPS['divToPElements'].search(compat_str(''.join(map(tostring, list(elem))))):
                    logger.debug("Altering div(#%s.%s) to p" % (elem.get('id', ''), elem.get('class', '')))
                    elem.tag = "p"

    def tags(self, node, *tag_names):
        for tag_name in tag_names:
            for e in node.findall('.//%s' %tag_name):
                yield e

    def sanitize(self, node, nodes):
        for header in self.tags(node, "h1", "h2", "h3", "h4", "h5", "h6"):
            if self.class_weight(header) < 0 or self.get_link_density(header) > 0.33: header.drop_tree()

        for elem in self.tags(node, "form"):
            elem.drop_tree()
        allowed = {}
        # Conditionally clean <table>s, <ul>s, and <div>s
        for el in self.tags(node, "table", "ul", "div"):
            if el in allowed:
                continue
            weight = self.class_weight(el)
            el_key = el
            if el_key in nodes:
                content_score = nodes[el_key]['content_score']
            else:
                content_score = 0

            tag = el.tag
            if weight + content_score < 0:
                el.drop_tree()
                logger.debug("Conditionally cleaned %s with weight %s and content score %s because score + content score was less than zero." %
                    (describe(el), weight, content_score))
            elif len(el.text_content().split(",")) < 10:
                counts = {}
                for kind in ['p', 'img', 'li', 'a', 'embed', 'input', 'iframe']:
                    counts[kind] = len(el.findall('.//%s' % kind))
                counts["li"] -= 100

                content_length = len(el.text_content()) # Count the text length excluding any surrounding whitespace
                link_density = self.get_link_density(el)
                parent_node = el.getparent()
                if parent_node is not None:
                    if parent_node in nodes:
                        content_score = nodes[parent_node]['content_score']
                    else:
                        content_score = 0
                    pweight = self.class_weight(parent_node) + content_score
                    pname = parent_node.tag
                else:
                    pweight = 0
                    pname = "no parent"
                to_remove = False
                reason = ""

                if counts["p"] and counts["img"] > counts["p"]:
                    reason = "too many images"
                    to_remove = True
                elif counts["li"] > counts["p"] and tag != "ul" and tag != "ol":
                    reason = "more <li>s than <p>s"
                    to_remove = True
                elif counts["input"] > (counts["p"] / 3):
                    reason = "less than 3x <p>s than <input>s"
                    to_remove = True
                elif content_length < (self.options.get('min_text_length', self.TEXT_LENGTH_THRESHOLD)) and (counts["img"] == 0):
                    reason = "too short a content length without a single image"
                    to_remove = True
                elif weight < 25 and link_density > 0.2:
                    reason = "too many links for its weight less than 25 (#{weight})"
                    to_remove = True
                elif weight >= 25 and link_density > 0.5:
                    reason = "too many links for its weight (#{weight})"
                    to_remove = True
                elif el.tag.lower() == "embed":
                    if not REGEXPS.get('videos').search(el.get('src')):
                        to_remove = True
                elif el.tag.lower() == "iframe":
                    if not REGEXPS.get('videos').search(el.get('src')):
                        to_remove = True
                elif (counts["embed"] == 1 and content_length < 75) or counts["embed"] > 2:
                    reason = "<embed>s with too short a content length, or too many <embed>s"
                    to_remove = True
                elif (counts["iframe"] == 1 and content_length < 75) or counts["iframe"] > 2:
                    reason = "<iframe>s with too short a content length, or too many <iframe>s"
                    to_remove = True
                if to_remove:
                    logger.debug("Conditionally cleaned %s#%s.%s with weight %s and content score %s because it has %s." %
                               (el.tag, el.get('id',''), el.get('class', ''), weight, content_score, reason))
                    logger.debug("pname %s pweight %s" %(pname, pweight))
                    el.drop_tree()
        return tounicode(node)
