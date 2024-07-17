import logging

def Logger(log_name):
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    # Handlers
    ch = logging.StreamHandler()
    fh = logging.FileHandler(log_name)

    # Set levels for handlers
    ch.setLevel(logging.INFO)
    fh.setLevel(logging.DEBUG)

    # Create formatter and add it to handlers
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    ch.setFormatter(formatter)
    fh.setFormatter(formatter)

    # Add handlers to the logger
    logger.addHandler(ch)
    logger.addHandler(fh)

    return logger