import numpy as np
import math


class Sphere:
    def __init__(self, r, sectors=50, stacks=50):
        self.r = r
        self.sectors = sectors
        self.stacks = stacks

    def build_sphere_points(self):
        xy_coords, tex_coords = [], []

        theta_step = 2 * np.pi / self.sectors
        phi_step = np.pi / self.stacks

        for i in range(self.stacks + 1):
            phi = np.pi / 2 - i * phi_step
            xy = self.r * math.cos(phi)
            z = self.r * math.sin(phi)

            for j in range(self.sectors + 1):
                theta = j * theta_step
                x = xy * math.cos(theta)
                y = xy * math.sin(theta)

                xy_coords.extend([x, y, z])
                tex_coords.extend([j / self.sectors, i / self.stacks])
        return xy_coords, tex_coords

    def combine_coordinates(self, xy_coords, tex_coords):
        xy_coords = np.asarray(xy_coords, dtype=np.float32).reshape(-1, 3)
        tex_coords = np.asarray(tex_coords, dtype=np.float32).reshape(-1, 2)
        vertex_data = np.column_stack((xy_coords, tex_coords)).flatten().astype(np.float32)
        return vertex_data

    def build_indices(self):
        k1, k2 = 0, 0
        indices, lineIndices = [], []
        for i in range(self.stacks):
            k1 = i * (self.sectors + 1)
            k2 = k1 + self.sectors + 1

            for _ in range(self.sectors):
                if i != 0:
                    indices.append(k1)
                    indices.append(k2)
                    indices.append(k1 + 1)

                if i != (self.stacks - 1):
                    indices.append(k1 + 1)
                    indices.append(k2)
                    indices.append(k2 + 1)

                lineIndices.append(k1)
                lineIndices.append(k2)
                if i != 0:
                    lineIndices.append(k1)
                    lineIndices.append(k1 + 1)
                k1 += 1
                k2 += 1
        return indices, lineIndices
