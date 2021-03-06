import logging
import sys

def rgb2gray(rgb):
    """Given an (nx x ny x 3) array, flatten it into a greyscale image

    The coefficients here are from Matlab's NTSC/PAL implementation
    """
    r, g, b = rgb[:,:,0], rgb[:,:,1], rgb[:,:,2]
    gray = 0.2989 * r + 0.5870 * g + 0.1140 * b
    return gray


def init_logger(verbose=False):
    """Sets up logging for this cli"""
    log_level = logging.DEBUG if verbose is True else logging.INFO

    logging.basicConfig(format="%(levelname)s %(message)s\033[1;0m",
                        stream=sys.stderr, level=log_level)

    logging.addLevelName(logging.CRITICAL,
                         "\033[1;37m[\033[1;31mCRIT\033[1;37m]\033[0;31m")
    logging.addLevelName(logging.ERROR,
                         "\033[1;37m[\033[1;33mERR\033[1;37m]\033[0;33m")
    logging.addLevelName(logging.WARNING,
                         "\033[1;37m[\033[1;33mWARN\033[1;37m]\033[0;33m")
    logging.addLevelName(logging.INFO,
                         "\033[1;37m[\033[1;32mINFO\033[1;37m]\033[0;37m")
    logging.addLevelName(logging.DEBUG,
                         "\033[1;37m[\033[1;34mDBUG\033[1;37m]\033[0;34m")

    # Squelch noisy loggers
    logging.getLogger('boto3').setLevel(logging.WARNING)
    logging.getLogger('PIL').setLevel(logging.WARNING)
    logging.getLogger('botocore').setLevel(logging.WARNING)
    logging.getLogger('s3transfer').setLevel(logging.WARNING)
    logging.getLogger('nose').setLevel(logging.WARNING)
    logging.getLogger('requests').setLevel(logging.WARNING)
    logging.getLogger('fitbit').setLevel(logging.WARNING)
