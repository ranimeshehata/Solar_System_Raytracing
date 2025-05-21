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
WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 800
WINDOW_X = 800
WINDOW_Y = 300
WINDOW_TITLE = "Solar System Raytracing"
SECTORS = 36
STACKS = 18
TIME, CAMERA_EYE, CAMERA_TARGET, CAMERA_UP = parse_json()


def main():
    renderer = WindowRenderer(
        window_w=WINDOW_WIDTH,
        window_h=WINDOW_HEIGHT,
        window_x=WINDOW_X,
        window_y=WINDOW_Y,
        window_title=WINDOW_TITLE,
    )
    renderer.create_shader()

    venus = Planet(
        r=0.5,
        texture_path="assets/texture/planets/earth_nasa.png",
        sectors=SECTORS,
        stacks=STACKS,
        rotation_speed=0.5,
    )

    camera = CAMERA(renderer.window, CAMERA_EYE, CAMERA_TARGET, CAMERA_UP)

    # --- Initialize the skybox ---
    skybox = SkyboxGL("assets/texture/sky/skyfield.png")
    
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
        venus.draw(model_loc, model_matrix, glfw.get_time())

        glfw.swap_buffers(renderer.window)
    glfw.terminate()


if __name__ == "__main__":
    main()
