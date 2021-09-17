import colorsys
from math import floor
from random import random

import glm

import VBOHandler
from degreesMath import *


#import line_profiler_pycharm


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
        self.particleCount = 2000

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
            newPos = self.generateSpawnPos()

            self.particles.append({
                "position": newPos,
                "normalisedVector": glm.normalize(newPos),
                "distanceToCentre": self.particleSpawnRadius,
                "velocityUnitMultiplier": 0.05,  # *(random()/2+0.5),
                "scale": 0.05,
                "scaleMinLimit": 0.05,
                "scaleMaxLimit": 1,
                "scaleBeatSize": 0.25,
                "scaleDownVelocityPS": 0.6,
                "scaleBeatJump": 0.05,
                "color": [*colorsys.hsv_to_rgb(random(), 1, 1), 1],
                "rotation": random() * 360,
                "lifetime": 500,
                "draw": 0,
                "timestamp": 0  # Creation Date
            })
        self.particleOrder = self.particles

        self.VBO = VBOHandler.VBOParticle(shader, self.circleVertices, self.particles)

        self.updateCount = 0
        self.changeColourCount = int(random()*360)
        self.currentColour = [*colorsys.hsv_to_rgb(self.changeColourCount/360, 1, 1), 1]
        self.canChangeColour = False
        self.lastBeatTime = 0
        self.maxDist = 10

    def generateSpawnPos(self):
        u1 = random()
        u2 = random()

        latitude = acos(2 * u1 - 1) - 90  # -90 -> 90 ==>
        #latitude = (acos(2 * u1 - 1) - 90)*0.1 + 180  # -90 -> 90 ==>
        #latitude = 45

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

    def update(self, deltaT, currentTime, push=False, avgAmplitude=0):
        self.updateCount += 1

        particleCountSpawn = floor(avgAmplitude)

        if push:
            self.lastBeatTime = currentTime
            self.canChangeColour = True

        if currentTime - self.lastBeatTime > 80 and self.canChangeColour:  # ms btw
            self.canChangeColour = False
            self.changeColourCount += 20
            self.currentColour = [*colorsys.hsv_to_rgb(self.changeColourCount/360, 1, 1), 1]

        particleCount = particleCountSpawn * (self.updateCount % 4 == 0) + 150 * push
        chosenParticles = self.particleOrder[:particleCount]
        self.particleOrder = self.particleOrder[particleCount:] + self.particleOrder[:particleCount]

        for particle in chosenParticles:
            newPos = self.generateSpawnPos()

            particle["draw"] = True
            particle["timestamp"] = currentTime
            particle["position"] = newPos
            particle["normalisedVector"] = glm.normalize(newPos)
            particle["distanceToCentre"] = self.particleSpawnRadius
            particle["color"] = self.currentColour

        for particle in self.particles:
            if not particle["draw"]:
                continue

            if particle["distanceToCentre"] > self.maxDist:
                particle["draw"] = False
                continue

            particle["scale"] -= particle["scaleDownVelocityPS"] * deltaT / 1000

            if push:
                particle["scale"] += particle["scaleBeatJump"]

                if particle["distanceToCentre"] < 0.25:
                    particle["scale"] = particle["scaleBeatSize"]

            particle["scale"] = max(particle["scaleMinLimit"], particle["scale"])
            particle["scale"] = min(particle["scaleMaxLimit"], particle["scale"])

            particle["position"] += particle["normalisedVector"] * particle["velocityUnitMultiplier"]
            particle["distanceToCentre"] += particle["velocityUnitMultiplier"]
            alphaVal = 1-(particle["distanceToCentre"]/self.maxDist)

            particle["color"][3] = alphaVal * 0.8

        self.VBO.update()

    def draw(self):
        self.VBO.draw()
