import argparse
import random

from PIL import Image
from numpy import*
import matplotlib.pyplot as plt
from scipy.spatial import Voronoi, voronoi_plot_2d

IMG_SCALE = 8

def rgb2gray(rgb):

    r, g, b = rgb[:,:,0], rgb[:,:,1], rgb[:,:,2]
    gray = 0.2989 * r + 0.5870 * g + 0.1140 * b

    return gray

def image_to_voronoi(img_file, n_points, power):

    temp=asarray(Image.open(img_file)).astype('float')

    # Greyscale images are 2d arrays, color ones are 3d (x, y)
    if len(temp.shape) > 2:
        temp = rgb2gray(temp)

    npix = temp.shape[0] * temp.shape[1]
    temp = (255 - temp) ** power
    img_sum = sum(temp)
    temp = n_points * temp / img_sum

    actual_points = 0
    points = []
    for ii in range(temp.shape[0]):
        for jj in range(temp.shape[1]):
            if temp[ii][jj] > random.random():
                actual_points += 1
                points.append((ii,jj))
    print "Points requested: {}".format(n_points)
    print "Actual points generated: {}".format(actual_points)

    vor = Voronoi(points)

    return temp, vor

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

class Plotter():

    def __init__(self, verbose=False):
        self.verbose = verbose

    def __enter__(self):
        if self.verbose is True:
            print "IN;"
            print "SP1;"
        return self

    def __exit__(self, *args):
        if self.verbose is True:
            print "PU;"

    def write_segment(self, segment):
        pass


def draw_voronoi(vor, verbose=False):
    with Plotter(verbose=verbose) as p:
        for segment in yield_voronoi_segments(vor):
            p.write_segment(segment)


def plot_voronoi(image, vor, verbose=False):

    aspect_ratio = float(image.shape[0]) / image.shape[1]
    if verbose is True:
        print "Image has aspect ratio: {}".format(aspect_ratio)

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
    parser.add_argument('--verbose', dest='verbose', action='store_true')
    parser.add_argument('--no-feature', dest='verbose', action='store_false')
    parser.set_defaults(verbose=False)
    args = parser.parse_args()

    image, vor = image_to_voronoi(args.filename, args.vertices, args.power)
    keep = plot_voronoi(image, vor, args.verbose)

    if keep is True:
        draw_voronoi(vor)
    else:
        if args.verbose is True:
            print "Discarding image"

if __name__ == "__main__":
    main()
