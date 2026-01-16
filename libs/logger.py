import logging


class Logger(logging.Formatter):
    formats = {
        logging.DEBUG: "\x1b[1;90m%(asctime)s\x1b[0m \x1b[1;7;34m %(levelname)s \x1b[0m \t\x1b[1;4;34m(%(filename)s)\x1b[0m %(message)s",
        logging.INFO: "\x1b[1;90m%(asctime)s\x1b[0m \x1b[1;7;32m %(levelname)s \x1b[0m \t\x1b[1;4;34m(%(filename)s)\x1b[0m %(message)s",
        logging.WARNING: "\x1b[1;90m%(asctime)s\x1b[0m \x1b[1;7;33m %(levelname)s \x1b[0m \t\x1b[1;4;34m(%(filename)s)\x1b[0m %(message)s",
        logging.ERROR: "\x1b[1;90m%(asctime)s\x1b[0m \x1b[1;7;31m %(levelname)s \x1b[0m \t\x1b[1;4;34m(%(filename)s)\x1b[0m \x1b[1;31m%(message)s\x1b[0m",
        logging.CRITICAL: "\x1b[1;90m%(asctime)s\x1b[0m \x1b[1;5;41;30m %(levelname)s \x1b[0m \t\x1b[1;4;34m(%(filename)s)\x1b[0m \x1b[1;4;31m%(message)s\x1b[0m",
    }

    def format(self, record):
        log_fmt = self.formats.get(record.levelno, "%(message)s")
        formatter = logging.Formatter(log_fmt, datefmt="%Y-%m-%d %H:%M:%S")
        return formatter.format(record)


logger = logging.getLogger("ROAR-WAF")
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setFormatter(Logger())
logger.addHandler(handler)
