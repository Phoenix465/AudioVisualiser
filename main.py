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
import audio
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
    sampleWidth = soundFile.getsampwidth()
    frameRate = soundFile.getframerate()
    channels = soundFile.getnchannels()

    beatTypeRanges = (
        (20, 60),  # Sub Bass
        (60, 250),  # Bass
        (250, 500),  # Low Midrange
        (500, 2000),  # Mid Range
        (2000, 4000),  # Upper Midrange
        (4000, 6000),  # Presence
        (6000, 20000)  # Brilliance
    )

    beatTypeMax = [10 for _ in range(len(beatTypeRanges))]
    beatTypeHit = [False for _ in range(len(beatTypeRanges))]

    pyAudioObj = pyaudio.PyAudio()

    frequencies = frameRate * np.arange(chunkSize / 2) / chunkSize

    maxY = 2.0 ** (pyAudioObj.get_sample_size(pyaudio.paInt16) * 8 - 1)

    soundStream = pyAudioObj.open(
        format=pyaudio.get_format_from_width(soundFile.getsampwidth()),
        channels=soundFile.getnchannels(),
        rate=soundFile.getframerate(),
        output=True
    )

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
            soundData = soundFile.readframes(chunkSize)
            soundStream.write(soundData)

            #  https://github.com/WarrenWeckesser/wavio/blob/cff688a318173a2bc700297a30a70858730b901f/wavio.py
            #  https://github.com/maxemitchell/portfolio/blob/master/src/pages/code_art/thanksgiving_break/index.js
            #  https://github.com/maxemitchell/beat-detection-python/blob/master/beat-detector.py

            audioArrayData = audio.audioDataToArray(soundData, sampleWidth, channels)
            audioFFT = np.abs((np.fft.fft(audioArrayData)[:int(len(audioArrayData)/2)]) / len(audioArrayData))

            beatTypeIndices = [
                [frequencyI for frequencyI, frequency in enumerate(frequencies)
                 if frequency >= lowerB and frequency < upperB] for lowerB, upperB in beatTypeRanges
            ]

            beatMaxFFT = [np.max(audioFFT[beatIndexRange]) for beatIndexRange in beatTypeIndices]
            beatTypeMax = [max(beatMax, beatTypeMax[i]) for i, beatMax in enumerate(beatMaxFFT)]

            for i, beatMax in enumerate(beatMaxFFT):
                if beatMax >= beatTypeMax[i] * 0.5 and not beatTypeHit[i]:
                    beatTypeHit[i] = True

                elif beatMax < beatTypeMax[i] * .3:
                    beatTypeHit[i] = False

            if any(beatTypeHit[:4]):
                beat = True

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
