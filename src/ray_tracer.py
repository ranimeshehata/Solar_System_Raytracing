import os
import numpy as np
from PIL import Image
from tqdm import tqdm
from camera.camera import CAMERA
from ray_tracing.material import Material
from ray_tracing.ray import ray_color
from ray_tracing.scene import Scene
from ray_tracing.sphere import Ring, Sphere
from ray_tracing.texture import ImageTexture
from scene_builder import PLANET_DATA, get_camera_config, calculate_planet_position, build_planet_dict
from utils.generate_video import generate_video_from_frames

WIDTH = 1000
HEIGHT = 300
SAMPLES_PER_PIXEL = 3
AMBIENT = 0.01  
MAX_DEPTH = 3      
TIME_STEP = 0.1         
TOTAL_FRAMES = 50       
FRAME_IDX = 0       

def render_frame(time, frame_idx, output_dir, eye, target, up):
    planets_dict = build_planet_dict()
    camera = CAMERA(None, 
                  camera_eye=eye, 
                  camera_target=target, 
                  camera_up=up, 
                  width=WIDTH, 
                  height=HEIGHT)

    
    spheres = []
    rings = [] 
    
    for pdata in PLANET_DATA:
        pos = calculate_planet_position(pdata, time, planets_dict)
        name, radius, texture_path = pdata[0], pdata[1], pdata[2]
        tex = ImageTexture(texture_path)
        
        if name == "Sun":
            mat = Material(
                tex,
                emissive=True,
                specular_strength=0.0,
                shininess=0,
                halo=True,
                halo_size=8.0,
                halo_strength=1.5
            )
        else:
            mat = Material(
                tex,
                emissive=(name == "Sun"),
                specular_strength=0.4,
                shininess=64
            )
        spheres.append(Sphere(pos, radius, mat))
        
        if name == "Saturn":
            ring_texture = ImageTexture("assets/texture/planets/saturn/saturn ring.png")
            ring_mat = Material(
                ring_texture,
                emissive=False,
                specular_strength=0.2,
                shininess=32
            )
            rings.append(Ring(
                center=pos,
                inner_radius=radius * 1.5,
                outer_radius=radius * 2.5,
                material=ring_mat
            ))

    # texture for the background
    sky_texture = ImageTexture("assets/texture/space.png")
    
    # light source : sun
    light_sphere = next(s for s in spheres if s.material.emissive)
    
    # scene creation with rings
    scene = Scene(spheres, light_sphere, rings=rings, background_texture=sky_texture)

    # initializing the image buffer
    image = np.zeros((HEIGHT, WIDTH, 3), dtype=np.float32)
    
    # render loop
    for y in tqdm(range(HEIGHT), desc=f"Rendering frame {frame_idx}", leave=False):
        for x in range(WIDTH):
            color = np.zeros(3, dtype=np.float32)
            for _ in range(SAMPLES_PER_PIXEL):
                dx, dy = np.random.rand(2)
                ro, rd = camera.get_ray(x, y, dx, dy)
                # calculating pixel color
                color += ray_color(ro, rd, scene, AMBIENT, MAX_DEPTH, 0)
                
            # averaging over all samples
            image[y, x] = color / SAMPLES_PER_PIXEL
    image = (np.clip(image / 255, 0, 1) ** (1/2.2) * 255).astype(np.uint8)
    
    filename = f"{output_dir}/frame_{frame_idx:04d}.png"
    Image.fromarray(image).save(filename)
    print(f"Saved frame {frame_idx} to {filename}")

def main():
    print("Ray Tracing Solar System")
    print("1. Render a single frame")
    print("2. Render a full video")
    choice = input("Enter choice [1-2]: ").strip()

    output_dir = "frames"
    video_dir = "video"
    video_filename = "solar_system.mp4"
    video_path = os.path.join(video_dir, video_filename)

    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(video_dir, exist_ok=True)

    config_time, eye, target, up = get_camera_config()

    if choice == "1":
        render_frame(config_time, FRAME_IDX, output_dir, eye, target, up)

    elif choice == "2":
        for i in range(TOTAL_FRAMES):
            current_time = config_time + i * TIME_STEP
            render_frame(current_time, i, output_dir, eye, target, up)
        generate_video_from_frames(output_dir, video_path)
        print(f"Video saved to: {video_path}")

    else:
        print("Invalid choice. Please enter 1 or 2.")

if __name__ == "__main__":
    main()

