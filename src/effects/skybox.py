import numpy as np
from OpenGL.GL import *
from PIL import Image

def load_shader(vertex_path, fragment_path):
    with open(vertex_path, 'r') as f:
        vertex_src = f.read()
    with open(fragment_path, 'r') as f:
        fragment_src = f.read()
    vertex_shader = glCreateShader(GL_VERTEX_SHADER)
    glShaderSource(vertex_shader, vertex_src)
    glCompileShader(vertex_shader)
    fragment_shader = glCreateShader(GL_FRAGMENT_SHADER)
    glShaderSource(fragment_shader, fragment_src)
    glCompileShader(fragment_shader)
    program = glCreateProgram()
    glAttachShader(program, vertex_shader)
    glAttachShader(program, fragment_shader)
    glLinkProgram(program)
    glDeleteShader(vertex_shader)
    glDeleteShader(fragment_shader)
    return program

class SkyboxGL:
    def __init__(self, texture_path):
        # Cube vertices
        self.vertices = np.array([
            -1,  1, -1,  -1, -1, -1,   1, -1, -1,   1, -1, -1,   1,  1, -1,  -1,  1, -1,  # back
            -1, -1,  1,  -1, -1, -1,  -1,  1, -1,  -1,  1, -1,  -1,  1,  1,  -1, -1,  1,  # left
             1, -1, -1,   1, -1,  1,   1,  1,  1,   1,  1,  1,   1,  1, -1,   1, -1, -1,  # right
            -1, -1,  1,  -1,  1,  1,   1,  1,  1,   1,  1,  1,   1, -1,  1,  -1, -1,  1,  # front
            -1,  1, -1,   1,  1, -1,   1,  1,  1,   1,  1,  1,  -1,  1,  1,  -1,  1, -1,  # top
            -1, -1, -1,  -1, -1,  1,   1, -1,  1,   1, -1,  1,   1, -1, -1,  -1, -1, -1   # bottom
        ], dtype=np.float32)

        self.vao = glGenVertexArrays(1)
        self.vbo = glGenBuffers(1)
        glBindVertexArray(self.vao)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, self.vertices.nbytes, self.vertices, GL_STATIC_DRAW)
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, None)
        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glBindVertexArray(0)

        # Load equirectangular texture
        self.texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.texture)
        image = Image.open(texture_path).convert("RGB")
        img_data = np.array(image, np.uint8)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, image.width, image.height, 0, GL_RGB, GL_UNSIGNED_BYTE, img_data)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glBindTexture(GL_TEXTURE_2D, 0)

        # Load shaders
        self.shader = load_shader("shaders/skybox_vert.glsl", "shaders/skybox_frag.glsl")

    def draw(self, view, projection):
        glDepthFunc(GL_LEQUAL)
        glUseProgram(self.shader)

        # Remove translation from view matrix
        view_no_translation = np.array(view, dtype=np.float32)
        view_no_translation[3, :3] = 0

        view_loc = glGetUniformLocation(self.shader, "view")
        proj_loc = glGetUniformLocation(self.shader, "projection")
        glUniformMatrix4fv(view_loc, 1, GL_FALSE, view_no_translation)
        glUniformMatrix4fv(proj_loc, 1, GL_FALSE, projection)

        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, self.texture)
        tex_loc = glGetUniformLocation(self.shader, "equirectangularMap")
        glUniform1i(tex_loc, 0)

        glBindVertexArray(self.vao)
        glDrawArrays(GL_TRIANGLES, 0, 36)
        glBindVertexArray(0)
        glBindTexture(GL_TEXTURE_2D, 0)
        glUseProgram(0)
        glDepthFunc(GL_LESS)