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
        num_circles: int,
        circle_seed: list,
        num_radial: int,
        radial_seed: list,
        skip_circles: list,
        random_seed: int,
        output_path: str,
        width: float,
        height: float,
        dpi: int,
        downscale: int
        ):

    # Initialise figure. We disable most plot elements.
    # If we downscale, we enlarge the pattern figure by the downscale factor
    fig1 = plt.figure(figsize=(width * downscale, height * downscale))
    ax1 = fig1.add_axes([0,0,1,1], frameon=False)

    fig1.patch.set_visible(True)
    ax1.axis('off')
    fig1.patch.set_facecolor('white')

    lines = []
    theta = np.linspace(0, 2*np.pi, num_radial)

    # Draw the radiating lines
    r = np.sqrt(1)
    x1 = r*np.cos(theta)
    x2 = r*np.sin(theta)
    for i in range(0, len(x1), 2):
        seed = radial_seed[i]
        # Prevent index error
        if i+1 > len(x1) - 1:
            break
        for j in [i,i+1]:
            x_radial = np.linspace(0,x1[j],num_circles)
            a = x2[j]/x1[j]
            y_radial = a*x_radial
            for k in range(0+seed,len(x_radial),2):
                # Prevent index error
                if k+1 > len(x_radial) - 1:
                    break
                if k in skip_circles:
                    continue
                lines.append(((x_radial[k], y_radial[k]), (x_radial[k+1], y_radial[k+1])))

    # Draw the circles
    radii = np.linspace(0,1,num_circles)
    for i in range(0,len(radii)):
        if i-1 in skip_circles:
            continue
        r = radii[i]
        seed = circle_seed[i]
        x1 = r*np.cos(theta)
        x2 = r*np.sin(theta)
        for j in range(0+seed, len(x1), 2):
            # Prevent index error
            if j+1 > len(x1) - 1:
                break
            # Circle lines
            lines.append(((x1[j], x2[j]), (x1[j+1], x2[j+1])))

    # Draw outer circle
    theta = np.linspace(0, 2*np.pi, 1000)
    r = np.sqrt(1)
    x1 = r*np.cos(theta)
    x2 = r*np.sin(theta)
    for i in range(0, len(x1), 1):
        # Prevent index error
        if i+1 > len(x1) - 1:
            break
        lines.append(((x1[i], x2[i]), (x1[i+1], x2[i+1])))

    # Draw inner circle
    theta = np.linspace(0, 2*np.pi, num_radial)
    x_radial = np.linspace(0,1,num_circles)
    r = x_radial[np.max(skip_circles)+1]
    x1 = r*np.cos(theta)
    x2 = r*np.sin(theta)
    for i in range(0, len(x1), 1):
        # Prevent index error
        if i+1 > len(x1) - 1:
            break
        lines.append(((x1[i], x2[i]), (x1[i+1], x2[i+1])))

    # Draw our lines
    ln_coll = LineCollection(lines,
                        colors="black",
                        linewidths=0.5,
                        zorder=8,
                        antialiased=False
                        )
    ax1.add_collection(ln_coll)

    plt.xlim((-1,1))
    plt.ylim((-1,1))

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
    ind = np.where(img_grey == 1)

    # Make background transparent if requested
    if background == "transparent":
        mask = []
        mask.append(flood(img_grey,(ind[0][0],ind[0][0]),tolerance=0))
        mask.append(flood(img_grey,(ind[-1][0],ind[0][-1]),tolerance=0))
        mask.append(flood(img_grey,(ind[-1][-1],ind[-1][-1]),tolerance=0))
        mask.append(flood(img_grey,(ind[-1][-1],ind[-1][0]),tolerance=0))

        for item in mask:
            img_grey[item] = 0
            img[item] = (0,0,0,0)
            ind = np.where(img_grey == 1)

    # Each loop colors one patch
    while len(ind[0]) > 0:
        mask = flood(img_grey,(ind[0][0],ind[1][0]),tolerance=0)
        color = my_cmap(rng.random(), bytes=True)[:4]
        img[mask] = color
        img_grey[mask] = 0
        ind = np.where(img_grey == 1)

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
    parser.add_argument("-x1", type=int, default=50, help="The number of circles in the hitomezashi grid.")
    parser.add_argument("-x2", type=int, default=99, help="The number of radials in the hitomezashi grid. Best to use an odd number.")
    parser.add_argument("-c", type=str, default="all", help="Colormap to draw colors from.")
    parser.add_argument("-o", type=str, default="polar/", help="Relative path to save the images to.")
    parser.add_argument("-s", type=int, default=0, help="Seed Number. 0 will create a psuedorandom seed number.")
    parser.add_argument("--skip", type=str, default="0", help="Which inner circles to skip in the hitomezashi grid. Inner most circle is '0'. Can specify multiple circles (e.g. 0,1,2,etc.).")
    parser.add_argument("--width", type=float, default=5, help="Figure width in inches.")
    parser.add_argument("--height", type=float, default=5, help="Figure height in inches.")
    parser.add_argument("--background", type=str, default="transparent", help="'transparent' or 'colored' background.")
    parser.add_argument("--downscale", type=int, default=2, help="Factor by which to downscale the final image. To disable downscale, enter a value of 1.")
    args=parser.parse_args()
    return args

def main():
    args = parse_args()
    skip = [int(item) for item in args.skip.split(',')]

    # Paremeters of the binomial distribution
    circle_dist = 0.5
    radial_dist = 0.5

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
        circle_seed = rng.binomial(1, circle_dist, args.x1)
        radial_seed = rng.binomial(1, radial_dist, args.x2)

        # Draw shape and fill
        # Output directory is the user specified relative path + the pattern or colored folder + the number of circles + radials in the grid + the name of the colormap + the seeds number
        pattern_path = args.o + "/patterns/" + str(args.x1) + "_" + str(args.x2) + "/" + cmap + "/"
        makedirs(pattern_path, exist_ok=True)
        draw(args.x1, circle_seed, args.x2, radial_seed, skip, seed_seq.entropy, pattern_path, args.width, args.height, 100, args.downscale)

        colored_path = args.o + "/colored/" + str(args.x1) + "_" + str(args.x2) + "/" + cmap + "/"
        makedirs(colored_path, exist_ok=True)
        fill(cmap_object, rng, seed_seq.entropy, args.background, args.downscale, pattern_path, colored_path)

        plt.close()

if __name__ == '__main__':
    main()