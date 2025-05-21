import numpy as np
from PIL import Image
from pyrr import Vector3
from tqdm import tqdm  


from camera.camera import CAMERA
from ray_tracing.material import Material
from ray_tracing.ray import ray_color
from ray_tracing.scene import Scene
from ray_tracing.sphere import Sphere
from ray_tracing.texture import ImageTexture
from utils.json_parser import parse_json


def main():
    width, height = 400, 300
    samples_per_pixel = 4  
    ambient = 0.1
    # load configurations of the scene scene
    time, camera_eye, camera_target, camera_up = parse_json()
    camera = CAMERA(
        window=None,  
        camera_eye=camera_eye,
        camera_target=camera_target,
        camera_up=camera_up,
        width=width,  
        height=height
    )
    
    max_depth = 5

    # loading textures
    earth_tex = ImageTexture("assets/texture/planets/earth_nasa.png")
    venus_tex = ImageTexture("assets/texture/planets/venus.png")
    sun_tex = ImageTexture("assets/texture/sun.png")

    # materials
    earth_mat = Material(earth_tex, specular_strength=0.3, shininess=32)
    venus_mat = Material(venus_tex, specular_strength=0.4, shininess=64)
    sun_mat = Material(sun_tex, emissive=True)

    # scene
    light_sphere = Sphere([1.0, 20.0, -5.0], 20, sun_mat)
    spheres = [
        Sphere([-7.0, -28.0, -5.0], 10, earth_mat),
        Sphere([10.0, -12.0, -5.0], 7, venus_mat),
        light_sphere
    ]
    scene = Scene(spheres, light_sphere)

    # initializing the output image 
    image = np.zeros((height, width, 3), dtype=np.float32)

    # render loop
    for y in tqdm(range(height), desc="Rendering rows"):  
        for x in range(width):
            color = np.zeros(3, dtype=np.float32)
            
            for _ in tqdm(range(samples_per_pixel), 
                        desc=f"Pixel ({x},{y})", 
                        leave=False,  
                        disable=(samples_per_pixel < 50)):  
                dx, dy = np.random.rand(2)
                ro, rd = camera.get_ray(x, y, dx, dy)
                color += ray_color(ro, rd, scene, ambient, max_depth, depth=0)
            
            image[y, x] = color / samples_per_pixel

    image = (np.clip(image / 255, 0, 1) ** (1/2.2) * 255).astype(np.uint8)
    Image.fromarray(image).save("out.png")

main()