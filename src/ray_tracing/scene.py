class Scene:
    def __init__(self, spheres, light):
        self.spheres = spheres
        self.light = light  
    
    def hit(self, ray_origin, ray_dir):
        closest_hit = None
        closest_t = float('inf')
        for sphere in self.spheres:
            hit_rec = sphere.hit(ray_origin, ray_dir)
            if hit_rec and hit_rec.t < closest_t:
                closest_t = hit_rec.t
                closest_hit = hit_rec
        return closest_hit