import argparse
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from  matplotlib.colors import ListedColormap
import numpy as np
from skimage.segmentation import flood
from skimage.io import imread, imsave
from skimage.color import rgb2gray
from metbrewer import met_brew, return_met_palettes
from os import makedirs

def draw(
        x_seed: list,
        y_seed: list,
        random_seed: int,
        output_path: str,
        width: float,
        height: float,
        padding: float,
        dpi: int
        ):
    """Generates a square hitomezashi pattern"""

    # Initialise figure.
    """
    We want to expand the size of the figure slightly because the frameon takes up space in the figure.
    For example, if width/height=10, dpi=100, and x=200; we expect every square to take up 5 pixels, perfectly filling up the space.
    However, because the frameon takus up space, the 200 squares have 999 pixels, causing some squares to be 4 pixel wide/high.
    To compensate we make the figure larger by one pixel.
    """
    one_pixel = 1 / dpi # inch per pixel
    fig_width = np.round(width * (1 + padding) + one_pixel, 2) # in inches
    fig_height = np.round(height * (1 + padding) + one_pixel, 2) # in inches
    fig1 = plt.figure(figsize=(fig_width, fig_height))

    """
    Here we add the padding to the figure.
    The amount of padding (in pixels) being added is height/width * dpi * padding.
    So if the padding=0.02 (2%), height/width=10, and dpi=100; the amount of padding added is 20 pixels.
    Keep in mind that 20 pixels here means that 10 pixels get added to the left/top and 10 to the right/bottom
    """
    ratio = (width * dpi) / (width * dpi * (1 + padding) + one_pixel)
    width_padding = round(ratio * padding * (width * dpi * (1 + padding)) + 1) # in pixels
    height_padding = round(ratio * padding * (height * dpi * (1 + padding)) + 1) # in pixels
    ax1 = fig1.add_axes([(ratio * padding / 2),(ratio * padding / 2),(1 - (width_padding / round(fig_width * dpi))),(1 - (height_padding / round(fig_height * dpi)))], frameon=True)
    fig1.patch.set_visible(True)
    fig1.patch.set_facecolor('white')

    # Disable axes ticks and labels
    plt.tick_params(
        axis='both',
        which='both',
        bottom=False,
        top=False,
        left=False,
        right=False,
        labelbottom=False,
        labelleft=False
        )

    # Will contain our lines we need to draw
    lines = []

    # Generate horizontal lines
    for i in range(0,len(x_seed)):
        seed = x_seed[i]
        for j in range(0,len(y_seed), 2):
            y1 = i
            y2 = i
            x1 = j + seed
            x2 = j + 1 + seed
            lines.append(((x1,y1), (x2,y2)))

    # Generate vertical lines
    for i in range(0,len(y_seed)):
        seed = y_seed[i]
        for j in range(0,len(x_seed), 2):
            y1 = j + seed
            y2 = j + 1 + seed
            x1 = i
            x2 = i
            lines.append(((x1,y1), (x2,y2)))

    # Draw our lines
    ln_coll = LineCollection(lines,
                        colors="black",
                        linewidths=0.5,
                        zorder=8,
                        antialiased=False
                        )
    ax1.add_collection(ln_coll)

    plt.xlim((0,len(x_seed)))
    plt.ylim((0,len(y_seed)))

    plt.savefig(output_path + "/" + str(random_seed) + ".png", dpi = dpi)

def fill(cmap: str,
        rng: any,
        random_seed: int,
        pattern_path: str,
        output_path: str):
    """Flood fills the hitomezashi pattern with colors from a colormap"""

    my_cmap = plt.get_cmap(cmap)

    # Load generated image
    img = imread(pattern_path + "/" + str(random_seed) + ".png")[:,:,:3]
    # We use the grayscale image for our flood function to find patches we need to color
    img_grey = rgb2gray(img)
    
    # Get indices of pixels we need to color
    ind = np.where(img_grey == 1)

    # Each loop colors one patch
    while len(ind[0]) > 0:
        mask = flood(img_grey,(ind[0][0],ind[1][0]),tolerance=0.5)
        color = my_cmap(rng.random(), bytes=True)[:3]
        img[mask] = color
        img_grey[mask] = 0
        ind = np.where(img_grey == 1)

    # Save image
    imsave(output_path + "/" + str(random_seed) + ".png", img)

