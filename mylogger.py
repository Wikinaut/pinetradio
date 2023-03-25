import logging
import sys
import time

def setup(loglevel, logfile):
    # https://stackoverflow.com/questions/13733552/logger-configuration-to-log-to-file-and-print-to-stdout
    logging.basicConfig(
        level=loglevel,
#        format="%(asctime)s %(filename)s [%(levelname)s] %(message)s",
        format="%(asctime)s %(message)s",
        datefmt='%Y%m%d-%H%M%S',
        handlers=[
            # logging.FileHandler( re.sub('.py$', '.log', sys.argv[0] ) ),
            logging.FileHandler( logfile ),
            logging.StreamHandler( sys.stdout ),
        ]
    )
#    logging.Formatter.converter = time.gmtime
    logging.Formatter.converter = time.localtime

    logger = logging.getLogger()

    return logger
