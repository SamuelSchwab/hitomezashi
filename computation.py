import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
import numpy as np
from skimage.segmentation import flood
from skimage.io import imread, imsave
from skimage.color import rgb2gray
from os.path import isfile
from os import makedirs
import json
import gc

def load_db(path):
	with open(path, "r") as file:
		db = json.load(file)
	return db

def save_db(db, path):
	with open(path, "w") as file:
		json.dump(db, file, indent=4)

def draw(
        x_seed: list,
        y_seed: list,
        random_seed: int,
        output_path: str,
        width: float,
        height: float,
        padding: float,
        dpi: int,
        border: bool
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
    ax1 = fig1.add_axes([(ratio * padding / 2),(ratio * padding / 2),(1 - (width_padding / round(fig_width * dpi))),(1 - (height_padding / round(fig_height * dpi)))], frameon=border)
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
        for j in range(0,len(y_seed)-1, 2):
            y1 = i
            y2 = i
            x1 = j + seed
            x2 = j + 1 + seed
            lines.append(((x1,y1), (x2,y2)))

    # Generate vertical lines
    for i in range(0,len(y_seed)):
        seed = y_seed[i]
        for j in range(0,len(x_seed)-1, 2):
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


    if border:
        plt.xlim((0,len(x_seed)-1))
        plt.ylim((0,len(y_seed)-1))
    else:
        plt.xlim((-1,len(x_seed)))
        plt.ylim((-1,len(y_seed)))

    plt.savefig(output_path + "/" + str(random_seed) + ".png", dpi = dpi)

    plt.cla()
    plt.clf()
    plt.close('all')
    plt.close(fig1)
    gc.collect()

def fill(cmap: str,
        rng: any,
        random_seed: int,
        pattern_path: str,
        output_path: str,
        background: str,
        save: bool):
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
    if background == "white":
        mask = []
        mask.append(flood(img_grey,(ind[0][0],ind[0][0]),tolerance=0.5))

        for item in mask:
            img_grey[item] = 0
            img[item] = (255,255,255,255)
            ind = np.where(img_grey > 0.5)

    # Each loop colors one patch
    loops = 0
    while len(ind[0]) > 0:
        mask = flood(img_grey,(ind[0][0],ind[1][0]),tolerance=0.5)
        color = my_cmap(rng.random(), bytes=True)[:4]
        img[mask] = color
        img_grey[mask] = 0
        ind = np.where(img_grey > 0.5)
        loops += 1

    # Save image
    if save:
        imsave(output_path + "/" + str(random_seed) + ".png", img)

    return loops

def main():
    s = 0
    o = "analysis/"
    width = 3.1
    height = 3.1
    padding = 0.04
    n = 500
    background = "white"

    # Paremeters of the binomial distribution
    x_dist = 0.5
    y_dist = 0.5

    steps = np.arange(10, 152, 2)
    num_loops = {}
    for item in steps:
        num_loops[str(item)] = {}

    if isfile("num_loops.json"):
        num_loops = load_db("num_loops.json")

    # Count number of loops
    print("Loops")
    for x in steps:
        if len(num_loops[str(x)]) > 0:
            continue
        print(x)
        for i in range(0,n):

            # Initialise seed for RNG
            if s ==0:
                seed_seq = np.random.SeedSequence()
            else:
                seed_seq = np.random.SeedSequence(s)

            rng = np.random.default_rng(seed_seq)

            #Get cmap
            cmap = "viridis"

            # Generate our seeds for our shape we are going to draw. These determine whether we will draw lines at even or odd coordinates.
            x_seed = rng.binomial(1, x_dist, x+1)
            y_seed = rng.binomial(1, y_dist, x+1)

            # Draw shape and fill
            # Output directory is the user specified relative path + the pattern or colored folder + the number of squares in the grid + the name of the colormap + the seeds number
            pattern_path = o + "/patterns/" + str(x) + "/" + cmap + "/"
            makedirs(pattern_path, exist_ok=True)
            draw(x_seed, y_seed, seed_seq.entropy, pattern_path, width, height, padding, 100, False)

            colored_path = o + "/colored/" + str(x) + "/" + cmap + "/"
            makedirs(colored_path, exist_ok=True)
            loops = fill(cmap, rng, seed_seq.entropy, pattern_path, colored_path, background, False)

            num_loops[str(x)][str(seed_seq.entropy)] = loops

        save_db(num_loops, "num_loops.json")


    num_regions = {}
    for item in steps:
        num_regions[str(item)] = {}

    if isfile("num_regions.json"):
        num_regions = load_db("num_regions.json")

    # Count number of regions
    print("Regions")
    for x in steps:
        if len(num_regions[str(x)]) > 0:
            continue
        print(x)
        for s in num_loops[str(x)]:
            if len(num_regions[str(x)]) == 0:
                 save = True
            else:
                 save = False

            # Initialise seed for RNG
            seed_seq = np.random.SeedSequence(int(s))

            rng = np.random.default_rng(seed_seq)

            #Get cmap
            cmap = "viridis"

            # Generate our seeds for our shape we are going to draw. These determine whether we will draw lines at even or odd coordinates.
            x_seed = rng.binomial(1, x_dist, x+1)
            y_seed = rng.binomial(1, y_dist, x+1)

            # Draw shape and fill
            # Output directory is the user specified relative path + the pattern or colored folder + the number of squares in the grid + the name of the colormap + the seeds number
            pattern_path = o + "/patterns/" + str(x) + "/" + cmap + "/"
            makedirs(pattern_path, exist_ok=True)
            draw(x_seed, y_seed, seed_seq.entropy, pattern_path, width, height, padding, 100, True)

            colored_path = o + "/colored/" + str(x) + "/" + cmap + "/"
            makedirs(colored_path, exist_ok=True)
            loops = fill(cmap, rng, seed_seq.entropy, pattern_path, colored_path, background, save)

            num_regions[str(x)][str(seed_seq.entropy)] = loops

        save_db(num_regions, "num_regions.json")


if __name__ == "__main__":
    main()