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
    
class Ring:
    def __init__(self, center, inner_radius, outer_radius, material):
        self.center = np.array(center, dtype=np.float32)
        self.inner_radius = inner_radius
        self.outer_radius = outer_radius
        self.material = material
        self.normal = np.array([0, 1, 0], dtype=np.float32) 
        
    def hit(self, ray_origin, ray_dir):
        # checking of intersection with the ring plane first
        denom = np.dot(self.normal, ray_dir)
        if abs(denom) < 1e-6:
            return None 
            
        t = np.dot(self.center - ray_origin, self.normal) / denom
        if t < 1e-4:
            return None  # behind the ray origin
            
        point = ray_origin + t * ray_dir
        dist_sq = np.sum((point - self.center)**2)
        
        if self.inner_radius**2 <= dist_sq <= self.outer_radius**2:
            u = (np.arctan2(point[2] - self.center[2], point[0] - self.center[0]) / (2 * np.pi) + 0.5)
            v = (np.linalg.norm(point - self.center) - self.inner_radius) / (self.outer_radius - self.inner_radius)
            return HitRecord(t, point, self.normal, self, u, v)
        return None
