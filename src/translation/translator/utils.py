import logging
import os
from datetime import datetime
import sys


class LOGGER:
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    INFO = logging.INFO
    CRITICAL = logging.CRITICAL
    DEBUG = logging.DEBUG
    NOTSET = logging.NOTSET

    LOG_FORMAT = '%(levelname)s %(asctime)s - %(message)s'

    def __init__(self, name, path="logs", logLevel=INFO):
        if not os.path.exists(path):
            os.makedirs(path)

        self.logger = logging.getLogger(name)
        self.logger.setLevel(logLevel)

        # File handler for logging to a file
        fileHandler = logging.FileHandler(f'{path}/{name}_{datetime.today().strftime("%Y-%m-%d-%H%M%S")}.txt', 'a',
                                          'utf-8')
        fileHandler.setFormatter(logging.Formatter(self.LOG_FORMAT))
        self.logger.addHandler(fileHandler)

        # Console handler for logging to stdout
        self.consoleHandler = logging.StreamHandler(sys.stdout)
        self.consoleHandler.setFormatter(logging.Formatter(self.LOG_FORMAT))
        self.logger.addHandler(self.consoleHandler)

    def debug(self, msg):
        self.logger.debug(msg)

    def info(self, msg):
        self.logger.info(msg)

    def warning(self, msg):
        self.logger.warning(msg)

    def error(self, msg):
        self.logger.error(msg)

    def critical(self, msg):
        self.logger.critical(msg)

    def setLevel(self, level):
        self.logger.setLevel(level)

    def enable_stdout(self):
        if self.consoleHandler not in self.logger.handlers:
            self.logger.addHandler(self.consoleHandler)

    def disable_stdout(self):
        if self.consoleHandler in self.logger.handlers:
            self.logger.removeHandler(self.consoleHandler)