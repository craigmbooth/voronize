import argparse
import time

import logging
from plotter import Plotter
import util

class BaseDrawing(object):

    def __init__(self):

        self.parser = argparse.ArgumentParser()
        self.parser.add_argument('--verbose', dest='verbose', action='store_true')
        self.parser.set_defaults(verbose=False)
        self.parser.add_argument('--dry-run', dest='dryrun', action='store_true')
        self.parser.set_defaults(dryrun=False)

        self.get_command_line_args()

        self.args = self.parser.parse_args()

        util.init_logger(verbose=self.args.verbose)

        self.data = self.perform_computations()

        self.display_image()
        res = input("Do you want to keep this one? [y/n]: ")
        keep = res in ["y", "Y"]

        if keep is True:
            start = time.time()
            with Plotter(verbose=self.args.verbose,
                         dryrun=self.args.dryrun) as self.p:
                self.plot_image()
            end = time.time()
            logging.info("Drawing took {}s".format((end-start)))
        else:
            logging.debug("Discarding image")


    def get_command_line_args(self):
        raise NotImplementedError("You must implement the "
                                  "get_command_line_args function")


    def perform_computations(self):
        raise NotImplementedError("You must implement the perform_computations "
                                  "function")


    def display_image(self):
        """Returns keep, a boolean stating whether or not to keep the image
        """
        raise NotImplementedError("You must implement the display_image "
                                  "function")


    def plot_image(self):
        raise NotImplementedError("You must implement the plot_image "
                                  "function")
