from PIL import Image
import matplotlib.pyplot as plt
import numpy as np
from scipy import interpolate

from plotter import Plotter

def rgb2gray(rgb):
    """Given an (nx x ny x 3) array, flatten it into a greyscale image

    The coefficients here are from Matlab's NTSC/PAL implementation
    """
    r, g, b = rgb[:,:,0], rgb[:,:,1], rgb[:,:,2]
    gray = 0.2989 * r + 0.5870 * g + 0.1140 * b
    return gray


num = 50000
revolutions = 40
n = 1
max_deviation = 2.7

img_file = "portrait.png"
temp=np.asarray(Image.open(img_file).rotate(180)).astype('float')
if len(temp.shape) > 2:
    temp = rgb2gray(temp)

xcoords = np.linspace(-1,1,temp.shape[0])
ycoords = np.linspace(-1,1,temp.shape[1])

theta = (np.linspace(0.0005, 1, num=num)) ** 0.5 * revolutions*2*np.pi

r = theta ** (1/n)
r = r / max(abs(r))
xx = np.cos(theta)
yy = np.sin(theta)
xxc = np.copy(xx)
yyc = np.copy(yy)
xx *= r
yy *= r

darkness = interpolate.interpn(np.stack([ycoords, xcoords]), temp, (xx, yy))
darkness = (255-darkness) / 255.0
darkness = darkness

r = theta ** (1/n)
r += darkness * max_deviation * np.sin(300*theta*r)
r = r / max(abs(r))

plt.plot(r*xxc, r*yyc, 'k', linewidth=1)
plt.show()


with Plotter(verbose=True, dryrun=False) as p:
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
        p.write_segment(np.array([start, end]))
