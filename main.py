import struct
from math import floor

import struct
import wave
from math import floor
from random import random
from time import time

import \
    glm  # If Window doesn't draw anything it's likely you installed PyGLM > 2.22, however only 1.99.3 works (only tested this)
import numpy as np
import pyaudio
import pygame
from OpenGL.GL import *
from pygame import DOUBLEBUF, OPENGL

import GameObjects
import ShaderLoader
import gamePaths
from degreesMath import *
from vector import *


#  ffmpeg -i "No.1 - Kobasolo.mp3" "No.1 - Kobasolo2.wav"


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
    glUseProgram(shader)

    uniformModel = glGetUniformLocation(shader, 'uniform_Model')
    uniformView = glGetUniformLocation(shader, 'uniform_View')
    uniformProjection = glGetUniformLocation(shader, 'uniform_Projection')

    # ----- OpenGL Settings -----
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

    glClearColor(0, 0, 0, 1.0)
    #glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)

    # ----- Camera Settings -----
    cameraRadius = 7
    cameraPos = Vector3(0, 0, cameraRadius)
    cameraFront = Vector3(0, 0, 0)
    cameraUp = Vector3(0, 1, 0)
    rotationAngle = 0

    # ----- Matrix Info -----
    projectionMatrix = glm.perspective(70, displayV.X/displayV.Y, 1, 1000.0)
    modelMatrix = glm.mat4(1)

    glUniformMatrix4fv(uniformModel, 1, GL_FALSE,
                       np.squeeze(modelMatrix))
    glUniformMatrix4fv(uniformProjection, 1, GL_FALSE,
                       np.squeeze(projectionMatrix))

    # Temp Object Set-Up
    newCircle = GameObjects.Circle(shader, Vector3(0, 0, 0), 0.05 , 45)

    newCircle2 = GameObjects.Circle(shader, Vector3(0, 0.8, 0.2), 0.05, 45)

    gameObjectHolder = GameObjects.GameObjectHolder()
    gameObjectHolder.addObject(newCircle)
    gameObjectHolder.addObject(newCircle2)

    for _ in range(200):
        gameObjectHolder.addObject(
            GameObjects.Circle(shader, Vector3(random()*3-1.5, random()*3-1.5, random()*3-1.5), 0.05, 45)
        )

    # ---- Sound Stuff -----
    chunkSize = 1024

    soundFile = wave.open(GamePaths.songPath, "rb")
    pyAudioObj = pyaudio.PyAudio()

    frequencyRange = 1.0 * np.arange(chunkSize) / chunkSize * soundFile.getframerate()
    print(frequencyRange, len(frequencyRange))
    maxY = 2.0 ** (pyAudioObj.get_sample_size(pyaudio.paInt16) * 8 - 1)

    soundStream = pyAudioObj.open(
        format=pyaudio.get_format_from_width(soundFile.getsampwidth()),
        channels=soundFile.getnchannels(),
        rate=soundFile.getframerate(),
        output=True
    )

    soundEnergyHistoryBuffer = np.full((32, 45), 30)

    soundData = [0]

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

        glUniformMatrix4fv(uniformView, 1, GL_FALSE,
                           np.squeeze(viewMatrix))

        if len(soundData) > 0 and False:
            #  http://www.williamvennes.com/beat-detection.html

            soundData = soundFile.readframes(chunkSize)
            soundStream.write(soundData)

            channelsData = np.array(struct.unpack("%dh" % (chunkSize * 2), soundData)) / maxY

            channelsDataAmplitudeL = np.fft.fft(channelsData[::2], chunkSize)
            channelsDataAmplitudeR = np.fft.fft(channelsData[1::2], chunkSize)

            soundAmplitudeBuffer = channelsDataAmplitudeL + channelsDataAmplitudeR  # Adds Two arrays element-wise.
            soundAmplitudeBuffer = abs(soundAmplitudeBuffer)

            #nstantEnergyBuffer = (32/1024) * np.sum(soundAmplitudeBuffer.reshape(-1, 32), axis=1)  # Splits Array into 32 sets of 32 and sums each set (entire thing just averages)
            instantEnergyBuffer = np.average(soundAmplitudeBuffer.reshape(-1, 32), axis=1)

            if all(instantEnergyBuffer != 0):
                #print(1, instantEnergyBuffer[0])
                soundEnergyHistoryBuffer = np.roll(soundEnergyHistoryBuffer, 1, axis=1)
                soundEnergyHistoryBuffer[:, 0] = instantEnergyBuffer

                averageSoundEnergyHistory = np.average(soundEnergyHistoryBuffer, axis=1)
                #print(averageSoundEnergyHistory[0], instantEnergyBuffer[0])
                #print(2, averageSoundEnergyHistory[0])
                beatBooleanMask = instantEnergyBuffer > averageSoundEnergyHistory * 1.25

                if beatBooleanMask[0]:
                    tempCircle = GameObjects.Circle(shader, Vector3(random()*4-2, random()*4-2, random()*4-2), 0.05, 45)
                    gameObjectHolder.addObject(tempCircle)
                    print("BEAT")

                #print(channelsDataAmplitudeL[20], channelsDataAmplitudeR[20])

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
