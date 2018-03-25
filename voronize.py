import argparse
import logging
import random
import time

import matplotlib.pyplot as plt
from numpy import *
import networkx as nx
from PIL import Image
import serial
from scipy.spatial import Voronoi, voronoi_plot_2d

from plotter import Plotter
import util


IMG_SCALE = 8

def rgb2gray(rgb):
    """Given an (nx x ny x 3) array, flatten it into a greyscale image

    The coefficients here are from Matlab's NTSC/PAL implementation
    """
    r, g, b = rgb[:,:,0], rgb[:,:,1], rgb[:,:,2]
    gray = 0.2989 * r + 0.5870 * g + 0.1140 * b
    return gray

def image_to_voronoi(img_file, n_points, power=power, floor=0,
                     ceil = 255, rotate=0):
    """Given the filename of an image, the number of random points to drop on
    there and a power representing the mapping between pixel darkness and
    probability of containing a point, place points on pixels weighted by their
    darkness, then do a voronoi tessellation on the resulting points and return
    the scipy voronoi tesselation object
    """

    temp=asarray(Image.open(img_file).rotate(rotate, expand=True)).astype('float')
    logging.info("Loaded image {}".format(img_file))
    logging.info("Image has size {}x{}".format(temp.shape[0], temp.shape[1]))

    # Greyscale images are 2d arrays, color ones are 3d (x, y)
    if len(temp.shape) > 2:
        logging.info("Image is in color, changing to greyscale")
        temp = rgb2gray(temp)

    temp = (255 - temp)
    temp[temp < floor] = floor
    temp[temp > ceil] = ceil
    temp = temp ** power

    # Convert each point to the probability of containing a point
    temp = n_points * temp / sum(temp)

    actual_points = 0
    points = []
    for ii in range(temp.shape[0]):
        for jj in range(temp.shape[1]):
            if temp[ii][jj] > random.random():
                actual_points += 1
                points.append((ii,jj))

    logging.info("Points requested: {}".format(n_points))
    logging.info("Actual points generated: {}".format(actual_points))

    return temp, Voronoi(points)

def yield_voronoi_segments(vor):

    center = vor.points.mean(axis=0)
    ptp_bound = vor.points.ptp(axis=0)

    finite_segments = []
    infinite_segments = []
    for pointidx, simplex in zip(vor.ridge_points, vor.ridge_vertices):
        simplex = asarray(simplex)
        if all(simplex >= 0):
            yield vor.vertices[simplex].astype(int)
        else:
            i = simplex[simplex >= 0][0]  # finite end Voronoi vertex

            t = vor.points[pointidx[1]] - vor.points[pointidx[0]]  # tangent
            t /= linalg.norm(t)
            n = array([-t[1], t[0]])  # normal

            midpoint = vor.points[pointidx].mean(axis=0)
            direction = sign(dot(midpoint - center, n)) * n
            far_point = vor.vertices[i] + direction * ptp_bound.max()
            yield [vor.vertices[i].astype(int), far_point.astype(int)]


def get_neighbors(G, source):
    all_neighbors = [(x, G.degree(x)) for x in G.neighbors(source)]
    if len(all_neighbors) == 0:
        return []
    max_degree = max([x[1] for x in all_neighbors])
    return [x[0] for x in all_neighbors if x[1] == max_degree]


def sort_segments(segments):
    logging.info("[OPTIMIZER] Starting path optimization...")
    G = nx.Graph()

    nodes = set()
    for s in segments:
        nfrom = "{},{}".format(s[0][0], s[0][1])
        nto = "{},{}".format(s[1][0], s[1][1])
        G.add_node(nfrom, x=s[0][0], y=s[0][1])
        G.add_node(nto, x=s[1][0], y=s[1][1])
        G.add_edge(nfrom, nto)
    logging.info("\t... Number of nodes in graph: {}".format(G.number_of_nodes()))
    logging.info("\t... Number of edges in graph: {}".format(G.number_of_edges()))

    sorted_segments = []
    line_len = 0
    all_lines = []
    while G.number_of_edges() > 0:
        source = random.choice(G.nodes())
        neighbors = get_neighbors(G, source)
        this_line = []

        if len(neighbors) == 0:
            G.remove_node(source)
            continue

        while len(neighbors) > 0:
            dest = random.choice(neighbors)
            this_line.append(
                [asarray([G.node[source]["x"], G.node[source]["y"]]),
                asarray([G.node[dest]["x"], G.node[dest]["y"]])]
                )
            line_len += 1
            G.remove_edge(source, dest)
            source = dest
            neighbors = get_neighbors(G, source)
        line_len = 0
        all_lines.append(this_line)
        G.remove_node(source)

    thresh = 5

    long_lines = [x for x in all_lines if len(x) > thresh]
    short_lines = [x for x in all_lines if len(x) <= thresh]

    # Sort so that for long line segments we start by drawing the longest
    long_lines = sorted(long_lines, key = lambda x:-len(x))

    # And for short line segments, sort by x coordinate
    short_lines = sorted(short_lines, key=lambda x: 1000000*x[0][0][0] + x[0][0][0])

    long_lines_flat = [item for sublist in long_lines for item in sublist]
    short_lines_flat = [item for sublist in short_lines for item in sublist]
    return long_lines_flat + short_lines_flat






    return sorted_segments


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
    parser.add_argument('--dry-run', dest='dryrun', action='store_true')
    parser.set_defaults(dryrun=False)

    args = parser.parse_args()

    util.init_logger(verbose=args.verbose)
    for arg in args._get_kwargs():
        logging.debug("Argument {} is {}".format(arg[0], arg[1]))

    image, vor = image_to_voronoi(args.filename, args.vertices, power=args.power,
                                  floor=args.floor, ceil=args.ceil)
    keep, img_size = plot_voronoi(image, vor, verbose=args.verbose)

    if keep is True:
        draw_voronoi(vor, img_size, verbose=args.verbose, dryrun=args.dryrun)
    else:
        if args.verbose is True:
            logging.info("Discarding image")

if __name__ == "__main__":
    main()
