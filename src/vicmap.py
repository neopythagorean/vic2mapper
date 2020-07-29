
from PIL import Image

blank_map = None
pixel_map = None

MAP_W = 5616
MAP_H = 2160

def load_map(location):
    global blank_map
    global pixel_map
    blank_map = Image.open(location)
    pixel_map = blank_map.load()