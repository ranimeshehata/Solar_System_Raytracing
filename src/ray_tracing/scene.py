class Scene:
    def __init__(self, spheres, light, rings=None, background_texture=None):
        self.spheres = spheres
        self.rings = rings if rings else []
        self.light = light  
        self.background_texture = background_texture
        
    def hit(self, ray_origin, ray_dir):
        closest_hit = None
        closest_t = float('inf')
        
        # spheres
        for sphere in self.spheres:
            hit_rec = sphere.hit(ray_origin, ray_dir)
            if hit_rec and hit_rec.t < closest_t:
                closest_t = hit_rec.t
                closest_hit = hit_rec
                
        # rings
        for ring in self.rings:
            hit_rec = ring.hit(ray_origin, ray_dir)
            if hit_rec and hit_rec.t < closest_t:
                closest_t = hit_rec.t
                closest_hit = hit_rec
                
        return closest_hit