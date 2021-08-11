from math import floor

import numpy as np
import pygame
from pygame import GL_MULTISAMPLEBUFFERS, GL_MULTISAMPLESAMPLES, DOUBLEBUF, OPENGL
import pyaudio

from vector import *
from time import time
from OpenGL.GL import *
from OpenGL.GLU import gluPerspective, gluLookAt
import ShaderLoader
import GameObjects
from degreesMath import *
import glm  # If Window doesn't draw anything it's likely you installed PyGLM > 2.22, however only 1.99.3 works (only tested this)

import gamePaths


def main():
    # Initialisation
    pygame.init()
    pygame.mixer.init()
    GamePaths = gamePaths.PathHolder()

    display = 1366, 768
    displayV = Vector2(*display)

    screen = pygame.display.set_mode(display, DOUBLEBUF | OPENGL)

    pygame.display.set_caption("Audio Visualiser")

    iconSurface = pygame.image.load(GamePaths.iconPath)
    pygame.display.set_icon(iconSurface)

    pygame.display.flip()

    shader = ShaderLoader.compileShaders("shaders/vertex.shader", "shaders/fragment.shader")

    uniformModel = glGetUniformLocation(shader, 'uniform_Model')
    uniformView = glGetUniformLocation(shader, 'uniform_View')
    uniformProjection = glGetUniformLocation(shader, 'uniform_Projection')

    # OpenGL Settings
    print(f"OpenGL Version: {glGetString(GL_VERSION).decode()}")

    glMatrixMode(GL_PROJECTION)
    #gluPerspective(70, (displayV.X / displayV.Y), 0.1, 128.0)
    glViewport(0, 0, displayV.X, displayV.Y)
    glMatrixMode(GL_MODELVIEW)

    glEnable(GL_DEPTH_TEST)
    glEnable(GL_MULTISAMPLE)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_SRC_ALPHA)
    #glDisable(GL_CULL_FACE)

    glUseProgram(shader)
    glClearColor(0, 0, 0, 1.0)

    #glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)

    # Settings
    cameraRadius = 5
    cameraPos = Vector3(0, 0, cameraRadius)
    cameraFront = Vector3(0, 0, 0)
    cameraUp = Vector3(0, 1, 0)
    rotationAngle = 0

    projectionMatrix = glm.perspective(70, displayV.X/displayV.Y, 1, 1000.0)
    modelMatrix = glm.mat4(1)

    # Temp Object Set-Up
    newCircle = GameObjects.Circle(shader, Vector3(0, 0, 0), 0.5, 45)
    newCircle2 = GameObjects.Circle(shader, Vector3(0, 0.8, 0.2), 0.5, 45)

    gameObjectHolder = GameObjects.GameObjectHolder()
    gameObjectHolder.addObject(newCircle)
    gameObjectHolder.addObject(newCircle2)

    times = [0]
    running = True
    clock = pygame.time.Clock()

    while running:
        deltaT = clock.tick(60)
        s = time() * 1000
        
        keyPressed = pygame.key.get_pressed()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        rotationAngle += deltaT / 1000 * 45
        cameraPos = Vector3(sin(rotationAngle) * cameraRadius, 0, cos(rotationAngle) * cameraRadius)

        viewMatrix = glm.lookAt(cameraPos.tuple,
                                cameraFront.tuple,
                                cameraUp.tuple)

        glUniformMatrix4fv(uniformModel, 1, GL_FALSE,
                           np.squeeze(modelMatrix))
        glUniformMatrix4fv(uniformView, 1, GL_FALSE,
                           np.squeeze(viewMatrix))
        glUniformMatrix4fv(uniformProjection, 1, GL_FALSE,
                           np.squeeze(projectionMatrix))

        gameObjectHolder.orderObjects(cameraPos)
        gameObjectHolder.draw()

        fps = str(floor(clock.get_fps()))

        pygame.display.flip()

        e = time() * 1000
        ft = e - s

        times.append(ft)

    print(sum(times) / len(times))


if __name__ == "__main__":
    main()
