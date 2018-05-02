import argparse
import logging
import random
import time

import matplotlib.pyplot as plt
from numpy import *
import networkx as nx
from PIL import Image
from scipy.spatial import Voronoi, voronoi_plot_2d

from plotter import Plotter
import util

IMG_SCALE = 8




def draw_voronoi(vor, img_size, verbose=False, dryrun=False):

    segments = yield_voronoi_segments(vor)
    segments = sort_segments(segments)

    start = time.time()
    with Plotter(verbose=verbose, dryrun=dryrun) as p:
        p.set_image_scale(img_size)
        for segment in segments:
            p.write_segment(segment)
    end = time.time()
    logging.info("Drawing took {}s".format((end-start)))


def plot_voronoi(image, vor, verbose=False):
    """Given a 2d image array and its voronoi tesselation, plot the voronoi
    tesselation, and ask whether to keep it
    """

    aspect_ratio = float(image.shape[0]) / image.shape[1]
    logging.debug("Image has aspect ratio: {}".format(aspect_ratio))

    voronoi_plot_2d(vor, show_points=False, show_vertices=False)
    fig = plt.gcf()
    fig.set_size_inches(IMG_SCALE*aspect_ratio, IMG_SCALE)

    fig.axes[0].get_xaxis().set_visible(False)
    fig.axes[0].get_yaxis().set_visible(False)

    plt.xlim([0,image.shape[0]])
    plt.ylim([0,image.shape[1]])

    plt.show(block=False)

    res = raw_input("Do you want to keep this one? [y/n]: ")
    return (res in ["y", "Y"], image.shape)

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("filename", type=str)
    parser.add_argument("vertices", type=int)
    parser.add_argument("--power", type=float, default=1.0)
    parser.add_argument("--floor", type=float, default=0)
    parser.add_argument("--ceil", type=float, default=255)
    parser.add_argument('--verbose', dest='verbose', action='store_true')
    parser.set_defaults(verbose=False)
    parser.add_argument('--rotate', dest='rotate', action='store_true')
    parser.set_defaults(rotate=False)
    parser.add_argument('--dry-run', dest='dryrun', action='store_true')
    parser.set_defaults(dryrun=False)

    args = parser.parse_args()

    util.init_logger(verbose=args.verbose)
    for arg in args._get_kwargs():
        logging.debug("Argument {} is {}".format(arg[0], arg[1]))

    image, vor = image_to_voronoi(args.filename, args.vertices, power=args.power,
                                  floor=args.floor, ceil=args.ceil,
                                  rotate=0 if args.rotate is False else -90)
    keep, img_size = plot_voronoi(image, vor, verbose=args.verbose)

    if keep is True:
        draw_voronoi(vor, img_size, verbose=args.verbose, dryrun=args.dryrun)
    else:
        if args.verbose is True:
            logging.info("Discarding image")

if __name__ == "__main__":
    main()
