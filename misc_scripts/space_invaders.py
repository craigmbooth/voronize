import random

from plotter import Plotter

NX = 3
NY = 4

# Makes three pages, 35*39

PAGE = 2

SEED = 42

ndraw_x = 35
ndraw_y = 39

pixel_size = 32
invader_gap_px = 2


def number_to_2d_list(invader):
    binvader = "{0:b}".format(invader).zfill(12)

    binvader_elements = []
    for iy in range(NY):
        row = list(binvader[:NX])
        binvader = binvader[NX:]
        row.extend(row[::-1])
        binvader_elements.append(row)
    return binvader_elements

def draw_invader(p, invader, xoff, yoff):

    for iy, row in enumerate(invader):
        for ix, pixel in enumerate(row):
            if pixel == "1":
                cx = xoff + ix*pixel_size + pixel_size
                cy = yoff + iy*pixel_size + pixel_size
                p.write_square([cx, cy], pixel_size)

if __name__ == "__main__":

    with Plotter(verbose=True, dryrun=False) as p:

        calc_xmax = pixel_size * ndraw_x * (NX * 2 + invader_gap_px)
        calc_ymax = pixel_size * ndraw_y * (NY + invader_gap_px)

        base_xoff = (p.xmax - calc_xmax) * 0.5
        base_yoff = (p.ymax - calc_ymax) * 0.5

        print calc_xmax, p.xmax
        print calc_ymax, p.ymax

        if calc_xmax > p.xmax:
            raise ValueError
        if calc_ymax > p.ymax:
            raise ValueError

        invaders = range(1,2**(NX*NY))

        random.Random(SEED).shuffle(invaders)
        invaders = invaders[PAGE*ndraw_x*ndraw_y:]

        current_nx = 0
        current_ny = 0
        for invader in invaders:
            list_invader = number_to_2d_list(invader)

            xoff = base_xoff + current_nx * pixel_size * (2 * NX + invader_gap_px)
            yoff = base_yoff + current_ny * pixel_size * (NY + invader_gap_px)

            draw_invader(p, list_invader, xoff, yoff)

            current_nx += 1

            if current_nx == ndraw_x:
                current_ny += 1

            if current_ny == ndraw_y and current_nx == ndraw_x:
                break

            if current_nx == ndraw_x:
                current_nx = 0
