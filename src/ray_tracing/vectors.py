import numpy as np
import numpy.random as random

def normalize(v):
    norm = np.linalg.norm(v)
    return v / norm if norm > 0 else v

def reflect(v, normal):
    return v - 2 * np.dot(v, normal) * normal

def random_point_on_sphere(center, radius):
    theta = random.uniform(0, 2 * np.pi)
    phi = np.arccos(1 - 2 * random.uniform(0, 1))
    x = radius * np.sin(phi) * np.cos(theta)
    y = radius * np.sin(phi) * np.sin(theta)
    z = radius * np.cos(phi)
    return center + np.array([x, y, z])

def get_sphere_uv(normal):
    x, y, z = normal
    u = 0.5 + np.arctan2(z, x) / (2 * np.pi)
    v = 0.5 - np.arcsin(y) / np.pi
    return u, v