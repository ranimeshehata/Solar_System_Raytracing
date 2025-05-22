import numpy as np

class Material:
    def __init__(self, texture, emissive=False, specular_strength=0.0, shininess=0):
        self.texture = texture
        self.emissive = emissive
        self.specular_strength = specular_strength
        self.shininess = shininess
    
    def emitted(self, u, v):
        if self.emissive:
            return self.texture.value(u, v) * 3
        else:
            return np.zeros(3, dtype=np.float32)