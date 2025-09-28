import logging
import sys

def setup_logger():
    logging.basicConfig(
        level=logging.INFO,
        format='[%(levelname)s] %(message)s',
        stream=sys.stdout
    )