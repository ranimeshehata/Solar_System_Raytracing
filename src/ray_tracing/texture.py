from PIL import Image
import numpy as np

class Texture:
    def value(self, u, v):
        pass

class SolidColor(Texture):
    def __init__(self, color):
        self.color = np.array(color, dtype=np.float32)
    
    def value(self, u, v):
        return self.color

class ImageTexture(Texture):
    def __init__(self, path):
        self.image = np.array(Image.open(path).convert("RGB"))
    
    def value(self, u, v):
        h, w, _ = self.image.shape
        tx = int(u * (w - 1))
        ty = int(v * (h - 1))
        return self.image[ty, tx].astype(np.float32)