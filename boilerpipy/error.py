# -*- coding: utf-8 -*-
from lxml.etree import ParseError

class Unparseable(Exception):
    """
    Local exception handler
    """
    def __init__(self, error):
        # pylint fixes
        super(Unparseable, self).__init__(error)

        if isinstance(error, type(ValueError)):
            pass
        if isinstance(error, type(ParseError)):
            pass
        if isinstance(error, type(AttributeError)):
            pass
        if isinstance(error, type(UnicodeError)):
            pass
        if isinstance(error, type(SyntaxError)):
            pass
        # Control shouldn't reach here
