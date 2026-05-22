from PIL import Image, ImageFile
import numpy as np

number_of_colors = 14

def load_image(image : ImageFile.ImageFile):
    pix = np.array(image)

    out_data = np.zeros(pix.shape[0:2], dtype=int)

    # Predefined colors in image
    colors = np.array([
        [255, 255, 255,   0], # background
        [141, 100, 100, 255], # buildings
        [159, 181, 186, 255], # roads
        [126, 255, 126, 255], # grass
        [220, 220, 220, 255], # paths
        [110, 221,   0, 255], # shrubs
        [  0, 149,  37, 255], # fields
        [210, 200, 180, 255], # idk gray
        [184, 138,   0, 255], # dirt
        [  0, 126, 255, 255], # water
        [211, 187, 186, 255], # out buildings
        [139, 129, 129, 255], # walls
        [211, 203, 228, 255], # another gray
        [233, 38, 38, 255] # red x
    ])
    
    for i, color in enumerate(colors):
        out_data[np.all(pix == color, axis = -1)] = i
    
    return out_data

# TODO see if this can be asynchronous
class TerminalMap:
    def __init__(self, color_offset: int):
        self.data = load_image(Image.open('./Data/map_data.png'))
#        self.data, self.width, self.height = self.read_data(path)
#        self.data = [[ int(((x-25)**2 + (y-25)**2)**.5) % 8 for x in range(50)] for y in range(50)]
        self.color_offset = color_offset
        self.width, self.height = self.data.shape[0:2]

        self.window_width = 1
        self.window_height = 1

    def _get(self, x: int, y: int):
        if x < 0 or x >= self.height or y < 0 or y >= self.width:
            return None
            return -(y%2) # don't think about it to much
        return self.data[y, x]

    def get_data(self, x: int, y: int):
        # x, y are terminal coordinates
        # First convert to image coordinates
        x_ = x
        y_1 = y*2
        y_2 = y*2 + 1
        # Second scale the coordinates
        sx_ = (x - self.window_width) * self.scale
        sy_1 = (y_1 - self.window_height) * self.scale
        sy_2 = (y_2 - self.window_height) * self.scale

        # Third center
        map_x = round(self.center_x + sx_)
        map_y1 = round(self.center_y + sy_1)
        map_y2 = round(self.center_y + sy_2)

        return self._get(map_x, map_y1), self._get(map_x, map_y2)

    def get_color(self, x: int, y: int):
        top, bottom = self.get_data(x, y)
        if top is None or bottom is None:
            return self.color_offset - 1;
        return top * number_of_colors + bottom + self.color_offset

    def set_location(self, center_x: float, center_y: float, scale: float):
        self.center_x = center_x
        self.center_y = center_y
        self.scale = scale  # scale is zoom_scale, so actual scale = 1 / zoom_scale

    def set_window_size(self, width: int, height: int):
        self.window_width = width
        self.window_height = height * 2 # to make this the image height
