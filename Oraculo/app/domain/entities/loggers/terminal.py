import logging
import os


LOG_LEVEL = os.getenv("LOG_LEVEL", "DEBUG").upper()
if hasattr(logging, LOG_LEVEL):
    logging.basicConfig(level=getattr(logging, LOG_LEVEL))
else:
    logging.basicConfig(level=logging.DEBUG)
    


class ColoredFormatter(logging.Formatter):
    FORMATS = {
        logging.INFO: "\033[92m[%(levelname)s] - %(asctime)s - %(name)s - %(message)s\033[0m",      # GREEN
        logging.WARNING: "\033[93m[%(levelname)s] - %(asctime)s - %(name)s - %(message)s\033[0m",   # YELLOW
        logging.ERROR: "\033[91m[%(levelname)s] - %(asctime)s - %(name)s - %(message)s\033[0m",     # RED
        logging.DEBUG: "\033[33m[%(levelname)s] - %(asctime)s - %(name)s - %(message)s\033[0m",     # BROWN
    }

    def format(self, record):
        fmt = self.FORMATS.get(record.levelno, "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        formatter = logging.Formatter(fmt)
        return formatter.format(record)


def apply_colored_formatter():
    """Apply colored formatter to all handlers of the root logger."""
    for handler in logging.getLogger().handlers:
        handler.setFormatter(ColoredFormatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))