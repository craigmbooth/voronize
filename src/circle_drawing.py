import argparse
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

IMG_SCALE = 8

class CircleDrawing(BaseDrawing):

    def get_command_line_args(self):
        self.parser.add_argument("image_file", type=str)
        self.parser.add_argument("--points", type=int, default=50000)
        self.parser.add_argument("--revolutions", type=int, default=30)
        self.parser.add_argument("--max-deviation", type=float, default=3)
        self.parser.add_argument("--scale-factor", type=float, default=0.5)


    def perform_computations(self):

        n = 1

        image=np.asarray(Image.open(
            self.args.image_file).rotate(180)).astype('float')

        if len(image.shape) > 2:
            image = util.rgb2gray(image)

        image[image > 200] = 255

        xcoords = np.linspace(-self.args.scale_factor,
                              self.args.scale_factor,image.shape[0])
        ycoords = np.linspace(-self.args.scale_factor,
                              self.args.scale_factor,image.shape[1])

        theta = ((np.linspace(
            0.0001, 1, num=self.args.points)) ** 0.5 *
                     self.args.revolutions*2*np.pi)

        r = theta ** (1/n)
        r = (r / max(abs(r))) * self.args.scale_factor
        xx = np.cos(theta)
        yy = np.sin(theta)
        xxc = np.copy(xx)
        yyc = np.copy(yy)
        xx *= r
        yy *= r

        darkness = scipy.interpolate.interpn(np.stack([ycoords, xcoords]),
                                       image, (xx, yy))
        darkness = (255-darkness) / 255.0
        darkness = darkness

        r = theta ** (1/n)
        r += darkness * self.args.max_deviation * np.sin(6000*theta*r)
        r = (r / max(abs(r))) * self.args.scale_factor

        return {"x": r*xxc, "y": r*yyc, "r": r}


    def display_image(self):
        plt.plot(self.data["x"], self.data["y"], 'k', linewidth=1)
        plt.show(block=False)


    def plot_image(self):

        xxc = self.data["x"]
        yyc = self.data["y"]
        r = self.data["r"]

        mx = (p.xmin + p.xmax) / 2.
        my = (p.ymin + p.ymax) / 2.
        maxradius = min([p.ymax, p.xmax]) / 2.0

        for i, _ in enumerate(xxc):
            if i == 0:
                continue

            start = np.array([r[i-1] * xxc[i-1],
                             r[i-1] * yyc[i-1]]) * maxradius
            end = np.array([r[i] * xxc[i],
                             r[i] * yyc[i]]) * maxradius

            start[0] += mx
            start[1] += my

            end[0] += mx
            end[1] += my
            self.p.write_segment(np.array([start, end]))


if __name__ == "__main__":
    CircleDrawing()
