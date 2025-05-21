import numpy as np

from ray_tracing.vectors import get_sphere_uv, normalize


class HitRecord:
    def __init__(self, t, point, normal, sphere, u, v):
        self.t = t
        self.point = point
        self.normal = normal
        self.sphere = sphere
        self.u = u
        self.v = v

class Sphere:
    def __init__(self, center, radius, material):
        self.center = np.array(center, dtype=np.float32)
        self.radius = radius
        self.material = material
    
    def hit(self, ray_origin, ray_dir):
        oc = ray_origin - self.center
        a = np.dot(ray_dir, ray_dir)
        b = 2.0 * np.dot(oc, ray_dir)
        c = np.dot(oc, oc) - self.radius**2
        discriminant = b**2 - 4 * a * c
        if discriminant < 0:
            return None
        sqrtd = np.sqrt(discriminant)
        roots = [(-b - sqrtd) / (2 * a), (-b + sqrtd) / (2 * a)]
        valid_roots = [t for t in roots if t > 1e-4]
        if not valid_roots:
            return None
        t = min(valid_roots)
        point = ray_origin + t * ray_dir
        normal = normalize(point - self.center)
        u, v = get_sphere_uv(normal)
        return HitRecord(t, point, normal, self, u, v)