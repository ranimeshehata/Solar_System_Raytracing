import numpy as np
from PIL import Image
from tqdm import tqdm
from camera.camera import CAMERA
from ray_tracing.material import Material
from ray_tracing.ray import ray_color
from ray_tracing.scene import Scene
from ray_tracing.sphere import Sphere
from ray_tracing.texture import ImageTexture
from scene_builder import PLANET_DATA, get_camera_config, calculate_planet_position, build_planet_dict

def main():
    width, height = 1000, 800
    samples_per_pixel = 4
    ambient = 0.1
    max_depth = 5

    time, eye, target, up = get_camera_config()
    planets_dict = build_planet_dict()

    camera = CAMERA(None,camera_eye=eye,camera_target=target,camera_up=up,width=width,height=height)
    spheres = []
    for pdata in PLANET_DATA:
        pos = calculate_planet_position(pdata, time, planets_dict)
        name, radius, texture_path = pdata[0], pdata[1], pdata[2]
        tex = ImageTexture(texture_path)
        mat = Material(tex, emissive=(name == "Sun"), specular_strength=0.3, shininess=32)
        spheres.append(Sphere(pos, radius, mat))

    light_sphere = next(s for s in spheres if s.material.emissive)

    scene = Scene(spheres, light_sphere)

    image = np.zeros((height, width, 3), dtype=np.float32)

    for y in tqdm(range(height), desc="Rendering rows"):
        for x in range(width):
            color = np.zeros(3, dtype=np.float32)
            for _ in range(samples_per_pixel):
                dx, dy = np.random.rand(2)
                ro, rd = camera.get_ray(x, y, dx, dy)
                color += ray_color(ro, rd, scene, ambient, max_depth, 0)
            image[y, x] = color / samples_per_pixel

    image = (np.clip(image / 255, 0, 1) ** (1/2.2) * 255).astype(np.uint8)
    Image.fromarray(image).save("out.png")

if __name__ == "__main__":
    main()
