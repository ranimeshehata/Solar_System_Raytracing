import glfw
from OpenGL.GL import *
from utils.window_renderer import WindowRenderer

# constants
WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 800
WINDOW_X = 800
WINDOW_Y = 300
WINDOW_TITLE = "Solar System Raytracing"

def main():
    renderer = WindowRenderer(window_w=WINDOW_WIDTH, window_h=WINDOW_HEIGHT, window_x=WINDOW_X, window_y=WINDOW_Y, window_title=WINDOW_TITLE)
    renderer.create_shader()

    while not glfw.window_should_close(renderer.window):
        glfw.poll_events()
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # Rendering code here (e.g., draw objects, use shaders)

        glfw.swap_buffers(renderer.window)

    glfw.terminate()

if __name__ == "__main__":
    main()
