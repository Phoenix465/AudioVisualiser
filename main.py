import struct
import wave
from math import floor
from time import time

import glm
import numpy as np
import pyaudio
import pygame
from OpenGL.GL import *
from pygame import DOUBLEBUF, OPENGL

import GameObjects
import ShaderLoader
import gamePaths
from degreesMath import *


#  ffmpeg -i "No.1 - Kobasolo.mp3" "No.1 - Kobasolo2.wav"


def main():
    # Initialisation
    pygame.init()
    pygame.mixer.init()
    GamePaths = gamePaths.PathHolder()

    display = 1366, 768
    displayV = glm.vec2(display)

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
    glViewport(0, 0, int(displayV.x), int(displayV.y))
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
    cameraPos = glm.vec3(0, 0, cameraRadius)
    cameraFront = glm.vec3(0, 0, 0)
    cameraUp = glm.vec3(0, 1, 0)
    rotationAngle = 0

    # ----- Matrix Info -----
    projectionMatrix = glm.perspective(70, displayV.x/displayV.y, 1, 1000.0)
    modelMatrix = glm.mat4(1)

    glUniformMatrix4fv(uniformModel, 1, GL_FALSE,
                       glm.value_ptr(modelMatrix))

    glUniformMatrix4fv(uniformProjection, 1, GL_FALSE,
                       glm.value_ptr(projectionMatrix))
    # ---- Particle Emitter ----
    particleEmitterObject = GameObjects.ParticleEmitter(shader)

    # ---- Sound Stuff -----
    chunkSize = 1024
    groupCount = 32

    soundFile = wave.open(GamePaths.songPath, "rb")
    pyAudioObj = pyaudio.PyAudio()

    frequencyRange = 1.0 * np.arange(chunkSize) / chunkSize * soundFile.getframerate()
    print("Frequency Range", frequencyRange[:64], frequencyRange[16], frequencyRange[32], frequencyRange[64], frequencyRange[32*7])
    maxY = 2.0 ** (pyAudioObj.get_sample_size(pyaudio.paInt16) * 8 - 1)

    soundStream = pyAudioObj.open(
        format=pyaudio.get_format_from_width(soundFile.getsampwidth()),
        channels=soundFile.getnchannels(),
        rate=soundFile.getframerate(),
        output=True
    )

    soundEnergyHistoryBuffer = np.full((groupCount, 45), 30)

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

        rotationAngle += deltaT / 1000 * 10
        cameraPos = glm.vec3(sin(rotationAngle) * cameraRadius, 0, cos(rotationAngle) * cameraRadius)

        viewMatrix = glm.lookAt(cameraPos,
                                cameraFront,
                                cameraUp)

        glUniformMatrix4fv(uniformView, 1, GL_FALSE,
                           glm.value_ptr(viewMatrix))

        beat = False

        if len(soundData) > 0:
            #  http://www.williamvennes.com/beat-detection.html

            soundData = soundFile.readframes(chunkSize)
            soundStream.write(soundData)

            channelsData = np.array(struct.unpack("%dh" % (chunkSize * 2), soundData))

            channelsDataAmplitudeL = np.fft.fft(channelsData[::2], chunkSize)
            channelsDataAmplitudeR = np.fft.fft(channelsData[1::2], chunkSize)

            soundAmplitudeBuffer = channelsDataAmplitudeL + channelsDataAmplitudeR  # Adds Two arrays element-wise.
            soundAmplitudeBuffer = abs(soundAmplitudeBuffer)

            #nstantEnergyBuffer = (32/1024) * np.sum(soundAmplitudeBuffer.reshape(-1, 32), axis=1)  # Splits Array into 32 sets of 32 and sums each set (entire thing just averages)
            instantEnergyBuffer = np.average(soundAmplitudeBuffer.reshape(-1, chunkSize//groupCount), axis=1)

            if all(instantEnergyBuffer != 0):
                #print(1, instantEnergyBuffer[0])
                soundEnergyHistoryBuffer = np.roll(soundEnergyHistoryBuffer, 1, axis=1)
                soundEnergyHistoryBuffer[:, 0] = instantEnergyBuffer

                averageSoundEnergyHistory = np.average(soundEnergyHistoryBuffer, axis=1)
                #print(averageSoundEnergyHistory[0], instantEnergyBuffer[0])
                #print(2, averageSoundEnergyHistory[0])
                beatBooleanMask = instantEnergyBuffer > averageSoundEnergyHistory * 5

                if any(beatBooleanMask):
                    beat = True

                #print(channelsDataAmplitudeL[20], channelsDataAmplitudeR[20])

        particleEmitterObject.update(deltaT, rotationAngle, push=beat)
        particleEmitterObject.sort(cameraPos)
        particleEmitterObject.draw()

        fps = str(floor(clock.get_fps()))

        pygame.display.flip()

        e = time() * 1000
        ft = e - s

        times.append(ft)

    print(sum(times) / len(times))


if __name__ == "__main__":
    main()
