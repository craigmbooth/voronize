from PIL import Image
import matplotlib.pyplot as plt
import numpy as np
from scipy import interpolate


from plotter import Plotter
import util

def main():
    num = 80000
    revolutions = 30
    n = 1
    max_deviation = 3
    scale_factor = 0.5

    img_file = "sources/bertrand.png"
    temp=np.asarray(Image.open(img_file).rotate(180)).astype('float')

    if len(temp.shape) > 2:
        temp = util.rgb2gray(temp)


    temp[temp > 200] = 255

    xcoords = np.linspace(-scale_factor,scale_factor,temp.shape[0])
    ycoords = np.linspace(-scale_factor,scale_factor,temp.shape[1])

    theta = (np.linspace(0.0001, 1, num=num)) ** 0.5 * revolutions*2*np.pi

    r = theta ** (1/n)
    r = (r / max(abs(r))) * scale_factor
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
    r += darkness * max_deviation * np.sin(6000*theta*r)
    r = (r / max(abs(r))) * scale_factor

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

if __name__ == "__main__":
    main()
