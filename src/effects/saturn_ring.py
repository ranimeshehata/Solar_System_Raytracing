import numpy as np
from OpenGL.GL import *
from PIL import Image


class SaturnRing:
    def __init__(self, inner_radius, outer_radius, texture_path):
        self.inner_radius = inner_radius
        self.outer_radius = outer_radius
        self.texture_path = texture_path
        self.vao = glGenVertexArrays(1)
        self.vbo = glGenBuffers(1)
        self.vertex_count = 0
        self._load_texture(texture_path)
        self._create_buffers(self._create_ring_geometry())

    def _load_texture(self, path):
        """
        Load and configure a 2D texture in OpenGL using the image at self.texture_path.
        """
        image = Image.open(self.texture_path)
        img_data = np.array(image.convert("RGBA")).tobytes()

        # Generate and bind a texture object
        self.texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.texture)

        # Upload image data to the GPU
        glTexImage2D(
            GL_TEXTURE_2D,
            0,
            GL_RGBA,
            image.width,
            image.height,
            0,
            GL_RGBA,
            GL_UNSIGNED_BYTE,
            img_data,
        )

        # Set texture filtering and wrapping
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)

    def _create_ring_geometry(self):
        segments = 100
        vertices = []
        for i in range(segments + 1):
            angle = 2 * np.pi * i / segments
            x = np.cos(angle)
            z = np.sin(angle)
            vertices += [self.inner_radius * x, 0, self.inner_radius * z, 1, 0]
            vertices += [self.outer_radius * x, 0, self.outer_radius * z, 0, 1]
        self.vertex_count = len(vertices) // 5
        vertices = np.array(vertices, dtype=np.float32)
        return vertices

    def _create_buffers(self, vertices):
        glBindVertexArray(self.vao)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)

        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 5 * 4, ctypes.c_void_p(0))
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 5 * 4, ctypes.c_void_p(3 * 4))

        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glBindVertexArray(0)

    def draw(self, model_loc, model_matrix):
        glBindTexture(GL_TEXTURE_2D, self.texture)
        glUniformMatrix4fv(model_loc, 1, GL_FALSE, model_matrix)
        glBindVertexArray(self.vao)
        glDrawArrays(GL_TRIANGLE_STRIP, 0, self.vertex_count)
        glBindVertexArray(0)
