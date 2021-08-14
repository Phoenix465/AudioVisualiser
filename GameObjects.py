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
        scale: float
        scaleMinLimit: float
        scaleMaxLimit: float
        scaleDownVelocityPS: float
        scaleBeatJump: float
        rotation: float

    def __init__(self, shader):
        self.particleCount = 2000

        self.circleSides = 100
        self.circleVertices = []
        for i in range(self.circleSides):
            angle = i/self.circleSides * 360
            width = sin(angle)
            height = cos(angle)

            self.circleVertices.append(
                glm.vec3(width, height, 0)
            )

        self.particles = []
        for i in range(self.particleCount):
            self.particles.append(
                self.Particle(
                    position=glm.vec3(random() - 0.5, random() - 0.5, random() - 0.5) * 4,
                    scale=0.05,
                    scaleMinLimit=0.05,
                    scaleMaxLimit=1,
                    scaleDownVelocityPS=1,
                    scaleBeatJump=0.05,
                    color=Colour(random(), random(), random(), alpha=.5),
                    rotation=random() * 360,
                    lifetime=500
                )
            )
            
        self.VBO = VBOHandler.VBOParticle(shader, self.circleVertices, self.particles)

    def sort(self, cameraPos):
        self.particles = sorted(self.particles, key=lambda particle: glm.length(particle.position-cameraPos), reverse=True)
        self.VBO.particles = self.particles

    def update(self, deltaT, cameraAngle, push=False):
        for particle in self.particles:
            particle.scale -= particle.scaleDownVelocityPS * deltaT / 1000

            if push:
                particle.scale += particle.scaleBeatJump

            particle.scale = max(particle.scaleMinLimit, particle.scale)
            particle.scale = min(particle.scaleMaxLimit, particle.scale)

            #particle.position += glm.normalize(particle.position) * 0.05

        self.VBO.update(cameraAngle)

    def draw(self):
        self.VBO.draw()
