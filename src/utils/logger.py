import logging
import os
import sys

log_level = os.getenv('LOGGING_LEVEL')


class ColorFormatter(logging.Formatter):
    """Logging colored formatter
       adapted from https://stackoverflow.com/a/56944256/3638629
    """

    grey = '\x1b[38;21m'
    blue = '\x1b[38;5;39m'
    yellow = '\x1b[38;5;226m'
    red = '\x1b[38;5;196m'
    bold_red = '\x1b[31;1m'
    reset = '\x1b[0m'

    def __init__(self, fmt):
        super().__init__()
        self.fmt = fmt
        self.FORMATS = {
            logging.DEBUG: self.grey + self.fmt + self.reset,
            logging.INFO: self.blue + self.fmt + self.reset,
            logging.WARNING: self.yellow + self.fmt + self.reset,
            logging.ERROR: self.red + self.fmt + self.reset,
            logging.CRITICAL: self.bold_red + self.fmt + self.reset
        }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


level = logging.getLevelName(log_level)

root = logging.getLogger()
root.setLevel(level)

handler = logging.StreamHandler(sys.stdout)
handler.setLevel(level)

formatter = ('%(asctime)s:%(levelname)s:%(name)s: %(message)s')

handler.setFormatter(ColorFormatter(formatter))
root.addHandler(handler)
logger = root
