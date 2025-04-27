# Hitomezashi patterns

<p align="center"><img src="https://raw.githubusercontent.com/SamuelSchwab/hitomezashi/main/README.png"/></p>

Draws and colors hitomezashi patterns in square, isometric, and polar grids.

Will generate a pattern, saved in the `patterns` folder, and a colored image, saved in the `colored` folder.

Images are saved at 100 dots per inch and named after the seed numbers used to initialize the random number generation. Patterns can be recreated by using these seed numbers in the `-s` argument.

## Install

Create a conda environment using the `requirements.txt` file:

`conda create --name hitomezashi --file requirements.txt`

Activate the environment and run one of the three scripts:

```
conda activate hitomezashi
python square.py
```

## Square patterns

`square.py` generates and colors square hitomezashi patterns.

The size of the hitomezashi pattern is dependent on the `--height` and `--width` arguments;
A width and height of 10 inches will result in a hitomezashi pattern of 1000 pixels.

Ideally, the total amount of pixels in the patterns is a multiple of the number of squares in the pattern. Otherwise, some squares are larger than others in the pattern.

Padding is added with the `--padding` argument. A hitomezashi pattern with a width and height of 10 inches (=1000 pixels) and a padding value of 0.02 (=2%) will have 20 pixels of padding added to the figure in the y and x dimensions, resulting in a final figure of 1021x1021 (1 pixel is always added to draw the border around the hitomezashi pattern).

### Arguments
    -n                       Generate n numbers to hitomezashi patterns. (default: 1)
    -x                       The number of squares (width/height) in the hitomezashi grid. (default: 100)
    -c                       Colormap to draw colors from. (default: all)
    -o                       Relative path to save the images to. (default: square/)
    -s                       Seed Number. 0 will create a psuedorandom seed number. (default: 0)
    --width                  Figure width in inches. (default: 10)
    --height                 Figure height in inches. (default: 10)
    --padding                Percentage (from 0 to 1) of the figure height/width which is added aspadding. (default: 0.04)

## Isometric patterns

`iso.py` generates and colors isometric hitomezashi patterns.

The isometric images are generated at twice (as specified by the `-downscale` argument) their specified size, downsampled down to the specified size, and then saved. This is done to make the diagonal lines prettier. However, this also increases computation time (for the flood fill function specifically).

### Arguments
    -n                       Generate n numbers to hitomezashi patterns. (default: 1)
    -x                       The number of triangles (width/height) in the hitomezashi grid. (default: 100)
    -c                       Colormap to draw colors from. (default: all)
    -o                       Relative path to save the images to. (default: iso/)
    -s                       Seed Number. 0 will create a psuedorandom seed number. (default: 0)
    --width                  Figure width in inches. (default: 10)
    --height                 Figure height in inches. (default: 10)
    --background             'transparent' or 'colored' background. (default: transparent)
    --downscale              Factor by which to downscale the final image. To disable downscale, enter a value of 1. (default: 2)

## Polar patterns

`polar.py` generates and colors polar hitomezashi patterns.

The number of inner circles and radial lines in the polar grid are specified by the `-x1` and `-x2` arguments respectively. Ideally, an odd number of radial lines are specified for the pattern to perfectly loop back on itself.

Like the isometric images, the polar images are also downscaled.

### Arguments
    -n                       Generate n numbers to hitomezashi patterns. (default: 1)
    -x1                      The number of circles in the hitomezashi grid. (default: 50)
    -x2                      The number of radials in the hitomezashi grid. Best to use an odd number. (default: 99)
    -c                       Colormap to draw colors from. (default: all)
    -o                       Relative path to save the images to. (default: polar/)
    -s                       Seed Number. 0 will create a psuedorandom seed number. (default: 0)
    --skip                   Which inner circles to skip in the hitomezashi grid. Inner most circle is '0'. Can specify multiple circles (e.g. 0,1,2,etc.). (default: 0)
    --width                  Figure width in inches. (default: 5)
    --height                 Figure height in inches. (default: 5)
    --background             'transparent' or 'colored' background. (default: transparent)
    --downscale              Factor by which to downscale the final image. To disable downscale, enter a value of 1. (default: 2)

## Colormaps

Colors get drawn from colormaps. All [matplotlib colormaps](https://matplotlib.org/stable/users/explain/colors/colormaps.html) are supported as well as [metbrewer colormaps](https://github.com/BlakeRMills/MetBrewer).

For the matplotlib colormaps, it is possible to draw randomly from a specific type of colormap with the `-c` argument: uniform, sequential, sequential2, diverging, cyclic, qualitative, and misc.

To use a random metbrewer colormap, use `metbrewer` for the `-c` argument.