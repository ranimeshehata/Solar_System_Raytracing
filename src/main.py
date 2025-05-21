import pyrr
import glfw
import numpy as np
from OpenGL.GL import *
from camera.camera import CAMERA
from objects.planet import Planet
from utils.json_parser import parse_json
from utils.window_renderer import WindowRenderer
from effects.skybox import SkyboxGL
from objects.orbit import Orbit

# constants
WINDOW_WIDTH = 1920
WINDOW_HEIGHT = 1020
WINDOW_X = 0
WINDOW_Y = 30
WINDOW_TITLE = "Solar System Raytracing"
SECTORS = 36
STACKS = 18

# Load scene configuration from JSON
TIME, CAMERA_EYE, CAMERA_TARGET, CAMERA_UP = parse_json()

PLANET_DATA = [
    # name,      radius, texture,                           orbit_radius, orbit_speed, rotation_speed, parent
    ("Sun",     1.0,    "assets/texture/sun.png",           0.0,         0.0,         0.1),
    ("Mercury", 0.15,   "assets/texture/planets/mercury.png", 2.0,       4.15,        0.3),
    ("Venus",   0.18,   "assets/texture/planets/venus.png",   3.0,       1.62,        0.2),
    ("Earth",   0.20,   "assets/texture/planets/earth_nasa.png", 4.0,    1.0,         0.5),
    ("Mars",    0.17,   "assets/texture/planets/mars.png",     5.5,      0.53,        0.4),
    ("Jupiter", 0.40,   "assets/texture/planets/jupiter.png",  7.5,      0.08,        0.6),
    ("Saturn",  0.35,   "assets/texture/planets/saturn/saturn.png", 9.0, 0.03,        0.7),
    ("Uranus",  0.28,   "assets/texture/planets/uranus.png",  11.0,      0.011,       0.8),
    ("Neptune", 0.27,   "assets/texture/planets/neptune.png", 13.0,      0.006,       0.9),
    ("Moon",    0.07,   "assets/texture/moon.png",            0.5,       12.0,        1.0, "Earth"),
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
    
    # --- Initialize the planets and orbits ---
    planets = []
    orbits = []
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
        
        # Add orbit for planets that orbit the sun (not the sun itself or moons)
        if orbit_radius > 0 and parent is None:
            orbits.append(Orbit(orbit_radius))
    
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

    # --- Use TIME from JSON as simulation start time ---
    start_time = TIME
    
    while not glfw.window_should_close(renderer.window):
        glfw.poll_events()
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # Draw skybox first
        glDepthMask(GL_FALSE)
        glDepthFunc(GL_LEQUAL)
        skybox.draw(camera.get_view_matrix(), projection)
        glDepthMask(GL_TRUE)
        glDepthFunc(GL_LESS)
        
        glUseProgram(renderer.shader)
        camera.position_camera(view_loc)

        use_solid_color_loc = glGetUniformLocation(renderer.shader, "useSolidColor")
        solid_color_loc = glGetUniformLocation(renderer.shader, "solidColor")

        glUniform1i(use_solid_color_loc, 1)  # Enable solid color
        glUniform3f(solid_color_loc, 0.6235, 0.6314, 0.6235)
        
        for planet, orbit in zip(planets, orbits):
            if planet.name == "Moon":
                
                # Find Earth's current position
                earth = next(p for p in planets if p.name == "Earth")
                earth_angle = earth.orbit_speed * time_elapsed
                earth_pos = np.array([
                    earth.orbit_radius * np.cos(earth_angle),
                    0,
                    earth.orbit_radius * np.sin(earth_angle)
                ])
                
                # Create translation matrix for Moon's orbit
                model = pyrr.matrix44.create_from_translation(earth_pos)
                orbit.draw(model_loc, model)
            else:
                # Draw normal orbits centered at the Sun
                orbit.draw(model_loc)
        
        # Draw orbits
        for orbit in orbits:
            orbit.draw(model_loc)

        glUniform1i(use_solid_color_loc, 0)  # Restore to textured mode for planets

        # Draw planets
        glUseProgram(renderer.shader)
        camera.position_camera(view_loc)
        model_matrix = pyrr.matrix44.create_identity(dtype=np.float32)
        # Use simulation time
        time_elapsed = start_time + glfw.get_time()
        
        
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
            planet.draw(model_loc, model_matrix, time_elapsed, planet.rotation_speed)
            
            # --- Draw atmosphere for Earth ---
            if planet.name == "Earth":
                glUseProgram(renderer.shader)
                camera.position_camera(view_loc)
                glUniform1i(use_solid_color_loc, 1)  # Enable solid color
                glUniform3f(solid_color_loc, 0.8, 0.9, 1.0)  # Light blue
                planet.draw_atmosphere(model_loc, model_matrix)
                glUniform1i(use_solid_color_loc, 0)  # Restore to textured mode
        
        
        glfw.swap_buffers(renderer.window)
    glfw.terminate()

if __name__ == "__main__":
    main()
