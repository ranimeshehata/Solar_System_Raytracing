import numpy as np

from ray_tracing.vectors import normalize


class Camera:
    def __init__(self, origin, width, height, aspect_ratio):
        self.origin = origin
        self.width = width
        self.height = height
        self.aspect_ratio = aspect_ratio
    
    def get_ray(self, x, y, dx=0.5, dy=0.5):
        u = ((x + dx) / self.width) * 2 - 1
        v = 1 - ((y + dy) / self.height) * 2
        u *= self.aspect_ratio
        direction = normalize(np.array([u, v, -1.0]))
        return (self.origin, direction)