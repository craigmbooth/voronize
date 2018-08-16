import argparse
import copy
import logging
import random
import sys

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
from PIL import Image
import scipy.interpolate

from base_drawing import BaseDrawing
from plotter import Plotter
import util

sys.setrecursionlimit(15000)
class MazeDrawing(BaseDrawing):

    def get_command_line_args(self):
        self.parser.add_argument("--nx", type=int, default=20)
        self.parser.add_argument("--ny", type=int, default=20)


    def perform_computations(self):

        w = self.args.nx
        h = self.args.ny

        vis = [[0] * w + [1] for _ in range(h)] + [[1] * (w + 1)]
        ver = [["|  "] * w + ['|'] for _ in range(h)] + [[]]
        hor = [["+--"] * w + ['+'] for _ in range(h + 1)]

        def walk(x, y):
            vis[y][x] = 1

            d = [(x - 1, y), (x, y + 1), (x + 1, y), (x, y - 1)]
            random.shuffle(d)
            for (xx, yy) in d:
                if vis[yy][xx]: continue
                if xx == x: hor[max(y, yy)][x] = "+  "
                if yy == y: ver[y][max(x, xx)] = "   "
                walk(xx, yy)

        walk(random.randrange(w), random.randrange(h))

        return {"hor": hor, "ver": ver}


    def _yield_segments(self):
        hor = self.data["hor"]
        ver = self.data["ver"]

        scale = 1
        ry = 0
        s = 1
        for row_hor, row_ver in zip(hor, ver):
            rx = 0

            the_row = []
            for ix, hor_elem in enumerate(row_hor):

                # Delete entrance and exit
                if ry == 0 and ix == 0:
                    rx += s
                    continue
                if ry == self.args.ny and ix == len(row_hor)-2:
                    rx +=s
                    continue

                if "--" in hor_elem:
                    xs = [rx*scale, (rx+s)*scale]
                    if ry % 2 == 0:
                        xs = list(reversed(xs))
                    ys = [ry*scale, ry*scale]
                    plt.plot(xs, ys, "k")
                    the_row.append(np.array([
                        [xs[0], ys[0]], [xs[1], ys[1]]]))
                rx += s

            # Make drawing faster by reversing even numbered rows so the pen is
            # in the correct position
            if ry % 2 == 0:
                the_row = list(reversed(the_row))
            for elem in the_row:
                yield elem

            ry += s

        ry = 0
        for row_hor, row_ver in zip(hor, ver):
            rx = 0
            the_row = []
            for ver_elem in row_ver:
                if "|" in ver_elem:
                    xs = [rx*scale, rx*scale]
                    ys = [ry*scale, (ry+s)*scale]

                    the_row.append(np.array([
                        [xs[0], ys[0]], [xs[1], ys[1]]]))
                rx += s
            ry += s
            for elem in the_row:
                yield elem


    def display_image(self):

        for segment in self._yield_segments():
            xs = [segment[0][0], segment[1][0]]
            ys = [segment[0][1], segment[1][1]]
            plt.plot(xs, ys, "k")
        plt.show(block=False)



    def plot_image(self):

        xscale = float(self.p.xmax) / float(self.args.nx)
        yscale = float(self.p.ymax) / float(self.args.ny)

        scale = min([xscale, yscale])
        logging.info("Scaling image by factor {}".format(scale))
        for segment in self._yield_segments():
            self.p.write_segment(segment*scale)



if __name__ == "__main__":
    MazeDrawing()
