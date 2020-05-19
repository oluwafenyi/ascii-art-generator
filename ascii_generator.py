import math
from PIL import Image


ASCII_CHARS = ['.', ':', '░', '▒', '▓', '█', '▄', '▅', '▆', '▉', '▉']


def resize_image(image: Image, new_width=100) -> Image:
    width, height = image.size
    aspect_ratio = height / width
    new_height = math.ceil(new_width * aspect_ratio)
    new_image = image.resize((new_width, new_height))
    return new_image


def pixels_to_chars(image: Image, range_width=25) -> list:
    pixels = list(image.getdata())
    chars = [ASCII_CHARS[value // range_width] for value in pixels]
    return chars


def generate_ascii_image(image_path: str, desired_width=100, range_width=25) \
        -> str:
    original = Image.open(image_path)
    image = original.copy()
    image = resize_image(image, new_width=desired_width)
    image = image.convert('L')
    chars = pixels_to_chars(image, range_width=range_width)

    image_ascii = [''.join(chars[index: index + desired_width]) for index in
                   range(0, len(chars), desired_width)]
    return '\n'.join(image_ascii)
