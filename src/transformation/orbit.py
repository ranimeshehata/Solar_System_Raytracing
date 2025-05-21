import numpy as np
from OpenGL.GL import *

class Orbit:
    def __init__(self, radius, segments=100):
        self.radius = radius
        self.segments = segments
        self.vao = glGenVertexArrays(1)
        self.vbo = glGenBuffers(1)
        self._prepare_circle()

    def _prepare_circle(self):
        theta = np.linspace(0, 2 * np.pi, self.segments, endpoint=True)
        x = self.radius * np.cos(theta)
        z = self.radius * np.sin(theta)
        y = np.zeros_like(x)
        texcoords = np.zeros((self.segments, 2), dtype=np.float32)
        vertices = np.column_stack([x, y, z, texcoords]).astype(np.float32)

        glBindVertexArray(self.vao)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)
        # Position attribute
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 5 * 4, ctypes.c_void_p(0))
        glEnableVertexAttribArray(0)
        # Texcoord attribute (dummy)
        glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 5 * 4, ctypes.c_void_p(3 * 4))
        glEnableVertexAttribArray(1)
        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glBindVertexArray(0)
        self.vertex_count = len(vertices)

    def draw(self, model_loc):
        model = np.eye(4, dtype=np.float32)
        glUniformMatrix4fv(model_loc, 1, GL_FALSE, model)
        glBindVertexArray(self.vao)
        glDrawArrays(GL_LINE_LOOP, 0, self.vertex_count)
        glBindVertexArray(0)