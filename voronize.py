import argparse
import logging
import random

import matplotlib.pyplot as plt
from numpy import*
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
                     ceil = 255):
    """Given the filename of an image, the number of random points to drop on
    there and a power representing the mapping between pixel darkness and
    probability of containing a point, place points on pixels weighted by their
    darkness, then do a voronoi tessellation on the resulting points and return
    the scipy voronoi tesselation object
    """

    temp=asarray(Image.open(img_file)).astype('float')
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
            yield vor.vertices[simplex]
        else:
            i = simplex[simplex >= 0][0]  # finite end Voronoi vertex

            t = vor.points[pointidx[1]] - vor.points[pointidx[0]]  # tangent
            t /= linalg.norm(t)
            n = array([-t[1], t[0]])  # normal

            midpoint = vor.points[pointidx].mean(axis=0)
            direction = sign(dot(midpoint - center, n)) * n
            far_point = vor.vertices[i] + direction * ptp_bound.max()
            yield [vor.vertices[i], far_point]


def draw_voronoi(vor, verbose=False):
    with Plotter(verbose=verbose, mock=True) as p:
        for segment in yield_voronoi_segments(vor):
            p.write_segment(segment)


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

    res = raw_input("Do you want to keep this one? [y/n]")
    return res in ["y", "Y"]

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("filename", type=str)
    parser.add_argument("vertices", type=int)
    parser.add_argument("--power", type=float, default=1.0)
    parser.add_argument("--floor", type=float, default=0)
    parser.add_argument("--ceil", type=float, default=255)
    parser.add_argument('--verbose', dest='verbose', action='store_true')
    parser.add_argument('--no-feature', dest='verbose', action='store_false')
    parser.set_defaults(verbose=False)
    args = parser.parse_args()

    util.init_logger(verbose=args.verbose)
    for arg in args._get_kwargs():
        logging.debug("Argument {} is {}".format(arg[0], arg[1]))

    image, vor = image_to_voronoi(args.filename, args.vertices, power=args.power,
                                  floor=args.floor, ceil=args.ceil)
    keep = plot_voronoi(image, vor, args.verbose)

    if keep is True:
        draw_voronoi(vor, verbose=args.verbose)
    else:
        if args.verbose is True:
            logging.info("Discarding image")

if __name__ == "__main__":
    main()
