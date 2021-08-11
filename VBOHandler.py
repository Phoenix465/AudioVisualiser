from OpenGL.GL import glGenBuffers, glGetAttribLocation, glBindBuffer, glGetUniformLocation, glBufferData, glUniformMatrix4fv, glBindVertexArray, glGenVertexArrays, glVertexAttribPointer, glEnableVertexAttribArray, glDrawElements, GL_STATIC_DRAW, GL_UNSIGNED_INT, GL_ELEMENT_ARRAY_BUFFER, GL_ARRAY_BUFFER, GL_DYNAMIC_DRAW, GL_FLOAT, GL_FALSE, GL_TRIANGLES
from errors import VBOError
import numpy as np
import ctypes


class VBO:
    def __init__(self, shader, vertices, colours):
        if len(vertices) != len(colours):
            raise VBOError("Length of Vertices Doesn't Match Length of Colours")

        polygon = []
        for vertex, colour in zip(vertices, colours):
            polygon.extend(vertex.list + colour.RGBAList)

        self.polygon = np.array(polygon, dtype=np.float32)

        indices = []
        for i in range(len(vertices)-2):
            indices.extend([
                0,
                i+1,
                i+2
            ])

        self.indices = np.array(indices, dtype=np.uint32)

        self.VAO = glGenVertexArrays(1)
        self.VBO = glGenBuffers(1)
        self.EBO = glGenBuffers(1)

        glBindVertexArray(self.VAO)

        glBindBuffer(GL_ARRAY_BUFFER, self.VBO)
        glBufferData(GL_ARRAY_BUFFER, 4 * len(self.polygon), self.polygon, GL_STATIC_DRAW)

        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.EBO)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, 4 * len(self.indices), self.indices, GL_STATIC_DRAW)

        stride = (3 + 4) * 4  # 3 for xyz and 4 for RGBA

        position = glGetAttribLocation(shader, "position")
        glVertexAttribPointer(position, 3, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(0))
        glEnableVertexAttribArray(position)

        color = glGetAttribLocation(shader, "color")
        glVertexAttribPointer(color, 4, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(3*4))
        glEnableVertexAttribArray(color)

        self.uniformModel = glGetUniformLocation(shader, 'uniform_Model')
        self.uniformView = glGetUniformLocation(shader, 'uniform_View')
        self.uniformProjection = glGetUniformLocation(shader, 'uniform_Projection')

        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glBindVertexArray(0)

    def draw(self):
        glBindVertexArray(self.VAO)
        #glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.EBO)
        glDrawElements(GL_TRIANGLES, len(self.indices), GL_UNSIGNED_INT, None)
        glBindVertexArray(0)

    def delete(self):
        if hasattr(self, "vao"):
            del self.vao

        if hasattr(self, "vbo"):
            del self.vbo

