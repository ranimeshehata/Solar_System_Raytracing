import numpy as np

class Material:
    def __init__(self, texture, 
                 emissive=False, 
                 specular_strength=0.5, 
                 shininess=32,
                 halo=False,
                 halo_size=1.0,
                 halo_strength=1.0,
                 glow_radius=0.2,
                 reflectivity=0.1,
                 rim_power=4.0):
        """
        parameters:
        - texture: the base texture/color
        - emissive: whether the material emits light
        - specular_strength: intensity of specular highlights 
        - shininess: controls how shiny the object is under the specular light
        - halo: whether to show a halo effect
        - halo_size: size of the halo
        - halo_strength: intensity of the halo effect
        - glow_radius: radius of the glow around emissive objects
        - reflectivity: amount of environment reflection
        - rim_power: rim lighting effect backlight used behind the sun 
        """
        self.texture = texture
        self.emissive = emissive
        self.specular_strength = specular_strength
        self.shininess = shininess
        self.halo = halo
        self.halo_size = halo_size
        self.halo_strength = halo_strength
        self.glow_radius = glow_radius
        self.reflectivity = reflectivity
        self.rim_power = rim_power
    
    def emitted(self, u, v):
        if not self.emissive:
            return np.zeros(3, dtype=np.float32)

        base_color = self.texture.value(u, v)
        if isinstance(base_color, (list, tuple)):
            base_color = np.array(base_color, dtype=np.float32)
        
        # halo effect gets warm color and increased instensity
        emission = base_color*np.array([2.2,1.6,1.2], dtype=np.float32)*self.halo_strength
        return np.clip(emission, 0, 255)
    
    