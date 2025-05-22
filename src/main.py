import pyrr
import glfw
import numpy as np
from OpenGL.GL import *
from camera.camera import CAMERA
from utils.json_parser import parse_json
from utils.window_renderer import WindowRenderer
from effects.skybox import SkyboxGL
from transformation.transformation import Transform
from effects.saturn_ring import SaturnRing


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
    ("Sun",     1.0,    "assets/texture/sun.png",           0.0,         0.0,         0.04),
    ("Mercury", 0.15,   "assets/texture/planets/mercury.png", 2.0,       4.15,        0.3),
    ("Venus",   0.18,   "assets/texture/planets/venus.png",   3.0,       1.62,        0.2),
    ("Earth",   0.20,   "assets/texture/planets/earth_nasa.png", 4.0,    1.0,         0.5),
    ("Mars",    0.17,   "assets/texture/planets/mars.png",     5.5,      0.53,        0.4),
    ("Jupiter", 0.40,   "assets/texture/planets/jupiter.png",  7.5,      0.08,        0.6),
    ("Saturn",  0.35,   "assets/texture/planets/saturn/saturn.png", 9.0, 0.03,        0.7),
    ("Uranus",  0.28,   "assets/texture/planets/uranus.png",  11.0,      0.011,       0.8),
    ("Neptune", 0.27,   "assets/texture/planets/neptune.png", 13.0,      0.006,       0.9),
    ("Moon",    0.07,   "assets/texture/moon.png",            0.5,       12.0,        1.0,             "Earth"),
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

    transform = Transform(data=PLANET_DATA, sectors=SECTORS, stacks=STACKS)

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
    use_solid_color_loc = glGetUniformLocation(renderer.shader, "useSolidColor")
    solid_color_loc = glGetUniformLocation(renderer.shader, "solidColor")

    glUniformMatrix4fv(projection_loc, 1, GL_FALSE, projection)
    glEnable(GL_DEPTH_TEST)

    glfw.set_input_mode(renderer.window, glfw.STICKY_KEYS, GL_TRUE)

    # --- Use TIME from JSON as simulation start time ---
    start_time = TIME

    def window_size_callback(window, width, height):
        global WINDOW_H, WINDOW_W
        glViewport(0, 0, width, height)
        WINDOW_W = width
        WINDOW_H = height

    glfw.set_window_size_callback(renderer.window, window_size_callback)

    while not glfw.window_should_close(renderer.window):
        glfw.poll_events()
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # Set Camera Position
        camera.position_camera(view_loc)

        # Draw skybox first
        glDepthMask(GL_FALSE)
        glDepthFunc(GL_LEQUAL)
        skybox.draw(camera.get_view_matrix(), projection)
        glDepthMask(GL_TRUE)
        glDepthFunc(GL_LESS)

        # Draw orbits
        transform.place_orbits(
            renderer.shader, use_solid_color_loc, solid_color_loc, model_loc
        )

        # Use simulation time
        time_elapsed = start_time + glfw.get_time()

        # Draw planets
        transform.place_planets(
            time_elapsed,
            model_loc,
            use_solid_color_loc,
            solid_color_loc,
            renderer.shader,
        )

        glfw.swap_buffers(renderer.window)
    glfw.terminate()


if __name__ == "__main__":
    main()
