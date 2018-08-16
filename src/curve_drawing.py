import argparse
import copy
import logging
import random

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
from PIL import Image
import scipy.interpolate

from base_drawing import BaseDrawing
from plotter import Plotter
import util


class CurveDrawing(BaseDrawing):

    def get_command_line_args(self):
        self.parser.add_argument("image_file", type=str)
        self.parser.add_argument("--points", type=int, default=500)
        self.parser.add_argument("--rotate", type=int, default=0)
        self.parser.add_argument("--power", type=float, default=1.0)
        self.parser.add_argument("--floor", type=float, default=0)
        self.parser.add_argument("--ceil", type=float, default=255)
        self.parser.add_argument("--choice-scatter", type=int, default=50)
        self.parser.add_argument("--jump-probability", type=float, default=0.005)

    def perform_computations(self):

        img=np.asarray(Image.open(
            self.args.image_file).rotate(
                self.args.rotate, expand=True)).astype('float')
        logging.info("Loaded image {}".format(self.args.image_file))
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
        img = self.args.points * img / np.sum(img)

        actual_points = 0
        points = []
        for ii in range(img.shape[0]):
            for jj in range(img.shape[1]):
                if img[ii][jj] > random.random():
                    actual_points += 1
                    points.append((ii,jj))

        pc = copy.copy(points)
        logging.info("Points requested: {}".format(self.args.points))
        logging.info("Actual points generated: {}".format(actual_points))

        points = self._sort_points(points)
        points = np.array(points)

        tck, u = scipy.interpolate.splprep(points.T, u=None, s=0.0, per=1)
        u_new = np.linspace(u.min(), u.max(), len(points)*10)
        x_new, y_new = scipy.interpolate.splev(u_new, tck, der=0)

        return {"points": pc, "x": x_new, "y": y_new}


    def _sort_points(self, points):

        sorted_points = []
        np.random.shuffle(points)

        first, rest = points[0], points[1:]
        points = rest
        sorted_points.append(first)

        while len(points) > 0:
            xc = sorted_points[-1][0]
            yc = sorted_points[-1][1]

            if random.random() < self.args.jump_probability:
                np.random.shuffle(points)
                first, rest = points[0], points[1:]
                points = rest
            else:
                points.sort(key=lambda x: (x[0]-xc)**2 + (x[1]-yc)**2)
                max_pick = min([len(points), self.args.choice_scatter])
                if len(points) < self.args.choice_scatter:
                    break
                selected_point = random.randint(0, max_pick-1)
                first = points[selected_point]
                del(points[selected_point])


            sorted_points.append(first)

        return sorted_points


    def display_image(self):

        points = self.data["points"]
        x = self.data["x"]
        y = self.data["y"]

        px = [x[0] for x in points]
        py = [x[1] for x in points]

        plt.plot(x, y, 'k', linewidth=1)
        plt.show(block=False)



    def plot_image(self):

        x = self.data["x"]
        y = self.data["y"]

        xmin = min(x)
        xmax = max(x)
        ymin = min(y)
        ymax = max(y)

        # n.b. there is probably a fix to do here to get things to scale to
        # the full size of the page.
        divisor = max([(xmax-xmin), (ymax-ymin)])
        x = self.p.ymax * (x - xmin) / divisor
        y = self.p.ymax * (y - ymin) / divisor

        for i, _ in enumerate(x):
            if i == 0:
                continue

            start = np.array([x[i-1], y[i-1]])
            end = np.array([x[i], y[i]])
            self.p.write_segment(np.array([start, end]))


if __name__ == "__main__":
    CurveDrawing()
