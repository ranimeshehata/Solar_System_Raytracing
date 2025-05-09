import glfw
from OpenGL.GL.shaders import compileProgram, compileShader
from OpenGL.GL import *

class WindowRenderer:
    def __init__(self, window_w=800, window_h=600, window_x=800, window_y=200, window_title="Window"):
        """
        Initializes the window renderer with custom window size, position, and title.

        :param window_w: Window width (default 800)
        :param window_h: Window height (default 600)
        :param window_x: Window x-position (default 800)
        :param window_y: Window y-position (default 200)
        :param window_title: Title of the window (default "Window")
        """
        self.window_w = window_w
        self.window_h = window_h
        self.window_x = window_x
        self.window_y = window_y
        self.window_title = window_title

        self._initialize_window()
        glfw.make_context_current(self.window)
        glfw.set_window_pos(self.window, self.window_x, self.window_y)

    def _initialize_window(self):
        """
        Initializes GLFW, creates the window, and checks for errors.
        """
        if not glfw.init():
            raise Exception("Couldn't Initialize glfw! :(")

        self.window = glfw.create_window(self.window_w, self.window_h, self.window_title, None, None)
        if not self.window:
            glfw.terminate()
            raise Exception("Couldn't Create Window! :(")

    def create_shader(self, vertex_shader_path="shaders/vertex_shader.glsl", frag_shader_path="shaders/fragment_shader.glsl"):
        """
        Loads, compiles, and links vertex and fragment shaders.

        :param vertex_shader_path: Path to the vertex shader file (default "shaders/vertex_shader.glsl")
        :param frag_shader_path: Path to the fragment shader file (default "shaders/fragment_shader.glsl")
        """
        try:
            # Read shader source files
            with open(vertex_shader_path) as f:
                vertex_shader_source = f.read()
            with open(frag_shader_path) as f:
                fragment_shader_source = f.read()

            # Compile and link shaders
            self.shader = compileProgram(
                compileShader(vertex_shader_source, GL_VERTEX_SHADER),
                compileShader(fragment_shader_source, GL_FRAGMENT_SHADER),
            )
        except FileNotFoundError:
            print("Shader File(s) not Found! :(")
        except Exception as e:
            print(f"Error during shader compilation: {e}")
