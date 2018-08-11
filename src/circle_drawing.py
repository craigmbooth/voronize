import argparse
import logging
import random

import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
from PIL import Image

from base_drawing import BaseDrawing
from plotter import Plotter
import util

IMG_SCALE = 8

class CircleDrawing(BaseDrawing):

    def get_command_line_args(self):
        self.parser.add_argument("filename", type=str)
        self.parser.add_argument("vertices", type=int)
        self.parser.add_argument("--power", type=float, default=1.0)
        self.parser.add_argument("--floor", type=float, default=0)
        self.parser.add_argument("--ceil", type=float, default=255)
        self.parser.add_argument('--rotate', type=float, default=0)
        self.parser.set_defaults(rotate=False)


    def perform_computations(self):
        pass


    def display_image(self):
        pass

    def plot_image(self):
        pass


if __name__ == "__main__":
    CircleDrawing()
