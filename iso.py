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
from skimage.transform import rescale

def draw(
        x_1_seed: list,
        x_2_seed: list,
        y_seed: list,
        random_seed: int,
        output_path: str,
        width: float,
        height: float,
        dpi: int,
        downscale: int
        ):

    # Initialise figure. We disable most plot elements.
    # If we downscale, we enlarge the pattern figure by the downscale factor
    one_pixel = 1 / dpi # inch per pixel
    fig1 = plt.figure(figsize=(width * downscale, height * downscale))
    ax1 = fig1.add_axes([0,0,1,1], frameon=False)

    fig1.patch.set_visible(True)
    ax1.axis('off')
    fig1.patch.set_facecolor('white')

    # Will contain our lines we need to draw
    lines = []

    # Generate horizontal lines
    x_offset = -0.5
    for i in range(0,len(y_seed)):
        x_offset = x_offset + 0.5
        seed = y_seed[i]
        for j in range(0,len(x_1_seed), 2):
            # Prevent drawing outside of our triangle grid
            if (j + x_offset + 1 + seed) >  len(y_seed) - (i/2):
                break
            y1 = i
            y2 = i
            x1 = j + x_offset + seed
            x2 = j + x_offset + 1 + seed
            lines.append(((x1,y1), (x2,y2)))

    # Generate slanted lines
    for i in range(0,len(x_1_seed)):
        seed = x_1_seed[i]
        for j in range(0,len(y_seed), 2):
            # Prevent drawing outside of our triangle grid
            if (j + seed + 1) >= (len(x_1_seed) - i)*2:
                break
            y1 = j + seed
            y2 = j + seed + 1
            x1 = i + seed * 0.5
            x2 = i + seed * 0.5 + 0.5
            lines.append(((x1,y1), (x2,y2)))
            i = i + 1

    for i in range(0,len(x_2_seed)):
        seed = x_2_seed[i]
        for j in range(0,len(y_seed), 2):
            # Prevent drawing outside of our triangle grid
            if (j + seed + 1) >= i*2:
                break
            y1 = j + seed
            y2 = j + seed + 1
            x1 = i - seed * 0.5
            x2 = i - seed * 0.5 - 0.5
            lines.append(((x1,y1), (x2,y2)))
            i = i - 1

    # Generate border frame
    lines.append(((0,0), (len(x_1_seed),0)))
    lines.append(((0,0), (len(x_1_seed)/2,len(y_seed))))
    lines.append(((len(x_1_seed)/2,len(y_seed)), (len(x_1_seed),0)))

    # Draw our lines
    ln_coll = LineCollection(lines,
                        colors="black",
                        linewidths=0.5,
                        zorder=8,
                        antialiased=False
                        )
    ax1.add_collection(ln_coll)

    plt.xlim((-one_pixel,len(x_1_seed)))
    plt.ylim((-one_pixel,len(y_seed)))

    plt.savefig(output_path + "/" + str(random_seed) + ".png", dpi = dpi)

def fill(cmap: str,
        rng: any,
        random_seed: int,
        background: str,
        downscale: int,
        pattern_path: str,
        output_path: str):
    """Flood fills the hitomezashi pattern with colors from a colormap"""

    my_cmap = plt.get_cmap(cmap)

    # Load generated image
    img = imread(pattern_path + "/" + str(random_seed) + ".png")

    # We use the grayscale image for our flood function to find patches we need to color. Grayscale color scale is from 0 (black) to 1 (white).
    img_grey = rgb2gray(img[:,:,:3])
    
    # We will flood fill all white areas.
    # Get indices of pixels we need to color.
    ind = np.where(img_grey > 0.5)

    # Make background transparent if requested
    if background == "transparent":
        mask = []
        mask.append(flood(img_grey,(ind[0][0],ind[0][0]),tolerance=0))
        mask.append(flood(img_grey,(ind[-1][0],ind[0][-1]),tolerance=0))

        for item in mask:
            img_grey[item] = 0
            img[item] = (0,0,0,0)
            ind = np.where(img_grey > 0.5)

    # Each loop colors one patch
    while len(ind[0]) > 0:
        mask = flood(img_grey,(ind[0][0],ind[1][0]),tolerance=0)
        color = my_cmap(rng.random(), bytes=True)[:4]
        img[mask] = color
        img_grey[mask] = 0
        ind = np.where(img_grey > 0.5)

    # Downscale the image
    if downscale != 1:
        img = rescale(img, 0.5, channel_axis=-1, anti_aliasing=True)
        img *= 255
        img = img.astype(np.uint8)

    # Save image
    imsave(output_path + "/" + str(random_seed) + ".png", img)

def parse_args():
    parser=argparse.ArgumentParser(
        description="Plots hitomezashi patterns in a iso grid. ",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
        )
    parser.add_argument("-n", type=int, default=1, help="Number of patterns to generate.")
    parser.add_argument("-x", type=int, default=100, help="The number of triangles (width/height) in the hitomezashi grid.")
    parser.add_argument("-c", type=str, default="all", help="Colormap to draw colors from.")
    parser.add_argument("-o", type=str, default="iso/", help="Relative path to save the images to.")
    parser.add_argument("-s", type=int, default=0, help="Seed Number. 0 will create a psuedorandom seed number.")
    parser.add_argument("--width", type=float, default=10, help="Figure width in inches.")
    parser.add_argument("--height", type=float, default=10, help="Figure height in inches.")
    parser.add_argument("--background", type=str, default="transparent", help="'transparent' or 'colored' background.")
    parser.add_argument("--downscale", type=int, default=2, help="Factor by which to downscale the final image. To disable downscale, enter a value of 1.")
    args=parser.parse_args()
    return args

def main():
    args = parse_args()

    # Paremeters of the binomial distribution
    x_1_dist = 0.5
    x_2_dist = 0.5
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
        else:
            cmap_object = cmap

        # Generate our seeds for our shape we are going to draw. These determine whether we will draw lines at even or odd coordinates.
        x_1_seed = rng.binomial(1, x_1_dist, args.x)
        x_2_seed = rng.binomial(1, x_2_dist, args.x)
        y_seed = rng.binomial(1, y_dist, args.x)

        # Draw shape and fill
        # Output directory is the user specified relative path + the pattern or colored folder + the number of triangles in the grid + the name of the colormap + the seeds number
        pattern_path = args.o + "/patterns/" + str(args.x) + "/" + cmap + "/"
        makedirs(pattern_path, exist_ok=True)
        draw(x_1_seed, x_2_seed, y_seed, seed_seq.entropy, pattern_path, args.width, args.height, 100, args.downscale)

        colored_path = args.o + "/colored/" + str(args.x) + "/" + cmap + "/"
        makedirs(colored_path, exist_ok=True)
        fill(cmap_object, rng, seed_seq.entropy, args.background, args.downscale, pattern_path, colored_path)

        plt.close()

if __name__ == '__main__':
    main()