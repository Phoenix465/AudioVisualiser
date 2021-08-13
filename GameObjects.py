from dataclasses import dataclass
from random import random

import glm

import VBOHandler
from colour import *
from degreesMath import *


class ParticleEmitter:
    @dataclass
    class Particle:
        position: glm.vec3
        color: Colour
        lifetime: float
        size: glm.vec3
        rotation: float

    def __init__(self, shader):
        self.circleRadius = 0.05
        self.particleCount = 1000

        self.circleSides = 45
        self.circleVertices = []
        for i in range(self.circleSides):
            angle = i/self.circleSides * 360
            width = sin(angle) * self.circleRadius
            height = cos(angle) * self.circleRadius

            self.circleVertices.append(
                glm.vec3(width, height, 0)
            )

        self.particles = []
        for i in range(self.particleCount):
            self.particles.append(
                self.Particle(
                    position=glm.vec3(random() - 0.5, random() - 0.5, random() - 0.5) * 4,
                    size=glm.vec3(0.05, 0.05, 0.05),
                    color=Colour(random(), random(), random(), alpha=.5),
                    rotation=random() * 360,
                    lifetime=500
                )
            )
            
        self.VBO = VBOHandler.VBOParticle(shader, self.circleVertices, self.particles)

    def update(self, cameraAngle):
        self.VBO.update(cameraAngle)

    def draw(self):
        self.VBO.draw()
