import glfw
from OpenGL.GL.shaders import compileProgram, compileShader
from OpenGL.GL import *

class WindowRenderer:
    """
    A class to manage an OpenGL window using GLFW and compile shaders.

    Attributes:
        window_w (int): Width of the window.
        window_h (int): Height of the window.
        window_x (int): X position of the window on the screen.
        window_y (int): Y position of the window on the screen.
        window_title (str): Title of the window.
        window (GLFWwindow): The GLFW window object.
        shader (int): OpenGL shader program ID (after shader creation).
    """

    def __init__(self, window_w=800, window_h=600, window_x=800, window_y=200, window_title="Window"):
        """
        Initialize the window renderer with specified size, position, and title.

        Args:
            window_w (int): Width of the window (default: 800).
            window_h (int): Height of the window (default: 600).
            window_x (int): X position of the window on the screen (default: 800).
            window_y (int): Y position of the window on the screen (default: 200).
            window_title (str): Title of the window (default: "Window").
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
        Initialize GLFW and create a window.

        Raises:
            Exception: If GLFW fails to initialize or window creation fails.
        """
        if not glfw.init():
            raise Exception("Couldn't initialize GLFW.")

        self.window = glfw.create_window(self.window_w, self.window_h, self.window_title, None, None)
        if not self.window:
            glfw.terminate()
            raise Exception("Couldn't create GLFW window.")

    def create_shader(self, vertex_shader_path="shaders/vertex_shader.glsl", frag_shader_path="shaders/fragment_shader.glsl"):
        """
        Load, compile, and link vertex and fragment shaders.

        Args:
            vertex_shader_path (str): Path to the vertex shader file (default: "shaders/vertex_shader.glsl").
            frag_shader_path (str): Path to the fragment shader file (default: "shaders/fragment_shader.glsl").

        Sets:
            self.shader (int): Compiled and linked shader program ID.

        Raises:
            FileNotFoundError: If one of the shader files does not exist.
            Exception: If shader compilation or linking fails.
        """
        try:
            with open(vertex_shader_path) as f:
                vertex_src = f.read()
            with open(frag_shader_path) as f:
                frag_src = f.read()

            self.shader = compileProgram(
                compileShader(vertex_src, GL_VERTEX_SHADER),
                compileShader(frag_src, GL_FRAGMENT_SHADER),
            )
        except FileNotFoundError:
            print("Shader file(s) not found.")
        except Exception as e:
            print(f"Error compiling/linking shaders: {e}")
