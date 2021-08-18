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
        velocityUnitMultiplier: float
        color: Colour
        lifetime: float
        scale: float
        scaleMinLimit: float
        scaleMaxLimit: float
        scaleDownVelocityPS: float
        scaleBeatJump: float
        rotation: float
        brightness: float

    def __init__(self, shader):
        self.particleCount = 2000

        self.particleSpawnRadius = 0.001

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
            u1 = random()
            u2 = random()

            latitude = acos(2*u1-1) - 90
            longitude = 2 * 180 * u2

            self.particles.append(
                self.Particle(
                    position=glm.vec3(
                        cos(latitude)*cos(longitude),
                        cos(latitude)*sin(longitude),
                        sin(latitude),
                    ) * self.particleSpawnRadius,
                    velocityUnitMultiplier=0.005,
                    scale=0.05,
                    brightness=random(),
                    scaleMinLimit=0.05,
                    scaleMaxLimit=1,
                    scaleDownVelocityPS=0.5,
                    scaleBeatJump=0.05,
                    color=Colour(random(), random(), random(), alpha=.5),
                    rotation=random() * 360,
                    lifetime=500,
                )
            )
            
        self.VBO = VBOHandler.VBOParticle(shader, self.circleVertices, self.particles)

    def sort(self, cameraPos):
        self.particles = sorted(self.particles, key=lambda particle: glm.length(particle.position-cameraPos), reverse=True)
        self.VBO.particles = self.particles

    def update(self, deltaT, cameraXAngle, cameraYAngle, push=False):
        for particle in self.particles:
            particle.scale -= particle.scaleDownVelocityPS * deltaT / 1000

            if push:
                particle.scale += particle.scaleBeatJump

            particle.scale = max(particle.scaleMinLimit, particle.scale)
            particle.scale = min(particle.scaleMaxLimit, particle.scale)

            particle.position += glm.normalize(particle.position) * particle.velocityUnitMultiplier

        self.VBO.update(cameraXAngle, cameraYAngle)

    def draw(self):
        self.VBO.draw()
