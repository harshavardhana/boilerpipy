# -*- coding: utf-8 -*-
import logging
FORMAT = '%(asctime)-15s %(message)s'
logging.basicConfig(format=FORMAT, datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger('extractor')

class Logger(logging.Logger):
    """ """
    def __init__(self, level):
        self.loglevel = level
 
    @staticmethod
    def log(message, sender="extractor", level="info"):
        if not hasattr(logger, level):
            raise Exception('invalid log level')
        getattr(logger, level)("%s: %s", sender, message)
