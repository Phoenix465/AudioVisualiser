import colorsys
from dataclasses import dataclass
from math import floor
from random import random
from time import time

import glm

import VBOHandler
from colour import *
from degreesMath import *
import line_profiler_pycharm


class ScreenQuad:
    def __init__(self):
        self.vertices = [
            glm.vec3(-1, 1, 0),
            glm.vec3(-1, -1, 0),
            glm.vec3(1, 1, 0),
            glm.vec3(1, -1, 0)
        ]

        self.textureCoords = [
            glm.vec2(0, 1),
            glm.vec2(0, 0),
            glm.vec2(1, 1),
            glm.vec2(1, 0),
        ]

        self.quadVBO = VBOHandler.VBOScreen(self.vertices, self.textureCoords)

    def draw(self):
        self.quadVBO.draw()


class ParticleEmitter:
    def __init__(self, shader):
        self.particleCount = 3000

        self.particleSpawnRadius = 0.001

        self.circleSides = 100
        self.circleVertices = []
        for i in range(self.circleSides):
            angle = i / self.circleSides * 360
            width = sin(angle)
            height = cos(angle)

            self.circleVertices.append(
                glm.vec3(width, height, 0)
            )

        self.particles = []
        for i in range(self.particleCount):
            self.particles.append({
                "position": self.generateSpawnPos(),
                "distanceToCentre": self.particleSpawnRadius,
                "velocityUnitMultiplier": 0.05,  # *(random()/2+0.5),
                "scale": 0.05,
                "brightness": 1,
                "scaleMinLimit": 0.05,
                "scaleMaxLimit": 1,
                "scaleDownVelocityPS": 0.5,
                "scaleBeatJump": 0.05,
                "color": [*colorsys.hsv_to_rgb(random(), 1, 1), 1],
                "rotation": random() * 360,
                "lifetime": 500,
                "draw": 0,
                "timestamp": 0  # Creation Date
            })

        self.VBO = VBOHandler.VBOParticle(shader, self.circleVertices, self.particles)

        self.updateCount = 0
        self.currentColour = [*colorsys.hsv_to_rgb(random(), 1, 1), 1]
        self.framesAfterBeat = 0
        self.maxDist = 10

    def generateSpawnPos(self):
        u1 = random()
        u2 = random()

        latitude = acos(2 * u1 - 1) - 90  # -90 -> 90 ==>
        longitude = 2 * 180 * u2

        return glm.vec3(
            cos(latitude) * cos(longitude),
            cos(latitude) * sin(longitude),
            sin(latitude),
        ) * self.particleSpawnRadius

    def sort(self, cameraPos):
        def particleSortFunction(particle):
            return glm.length(particle["position"] - cameraPos)

        self.particles = sorted(self.particles, key=particleSortFunction,
                                reverse=True)
        self.VBO.particles = self.particles

    #@line_profiler_pycharm.profile
    def update(self, deltaT, cameraXAngle, cameraYAngle, currentTime, push=False, avgAmplitude=0):
        def particleSortFunction(particle):
            return particle["timestamp"] + particle["draw"] * 1000000000

        self.updateCount += 1

        tempParticleSort = sorted(self.particles, key=particleSortFunction)
        particleCountSpawn = floor(avgAmplitude)

        self.framesAfterBeat += 1
        if push:
            self.framesAfterBeat = 0

        if self.framesAfterBeat == 5:
            self.currentColour = [*colorsys.hsv_to_rgb(random(), 1, 1), 1]

        chosenParticles = tempParticleSort[:particleCountSpawn * (self.updateCount % 4 == 0) + 100 * push]
        for particle in chosenParticles:
            particle["draw"] = True
            particle["timestamp"] = currentTime
            particle["position"] = self.generateSpawnPos()
            particle["distanceToCentre"] = self.particleSpawnRadius
            particle["color"] = self.currentColour

        for particle in self.particles:
            if not particle["draw"]:
                continue

            if glm.length(particle["position"]) > self.maxDist:
                particle["draw"] = False
                continue

            particle["scale"] -= particle["scaleDownVelocityPS"] * deltaT / 1000

            if push:
                particle["scale"] += particle["scaleBeatJump"]

            particle["scale"] = max(particle["scaleMinLimit"], particle["scale"])
            particle["scale"] = min(particle["scaleMaxLimit"], particle["scale"])

            particle["position"] += glm.normalize(particle["position"]) * particle["velocityUnitMultiplier"]
            particle["distanceToCentre"] += particle["velocityUnitMultiplier"]
            alphaVal = 1-(particle["distanceToCentre"]/self.maxDist)

            particle["color"][3] = alphaVal

        self.VBO.update(cameraXAngle, cameraYAngle)

    def draw(self):
        self.VBO.draw()