def parse_args():
    parser=argparse.ArgumentParser(
        description="Plots hitomezashi patterns in a square grid. ",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
        )
    parser.add_argument("-n", type=int, default=1, help="Number of patterns to generate.")
    parser.add_argument("-x", type=int, default=100, help="The number of squares (width/height) in the hitomezashi grid.")
    parser.add_argument("-c", type=str, default="all", help="Colormap to draw colors from.")
    parser.add_argument("-o", type=str, default="square/", help="Relative path to save the images to.")
    parser.add_argument("-s", type=int, default=0, help="Seed Number. 0 will create a psuedorandom seed number.")
    parser.add_argument("--width", type=float, default=10, help="Figure width in inches.")
    parser.add_argument("--height", type=float, default=10, help="Figure height in inches.")
    parser.add_argument("--padding", type=float, default=0.04, help="Percentage of the figure height/width which is added as padding.")
    args=parser.parse_args()
    return args


def main():
    args = parse_args()

    # Paremeters of the binomial distribution
    x_dist = 0.5
    y_dist = 0.5

    # The matplotlib colormaps
    cmaps = {
        "uniform": ['viridis', 'plasma', 'inferno', 'magma', 'cividis'],
        "sequential": ['Greys', 'Purples', 'Blues', 'Greens', 'Oranges', 'Reds',
                      'YlOrBr', 'YlOrRd', 'OrRd', 'PuRd', 'RdPu', 'BuPu',
                      'GnBu', 'PuBu', 'YlGnBu', 'PuBuGn', 'BuGn', 'YlGn'],
        "sequential2": ['binary', 'gist_yarg', 'gist_gray', 'gray', 'bone',
                      'pink', 'spring', 'summer', 'autumn', 'winter', 'cool',
                      'Wistia', 'hot', 'afmhot', 'gist_heat', 'copper'],
        "diverging": ['PiYG', 'PRGn', 'BrBG', 'PuOr', 'RdGy', 'RdBu', 'RdYlBu',
                      'RdYlGn', 'Spectral', 'coolwarm', 'bwr', 'seismic',
                      'berlin', 'managua', 'vanimo'],
        "cyclic": ['twilight', 'twilight_shifted', 'hsv'],
        "qualitative": ['Pastel1', 'Pastel2', 'Paired', 'Accent', 'Dark2',
                      'Set1', 'Set2', 'Set3', 'tab10', 'tab20', 'tab20b',
                      'tab20c'],
        "misc": ['flag', 'prism', 'ocean', 'gist_earth', 'terrain',
                      'gist_stern', 'gnuplot', 'gnuplot2', 'CMRmap',
                      'cubehelix', 'brg', 'gist_rainbow', 'rainbow', 'jet',
                      'turbo', 'nipy_spectral', 'gist_ncar']
    }

    # Generate n number of hitomezashi plots
    for i in range(0,args.n):

        # Initialise seed for RNG
        if args.s ==0:
            seed_seq = np.random.SeedSequence()
        else:
            seed_seq = np.random.SeedSequence(args.s)

        rng = np.random.default_rng(seed_seq)

        #Get cmap
        met_palettes = return_met_palettes()
        cmaps_list = []
        if args.c == "all":
            for cmap_name in cmaps:
                for item in cmaps[cmap_name]:
                    cmaps_list.append(item)
            for cmap_name in met_palettes:
                cmaps_list.append(cmap_name)
        elif args.c == "metbrewer":
            cmaps_list = []
            for cmap_name in met_palettes:
                cmaps_list.append(cmap_name)
        else:
             cmaps_list.append(args.c)

        cmap_ind = rng.integers(0, len(cmaps_list))
        cmap = cmaps_list[cmap_ind]

        if cmap in met_palettes:
            colors = met_brew(cmap)
            cmap_object = ListedColormap(colors)

        # Generate our seeds for our shape we are going to draw. These determine whether we will draw lines at even or odd coordinates.
        x_seed = rng.binomial(1, x_dist, args.x)
        y_seed = rng.binomial(1, y_dist, args.x)

        # Draw shape and fill
        # Output directory is the user specified relative path + the pattern or colored folder + the number of squares in the grid + the name of the colormap + the seeds number
        pattern_path = args.o + "/patterns/" + str(args.x) + "/" + cmap + "/"
        makedirs(pattern_path, exist_ok=True)
        draw(x_seed, y_seed, seed_seq.entropy, pattern_path, args.width, args.height, args.padding, 100)

        colored_path = args.o + "/colored/" + str(args.x) + "/" + cmap + "/"
        makedirs(colored_path, exist_ok=True)
        fill(cmap_object, rng, seed_seq.entropy, pattern_path, colored_path)

        plt.close()


if __name__ == "__main__":
    main()