import logging, sys
def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        h = logging.StreamHandler(sys.stdout)
        h.setFormatter(logging.Formatter("%(asctime)s | %(name)-15s | %(levelname)-7s | %(message)s"))
        logger.addHandler(h)
        logger.setLevel(logging.INFO)
    return logger
