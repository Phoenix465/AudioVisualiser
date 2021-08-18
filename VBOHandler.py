import ctypes

import glm
import numpy as np
from OpenGL.GL import glGenBuffers, glGetAttribLocation, glBindBuffer, glBufferData, glDrawElementsInstanced, \
    glBindVertexArray, glGenVertexArrays, glVertexAttribPointer, glBufferSubData, glEnableVertexAttribArray, \
    glVertexAttribDivisor, GL_STATIC_DRAW, GL_DYNAMIC_DRAW, GL_UNSIGNED_INT, GL_ELEMENT_ARRAY_BUFFER, GL_ARRAY_BUFFER, \
    GL_FLOAT, GL_FALSE, \
    GL_TRIANGLES


class VBOParticle:
    def __init__(self, shader, vertices, particles):
        self.vertices = vertices
        self.particles = particles
        self.particleData = self.serializeParticles(0, 0)

        self.polygon = self.generatePolygon()

        indices = []
        for i in range(len(vertices)-2):
            indices.extend([
                0,
                i+1,
                i+2
            ])

        self.indices = np.array(indices, dtype=np.uint32)

        self.VAO = glGenVertexArrays(1)
        self.VBO = glGenBuffers(1)  # Vertex Buffer Object
        self.PBO = glGenBuffers(1)  # Position Buffer Object
        self.EBO = glGenBuffers(1)  # Element Buffer Object

        glBindVertexArray(self.VAO)

        glBindBuffer(GL_ARRAY_BUFFER, self.VBO)
        glBufferData(GL_ARRAY_BUFFER, 4 * len(self.polygon), self.polygon, GL_STATIC_DRAW)

        glBindBuffer(GL_ARRAY_BUFFER, self.PBO)
        glBufferData(GL_ARRAY_BUFFER, 4 * len(self.particleData), self.particleData, GL_DYNAMIC_DRAW)

        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.EBO)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, 4 * len(self.indices), self.indices, GL_STATIC_DRAW)

        self.vertexStride = 3 * 4
        self.particleStride = (3 + 4 + 1 + 4 + 4 + 4 + 4) * 4

        self.vertexPositionLocation = glGetAttribLocation(shader, "vertexPosition")
        glBindBuffer(GL_ARRAY_BUFFER, self.VBO)
        glVertexAttribPointer(self.vertexPositionLocation, 3, GL_FLOAT, GL_FALSE, self.vertexStride, ctypes.c_void_p(0))
        glEnableVertexAttribArray(self.vertexPositionLocation)

        self.worldPositionLocation = glGetAttribLocation(shader, "worldPosition")
        glBindBuffer(GL_ARRAY_BUFFER, self.PBO)
        glVertexAttribPointer(self.worldPositionLocation, 3, GL_FLOAT, GL_FALSE, self.particleStride, ctypes.c_void_p(0))
        glVertexAttribDivisor(self.worldPositionLocation, 1)
        glEnableVertexAttribArray(self.worldPositionLocation)

        self.colorLocation = glGetAttribLocation(shader, "color")
        glVertexAttribPointer(self.colorLocation, 4, GL_FLOAT, GL_FALSE, self.particleStride, ctypes.c_void_p(3 * 4))
        glVertexAttribDivisor(self.colorLocation, 1)
        glEnableVertexAttribArray(self.colorLocation)

        self.scaleLocation = glGetAttribLocation(shader, "scale")
        glVertexAttribPointer(self.scaleLocation, 1, GL_FLOAT, GL_FALSE, self.particleStride, ctypes.c_void_p((3+4) * 4))
        glVertexAttribDivisor(self.scaleLocation, 1)
        glEnableVertexAttribArray(self.scaleLocation)

        self.lookAtMatrix0Location = glGetAttribLocation(shader, "lookAtMatrix0")
        glVertexAttribPointer(self.lookAtMatrix0Location, 4, GL_FLOAT, GL_FALSE, self.particleStride, ctypes.c_void_p((3+4+1) * 4))
        glVertexAttribDivisor(self.lookAtMatrix0Location, 1)
        glEnableVertexAttribArray(self.lookAtMatrix0Location)

        self.lookAtMatrix1Location = glGetAttribLocation(shader, "lookAtMatrix1")
        glVertexAttribPointer(self.lookAtMatrix1Location, 4, GL_FLOAT, GL_FALSE, self.particleStride, ctypes.c_void_p((3+4+1+4)*4))
        glVertexAttribDivisor(self.lookAtMatrix1Location, 1)
        glEnableVertexAttribArray(self.lookAtMatrix1Location)

        self.lookAtMatrix2Location = glGetAttribLocation(shader, "lookAtMatrix2")
        glVertexAttribPointer(self.lookAtMatrix2Location, 4, GL_FLOAT, GL_FALSE, self.particleStride, ctypes.c_void_p((3+4+1+4+4)*4))
        glVertexAttribDivisor(self.lookAtMatrix2Location, 1)
        glEnableVertexAttribArray(self.lookAtMatrix2Location)

        self.lookAtMatrix3Location = glGetAttribLocation(shader, "lookAtMatrix3")
        glVertexAttribPointer(self.lookAtMatrix3Location, 4, GL_FLOAT, GL_FALSE, self.particleStride, ctypes.c_void_p((3+4+1+4+4+4)*4))
        glVertexAttribDivisor(self.lookAtMatrix3Location, 1)
        glEnableVertexAttribArray(self.lookAtMatrix3Location)

        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glBindVertexArray(0)

    def update(self, cameraXAngle, cameraYAngle):
        glBindVertexArray(self.VAO)

        self.particleData = self.serializeParticles(cameraXAngle, cameraYAngle)

        glBindBuffer(GL_ARRAY_BUFFER, self.PBO)
        glBufferSubData(GL_ARRAY_BUFFER, 0, len(self.particleData) * 4, self.particleData)

        glBindVertexArray(0)

    def draw(self):
        glBindVertexArray(self.VAO)
        glDrawElementsInstanced(GL_TRIANGLES, len(self.indices), GL_UNSIGNED_INT, None, len(self.particles))
        glBindVertexArray(0)

    def serializeParticles(self, cameraXAngle, cameraYAngle):
        lookMatrix = glm.mat4(1)

        yRotation = glm.rotate(lookMatrix, glm.radians(cameraYAngle+90), (1, 0, 0))
        xRotation = glm.rotate(lookMatrix, glm.radians(cameraXAngle), (0, 1, 0))

        lookMatrix = xRotation * yRotation

        lookMatrix = lookMatrix.to_list()
        lookMatrixCombined = lookMatrix[0] + lookMatrix[1] + lookMatrix[2] + lookMatrix[3]

        particleData = []
        for particle in self.particles:
            particleData.extend(particle.position.to_list() + particle.color.RGBAList + [particle.scale] + lookMatrixCombined)

        return np.array(particleData, dtype=np.float32)

    def generatePolygon(self):
        polygon = []
        for vertex in self.vertices:
            polygon.extend(vertex.to_list())

        return np.array(polygon, dtype=np.float32)
