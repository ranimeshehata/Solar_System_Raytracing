import glfw
from OpenGL.GL import *
from utils.window_renderer import WindowRenderer
from objects.planet import Planet
import numpy as np
import pyrr
from PIL import Image

# constants
WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 800
WINDOW_X = 800
WINDOW_Y = 300
WINDOW_TITLE = "Solar System Raytracing"
SECTORS = 36
STACKS = 18


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

    glUseProgram(renderer.shader)
    view = pyrr.matrix44.create_look_at(
        eye=np.array([0.0, 0.0, 3.0]),
        target=np.array([0.0, 0.0, 0.0]),
        up=np.array([0.0, 1.0, 0.0]),
        dtype=np.float32,
    )

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

    glUniformMatrix4fv(view_loc, 1, GL_FALSE, view)
    glUniformMatrix4fv(projection_loc, 1, GL_FALSE, projection)
    glEnable(GL_DEPTH_TEST)

    while not glfw.window_should_close(renderer.window):
        glfw.poll_events()
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        model_matrix = pyrr.matrix44.create_identity(dtype=np.float32)
        venus.draw(model_loc, model_matrix, glfw.get_time())

        glfw.swap_buffers(renderer.window)

    glfw.terminate()


if __name__ == "__main__":
    main()
