import pyrr
import glfw
import numpy as np
from OpenGL.GL import *
from camera.camera import CAMERA
from objects.planet import Planet
from utils.json_parser import parse_json
from utils.window_renderer import WindowRenderer
from effects.skybox import SkyboxGL

# constants
WINDOW_WIDTH = 1920
WINDOW_HEIGHT = 1020
WINDOW_X = 0
WINDOW_Y = 30
WINDOW_TITLE = "Solar System Raytracing"
SECTORS = 36
STACKS = 18
TIME, CAMERA_EYE, CAMERA_TARGET, CAMERA_UP = parse_json()

PLANET_DATA = [
    # name, radius, texture, orbit_radius, orbit_speed, rotation_speed
    ("Sun",     0.7, "assets/texture/sun.png", 0.0, 0.0, 0.0),
    ("Mercury", 0.1, "assets/texture/planets/mercury.png", 2.0, 4.15, 0.3),
    ("Venus",   0.15, "assets/texture/planets/venus.png", 3.0, 1.62, 0.2),
    ("Earth",   0.5, "assets/texture/planets/earth_nasa.png", 5.0, 1.0, 0.5),
    ("Mars",    0.18, "assets/texture/planets/mars.png", 7.0, 0.53, 0.4),
    ("Jupiter", 0.3, "assets/texture/planets/jupiter.png", 10.0, 0.08, 0.6),
    ("Saturn",  0.25, "assets/texture/planets/saturn/saturn.png", 13.0, 0.03, 0.7),
    ("Uranus",  0.2, "assets/texture/planets/uranus.png", 16.0, 0.011, 0.8),
    ("Neptune", 0.15, "assets/texture/planets/neptune.png", 19.0, 0.006, 0.9),
    # Example for the Moon (orbits Earth)
    ("Moon", 0.05, "assets/texture/moon.png", 0.8, 12.0, 1.0, "Earth"),
]


def main():
    renderer = WindowRenderer(
        window_w=WINDOW_WIDTH,
        window_h=WINDOW_HEIGHT,
        window_x=WINDOW_X,
        window_y=WINDOW_Y,
        window_title=WINDOW_TITLE,
    )
    renderer.create_shader()
    
    # --- Initialize the planets ---
    planets = []
    for data in PLANET_DATA:
        if len(data) == 7:
            name, r, texture, orbit_radius, orbit_speed, rotation_speed, parent = data
        else:
            name, r, texture, orbit_radius, orbit_speed, rotation_speed = data
            parent = None
        planet = Planet(
            r=r,
            texture_path=texture,
            sectors=SECTORS,
            stacks=STACKS,
            rotation_speed=rotation_speed,
            orbit_radius=orbit_radius,
            orbit_speed=orbit_speed,
            parent=parent
        )
        planet.name = name
        planets.append(planet)
    
    camera = CAMERA(renderer.window, CAMERA_EYE, CAMERA_TARGET, CAMERA_UP)

    # --- Initialize the skybox ---
    skybox = SkyboxGL("assets/texture/space.png")
    
    glUseProgram(renderer.shader)

    projection = pyrr.matrix44.create_perspective_projection(
        fovy=45.0,
        aspect=WINDOW_WIDTH / WINDOW_HEIGHT,
        near=0.1,
        far=100.0,
        dtype=np.float32,
    )

    view_loc = glGetUniformLocation(renderer.shader, "view")
    projection_loc = glGetUniformLocation(renderer.shader, "projection")
    model_loc = glGetUniformLocation(renderer.shader, "model")

    glUniformMatrix4fv(projection_loc, 1, GL_FALSE, projection)
    glEnable(GL_DEPTH_TEST)

    glfw.set_input_mode(renderer.window, glfw.STICKY_KEYS, GL_TRUE)

    while not glfw.window_should_close(renderer.window):
        glfw.poll_events()
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # Draw skybox first
        glDepthMask(GL_FALSE)
        glDepthFunc(GL_LEQUAL)
        skybox.draw(camera.get_view_matrix(), projection)
        glDepthMask(GL_TRUE)
        glDepthFunc(GL_LESS)

        # Draw planets
        glUseProgram(renderer.shader)
        camera.position_camera(view_loc)
        model_matrix = pyrr.matrix44.create_identity(dtype=np.float32)
        time_elapsed = glfw.get_time()
        for planet in planets:
            if planet.parent == "Earth":
                # Moon orbits Earth
                earth = next(p for p in planets if p.name == "Earth")
                earth_angle = earth.orbit_speed * time_elapsed
                earth_pos = np.array([
                    earth.orbit_radius * np.cos(earth_angle),
                    0,
                    earth.orbit_radius * np.sin(earth_angle)
                ])
                moon_angle = planet.orbit_speed * time_elapsed
                moon_pos = earth_pos + np.array([
                    planet.orbit_radius * np.cos(moon_angle),
                    0,
                    planet.orbit_radius * np.sin(moon_angle)
                ])
                pos = moon_pos
            else:
                angle = planet.orbit_speed * time_elapsed
                pos = np.array([
                    planet.orbit_radius * np.cos(angle),
                    0,
                    planet.orbit_radius * np.sin(angle)
                ])
            model_matrix = pyrr.matrix44.create_from_translation(pos)
            planet.draw(model_loc, model_matrix, time_elapsed)

        glfw.swap_buffers(renderer.window)
    glfw.terminate()

if __name__ == "__main__":
    main()
