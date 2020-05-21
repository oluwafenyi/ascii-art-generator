import os

import numpy as np
from PIL import Image, ImageFont, ImageDraw
from colour import Color


TEMP_FOLDER = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'temp')
if not os.path.exists(TEMP_FOLDER):
    os.mkdir(TEMP_FOLDER)

FONT = ImageFont.load_default()
CHAR_WIDTH, CHAR_HEIGHT = FONT.getsize('a')
ASCII_CHARS = np.asarray(
    [' ', '.', ',', ':', 'i', 'r', 's', '?', '@', '9', 'B', '#']
)
LEFT_TO_RIGHT = 'ltr'
TOP_TO_BOTTOM = 'ttb'


def resize_image(image: Image, scaling_factor: float = 0.5) -> Image:
    """
    function to rescale the image for pixel to character conversion
    :params image: PIL.Image
    :params scaling_factor: float 0 < x <= 1, adjusts scale and ascii quality
    :returns image: rescaled image
    :raises ValueError: if scaling_factor not in range
    """
    if not 0 < scaling_factor <= 1.0:
        raise ValueError(
            'scaling factor should be between 0 exclusive and 1 inclusive'
        )

    image_width, image_height = image.size
    char_ratio = CHAR_HEIGHT / CHAR_WIDTH
    rescale_width = round(image_width * scaling_factor * char_ratio)
    rescale_height = round(image_height * scaling_factor)
    image = image.resize((rescale_width, rescale_height))
    return image


def pixels_to_chars(image: Image, pixel_levity: float = 1.0) -> list:
    """
    function for pixel to character conversion
    :params image: PIL.Image
    :params pixel_levity: this darkens or lightens the image, where  > 1 is
        brighter and < 1 is darker
    :returns chars: list of strings
    """

    pixel_values = np.sum(np.asarray(image), axis=2)
    pixel_values -= pixel_values.min()
    pixel_values = (1.0 - pixel_values / pixel_values.max()) ** pixel_levity
    pixel_values = (pixel_values * (ASCII_CHARS.size - 1)).astype(int)
    chars = ('\n'.join(''.join(r) for r in ASCII_CHARS[pixel_values]))\
        .split('\n')
    return chars


def _draw_image_ttb(image: Image, chars: list, gradient: tuple) -> Image:
    """
    Internal function to draw ascii characters on white background.
    :params image: -> PIL.Image
    :params chars: -> list of rows of strings to be drawn
    :params gradient: -> list of colour.Color objects in gradient range
    :returns image: image is return after drawing process is complete
    """

    from_, to = gradient
    gradient_range = list(Color(from_).range_to(Color(to), len(chars)))

    draw = ImageDraw.Draw(image)
    cursor = 0
    for i, line in enumerate(chars):
        color = gradient_range[i]
        draw.text((0, cursor), line, color.hex, font=FONT)
        cursor += CHAR_HEIGHT
    return image


def _draw_image_ltr(image: Image, chars: list, gradient: tuple) -> Image:
    """
    Internal function to draw ascii characters on white background.
    gradient from left to right. Generally slower than its counterpart
    :params image: -> PIL.Image
    :params chars: -> list of rows of strings to be drawn
    :params gradient: -> list of colour.Color objects in gradient range
    :returns image: image is return after drawing process is complete
    """

    from_, to = gradient
    gradient_range = list(Color(from_).range_to(Color(to), len(chars[0])))

    draw = ImageDraw.Draw(image)

    cursor = 0
    for i, line in enumerate(chars):
        pix = 0
        cursor_x = 0
        for _, char in enumerate(line):
            try:
                color = gradient_range[pix]
            except IndexError:
                pix = 0
                color = gradient_range[pix]
            pix += 1
            draw.text((cursor_x, cursor), char, color.hex, font=FONT)
            cursor_x += CHAR_WIDTH
        cursor += CHAR_HEIGHT
    return image


def generate_image(
    path: str,
    scaling_factor: float = 0.5,
    pixel_levity: float = 1.0,
    gradient=('black', 'black'),
    gradient_style='ttb'
):
    """
    main function for image generation, picture is stored in a temp folder
    adjacent this script
    :params path: path to the image
    :params scaling_factor: float
    :params pixel_levity: float
    :params gradient: tuple of length two containing strings of color names or
        hex codes, same color in for solid color output
    :params gradient_style: of of ttb or ltr, meaning top to bottom and left to
        right respectively
    """

    if gradient_style not in ('ltr', 'ttb'):
        raise ValueError('gradient_style should be one of "ltr" or "ttb"')

    image = Image.open(path)
    image = resize_image(image, scaling_factor=scaling_factor)
    chars = pixels_to_chars(image, pixel_levity=pixel_levity)

    new_width, new_height = \
        CHAR_WIDTH * image.width, CHAR_HEIGHT * image.height
    new_image = Image.new('RGBA', (new_width, new_height), 'white')

    if gradient_style == 'ttb':
        new_image = _draw_image_ttb(new_image, chars, gradient)

    elif gradient_style == 'ltr':
        new_image = _draw_image_ltr(new_image, chars, gradient)

    new_image.save(os.path.join(TEMP_FOLDER, 'ascii_art.png'))
