import util

class BaseDrawing(object):

    def __init__(self):

        parser = argparse.ArgumentParser()
        parser.add_argument('--verbose', dest='verbose', action='store_true')
        parser.set_defaults(verbose=False)
        parser.add_argument('--dry-run', dest='dryrun', action='store_true')
        parser.set_defaults(dryrun=False)

        self.args = self.get_command_line_args().parse_args()

        util.init_logger(verbose=self.args.verbose)

        self.data = self.perform_computations()

        if self.display_image() is True:
            plot_image()
        else:
            if args.verbose is True:
                logging.info("Discarding image")


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
