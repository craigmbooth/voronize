import argparse
import logging
import random

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
from PIL import Image
from scipy.spatial import Voronoi, voronoi_plot_2d

from base_drawing import BaseDrawing
from plotter import Plotter
import util

IMG_SCALE = 8

class VoronoiDrawing(BaseDrawing):

    def get_command_line_args(self):
        self.parser.add_argument("filename", type=str)
        self.parser.add_argument("vertices", type=int)
        self.parser.add_argument("--power", type=float, default=1.0)
        self.parser.add_argument("--floor", type=float, default=0)
        self.parser.add_argument("--ceil", type=float, default=255)
        self.parser.add_argument('--rotate', type=float, default=0)
        self.parser.set_defaults(rotate=False)


    def perform_computations(self):
        """Given the filename of an image, the number of random points to drop on
        there and a power representing the mapping between pixel darkness and
        probability of containing a point, place points on pixels weighted by their
        darkness, then do a voronoi tessellation on the resulting points and return
        the scipy voronoi tesselation object
        """

        img=np.asarray(Image.open(
            self.args.filename).rotate(
                self.args.rotate, expand=True)).astype('float')
        logging.info("Loaded image {}".format(self.args.filename))
        logging.info("Image has size {}x{}".format(img.shape[0], img.shape[1]))

        # Greyscale images are 2d arrays, color ones are 3d (x, y)
        if len(img.shape) > 2:
            logging.info("Image is in color, changing to greyscale")
            img = util.rgb2gray(img)

        img = (255 - img)
        img[img < self.args.floor] = self.args.floor
        img[img > self.args.ceil] = self.args.ceil
        img = img ** self.args.power

        # Convert each point to the probability of containing a point
        img = self.args.vertices * img / np.sum(img)

        actual_points = 0
        points = []
        for ii in range(img.shape[0]):
            for jj in range(img.shape[1]):
                if img[ii][jj] > random.random():
                    actual_points += 1
                    points.append((ii,jj))

        logging.info("Points requested: {}".format(self.args.vertices))
        logging.info("Actual points generated: {}".format(actual_points))

        return {"image": img, "voronoi": Voronoi(points)}

    def _yield_voronoi_segments(self, vor):

        center = vor.points.mean(axis=0)
        ptp_bound = vor.points.ptp(axis=0)

        finite_segments = []
        infinite_segments = []
        for pointidx, simplex in zip(vor.ridge_points, vor.ridge_vertices):
            simplex = np.asarray(simplex)
            if all(simplex >= 0):
                yield vor.vertices[simplex].astype(int)
            else:
                i = simplex[simplex >= 0][0]  # finite end Voronoi vertex

                t = vor.points[pointidx[1]] - vor.points[pointidx[0]]  # tangent
                t /= np.linalg.norm(t)
                n = np.array([-t[1], t[0]])  # normal

                midpoint = vor.points[pointidx].mean(axis=0)
                direction = np.sign(np.dot(midpoint - center, n)) * n
                far_point = vor.vertices[i] + direction * ptp_bound.max()
                yield [vor.vertices[i].astype(int), far_point.astype(int)]


    def _get_neighbors(self, G, source):
        all_neighbors = [(x, G.degree(x)) for x in G.neighbors(source)]
        if len(all_neighbors) == 0:
            return []
        max_degree = max([x[1] for x in all_neighbors])
        return [x[0] for x in all_neighbors if x[1] == max_degree]


    def _sort_segments(self, segments):
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
            source = random.choice(list(G.nodes()))
            neighbors = self._get_neighbors(G, source)
            this_line = []

            if len(neighbors) == 0:
                G.remove_node(source)
                continue

            while len(neighbors) > 0:
                dest = random.choice(neighbors)
                this_line.append(
                    [np.asarray([G.node[source]["x"], G.node[source]["y"]]),
                    np.asarray([G.node[dest]["x"], G.node[dest]["y"]])]
                    )
                line_len += 1
                G.remove_edge(source, dest)
                source = dest
                neighbors = self._get_neighbors(G, source)
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


    def display_image(self):
        """Given a 2d image array and its voronoi tesselation, plot the voronoi
        tesselation, and ask whether to keep it
        """

        image = self.data["image"]
        vor = self.data["voronoi"]

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

        res = input("Do you want to keep this one? [y/n]: ")
        return res in ["y", "Y"]


    def plot_image(self):

        segments = self._yield_voronoi_segments(self.data["voronoi"])
        segments = self._sort_segments(segments)

        img_size = self.data["image"].shape

        with Plotter(verbose=self.args.verbose, dryrun=self.args.dryrun) as p:
            p.set_image_scale(img_size)
            for segment in segments:
                p.write_segment(segment)


if __name__ == "__main__":
    VoronoiDrawing()
