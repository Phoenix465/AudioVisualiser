from math import floor
from time import time

import glm
import numpy as np
import pyaudio
import pygame
from OpenGL.GL import *
from pygame import DOUBLEBUF, OPENGL
from pygame import GL_MULTISAMPLEBUFFERS, GL_MULTISAMPLESAMPLES

import GameObjects
import ShaderLoader
import audio
import gamePaths
import numberShower
import quadHandler
from degreesMath import *


#  ffmpeg -i "No.1 - Kobasolo.mp3" "No.1 - Kobasolo2.wav"


def main():
    # Initialisation
    pygame.init()
    pygame.mixer.init()
    GamePaths = gamePaths.PathHolder()
    audioFiles = audio.InitializeMusicDirectory(GamePaths.musicPath, GamePaths.oldMP3Files, GamePaths.converterPath, GamePaths.ffmpegPath, GamePaths.ffprobePath)
    for i in range(len(audioFiles)):
        if audioFiles[i] in GamePaths.songPath:
            audioFiles.insert(0, audioFiles.pop(i))

    display = 1366, 768
    displayV = glm.vec2(display)

    pygame.display.gl_set_attribute(GL_MULTISAMPLEBUFFERS, 1)
    pygame.display.gl_set_attribute(GL_MULTISAMPLESAMPLES, 2)

    screen = pygame.display.set_mode(display, DOUBLEBUF | OPENGL)

    pygame.display.set_caption("Audio Visualiser")

    iconSurface = pygame.image.load(GamePaths.iconPath)
    pygame.display.set_icon(iconSurface)

    pygame.display.flip()

    shader = ShaderLoader.compileShaders(*GamePaths.defaultShaderPaths)
    blurShader = ShaderLoader.compileShaders(*GamePaths.blurShaderPaths)
    uiShader = ShaderLoader.compileShaders(*GamePaths.uiShaderPaths)
    glUseProgram(shader)

    uniformModel = glGetUniformLocation(shader, 'uniform_Model')
    uniformView = glGetUniformLocation(shader, 'uniform_View')
    uniformProjection = glGetUniformLocation(shader, 'uniform_Projection')
    uniformLookAtMatrix = glGetUniformLocation(shader, 'lookAtMatrix')

    glUseProgram(blurShader)
    uniformHorizontal = glGetUniformLocation(blurShader, 'horizontal')
    uniformShouldBlur = glGetUniformLocation(blurShader, 'shouldBlur')

    glUseProgram(shader)

    # ----- OpenGL Settings -----
    print(f"OpenGL Version: {glGetString(GL_VERSION).decode()}")

    glMatrixMode(GL_PROJECTION)
    # gluPerspective(70, (displayV.X / displayV.Y), 0.1, 128.0)
    glViewport(0, 0, int(displayV.x), int(displayV.y))
    glMatrixMode(GL_MODELVIEW)

    glEnable(GL_DEPTH_TEST)
    glEnable(GL_MULTISAMPLE)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glDisable(GL_CULL_FACE)
    # glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)

    glClearColor(0, 0, 0, 1.0)
    #glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)

    # ----- Camera Settings -----
    cameraRadius = 8
    cameraPos = glm.vec3(0, 0, cameraRadius)
    cameraFront = glm.vec3(0, 0, 0)
    cameraUp = glm.vec3(0, 1, 0)
    rotationXAngle = 0
    rotationYAngle = 90
    rotationZAngle = 0
    yDirection = 1

    cameraAccel = 0
    cameraVelocityDecay = 0.94
    cameraMinVelocity = 20
    cameraCurrentVelocity = 20

    # ----- Matrix Info -----
    projectionMatrix = glm.perspective(70, displayV.x / displayV.y, 1, 1000.0)
    modelMatrix = glm.mat4(1)

    glUniformMatrix4fv(uniformModel, 1, GL_FALSE,
                       glm.value_ptr(modelMatrix))

    glUniformMatrix4fv(uniformProjection, 1, GL_FALSE,
                       glm.value_ptr(projectionMatrix))
    # ---- Particle Emitter ----
    particleEmitterObject = GameObjects.ParticleEmitter(shader)

    # ---- Sound Stuff -----
    chunkSize = 1024

    musicHandler = audio.SoundHandler(GamePaths.songPath)
    musicUIHandler = audio.SoundUIHandler(uiShader, GamePaths.musicPath, musicHandler, GamePaths.mainFont, displayV, audioFiles)

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

    beatMinThreshold = [0.16, 0.16, 0.16, 0.16, 0.16, 0.16, 0.16]
    beatCutOff = [0, 0, 0, 0, 0, 0, 0]
    beatDecayRate = [0.965 for _ in range(len(beatTypeRanges))]

    frequencies = musicHandler.frameRate * np.arange(chunkSize / 2) / chunkSize

    maxY = 2.0 ** (musicHandler.pyAudioObj.get_sample_size(pyaudio.paInt16) * 8 - 1)

    # ----- Blur Effect -----
    screenFBO = glGenFramebuffers(1)
    glBindFramebuffer(GL_FRAMEBUFFER, screenFBO)

    fboTexture = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, fboTexture)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA16F, displayV.x, displayV.y, 0, GL_RGBA, GL_FLOAT, None)

    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)

    glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, fboTexture, 0)

    glBindFramebuffer(GL_FRAMEBUFFER, 0)
    glBindTexture(GL_TEXTURE_2D, 0)

    pingpongFBO = glGenFramebuffers(2)
    pingpongColourBuffers = glGenTextures(2)

    for i in range(2):
        glBindFramebuffer(GL_FRAMEBUFFER, pingpongFBO[i])
        glBindTexture(GL_TEXTURE_2D, pingpongColourBuffers[i])
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA16F, displayV.x, displayV.y, 0, GL_RGBA, GL_FLOAT, None)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
        glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, pingpongColourBuffers[i], 0)

    # ----- UI -----
    fpsCounter = numberShower.NumberShower(uiShader,
                                           GamePaths.scoreBasePath,
                                           60 / displayV.y,
                                           glm.vec2(1-((3*10+2)/768), 1 - 62 / 768),
                                           displayV,
                                           maxDigitLength=3,
                                           defaultNumber="000")

    updateTime = quadHandler.TextQuad(uiShader, "Update Time: 0ms", GamePaths.mainFont, glm.vec2(displayV.x-5, 5)/displayV, 0.05, displayV, (255, 255, 255, 255), isTopRight=True)

    blurCount = 0

    screenQuad = GameObjects.ScreenQuad()

    times = [0]
    running = True
    clock = pygame.time.Clock()

    stopUpdate = False
    frameCount = 0

    while running:
        deltaT = clock.tick(60)
        s = time() * 1000

        frameCount += 1

        keyPressed = pygame.key.get_pressed()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_e:
                    blurCount = min(blurCount+2, 20)

                elif event.key == pygame.K_q:
                    blurCount = max(blurCount-2, 0)

                elif event.key == pygame.K_SPACE:
                    stopUpdate = not stopUpdate

                elif event.key == pygame.K_r:
                    musicHandler.changeMusic(GamePaths.songPath)

                elif event.key == pygame.K_s:
                    musicUIHandler.shuffleToggle()

                elif event.key == pygame.K_a:
                    musicUIHandler.backSong()

                elif event.key == pygame.K_d:
                    musicUIHandler.nextSong()

                elif event.key == pygame.K_p:
                    musicUIHandler.togglePause()

        if not stopUpdate:
            cameraCurrentVelocity += cameraAccel
            cameraAccel = 0
            cameraCurrentVelocity *= cameraVelocityDecay
            cameraCurrentVelocity = max(cameraCurrentVelocity, cameraMinVelocity)

            rotationXAngle += deltaT / 1000 * cameraCurrentVelocity
            rotationYAngle += deltaT / 1000 * 45 * yDirection
            #rotationZAngle += deltaT / 1000 * 5

        if rotationYAngle > 360:
            rotationYAngle -= 360
        elif rotationYAngle < 0:
            rotationYAngle += 360
            
        if rotationXAngle > 360:
            rotationXAngle -= 360
        elif rotationXAngle < 0:
            rotationXAngle += 360

        if rotationZAngle > 360:
            rotationZAngle -= 360
        elif rotationZAngle < 0:
            rotationZAngle += 360

        """if rotationYAngle < 45:
            rotationYAngle = 45
            yDirection *= -1

        if rotationYAngle > 135:
            rotationYAngle = 135
            yDirection *= -1"""

        adjRotationY = sin(rotationYAngle)*45 + 90

        cameraHeight = sin(adjRotationY+90) * cameraRadius
        cameraAdjRadius = abs(cos(adjRotationY+90)) * cameraRadius

        cameraPos = glm.vec3(sin(rotationXAngle) * cameraAdjRadius, cameraHeight, cos(rotationXAngle) * cameraAdjRadius)
        #cameraUp = (sin(rotationZAngle), cos(rotationZAngle), 0)

        viewMatrix = glm.lookAt(cameraPos,
                                cameraFront,
                                cameraUp)

        particleLookMatrix = glm.mat4(1)

        yRotation = glm.rotate(particleLookMatrix, glm.radians(adjRotationY+90), (1, 0, 0))
        xRotation = glm.rotate(particleLookMatrix, glm.radians(rotationXAngle), (0, 1, 0))

        particleLookMatrix = xRotation * yRotation

        beat = False
        averageAmplitude = 0

        if musicHandler.soundDataHolder.rewind:
            print("Rewinding")

            musicHandler.soundDataHolder.rewind = False
            musicHandler.changeMusic(GamePaths.songPath)

        if len(musicHandler.soundDataHolder.data) > 0 and not musicHandler.soundDataHolder.read:
            #  https://github.com/WarrenWeckesser/wavio/blob/cff688a318173a2bc700297a30a70858730b901f/wavio.py
            #  https://github.com/maxemitchell/portfolio/blob/master/src/pages/code_art/thanksgiving_break/index.js
            #  https://github.com/maxemitchell/beat-detection-python/blob/master/beat-detector.py

            musicHandler.soundDataHolder.read = True
            soundData = musicHandler.soundDataHolder.data

            audioArrayData = audio.audioDataToArray(soundData, musicHandler.sampleWidth, musicHandler.channels)
            audioFFT = np.abs((np.fft.fft(audioArrayData)[:int(len(audioArrayData) / 2)]) / len(audioArrayData))

            averageAmplitude = np.average(audioFFT)  # average

            beatTypeIndices = [
                [frequencyI for frequencyI, frequency in enumerate(frequencies)
                 if frequency >= lowerB and frequency < upperB] for lowerB, upperB in beatTypeRanges
            ]

            beatMaxFFT = [np.max(audioFFT[beatIndexRange]) for beatIndexRange in beatTypeIndices]
            beatTypeMax = [max(beatMax, beatTypeMax[i]) for i, beatMax in enumerate(beatMaxFFT)]

            for i, beatMax in enumerate(beatMaxFFT[:3]):
                if beatMax >= beatTypeMax[i] * beatCutOff[i] and beatMax >= beatTypeMax[i] * beatMinThreshold[i]:
                    beatCutOff[i] = 1
                    cameraAccel = 35
                    beat = True
                else:
                    beatCutOff[i] *= beatDecayRate[i]
                    beatCutOff[i] = max(beatCutOff[i], beatMinThreshold[i])

        if not stopUpdate:
            # At 3000 particles, 23 ms to update
            particleEmitterObject.update(deltaT, pygame.time.get_ticks(), push=beat, avgAmplitude=averageAmplitude)

            #  At 3000 particles, 4ms to sort, 3ms to draw
            if frameCount % 2 == 0:
                particleEmitterObject.sort(cameraPos)

        glBindFramebuffer(GL_FRAMEBUFFER, screenFBO)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glUseProgram(shader)

        glUniformMatrix4fv(uniformView, 1, GL_FALSE,
                           glm.value_ptr(viewMatrix))

        glUniformMatrix4fv(uniformLookAtMatrix, 1, GL_FALSE,
                           glm.value_ptr(particleLookMatrix))

        particleEmitterObject.draw()

        glBindFramebuffer(GL_FRAMEBUFFER, 0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        glUseProgram(blurShader)
        horizontal = True
        firstIteration = True

        glUniform1i(uniformShouldBlur, blurCount != 0)

        for i in range(2):
            glBindFramebuffer(GL_FRAMEBUFFER, pingpongFBO[i])
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        for i in range(blurCount):
            glBindFramebuffer(GL_FRAMEBUFFER, pingpongFBO[int(horizontal)])
            glClear(GL_COLOR_BUFFER_BIT)

            glUniform1i(uniformHorizontal, horizontal)
            glBindTexture(GL_TEXTURE_2D, firstIteration and fboTexture or pingpongColourBuffers[int(not horizontal)])

            screenQuad.draw()

            horizontal = not horizontal
            firstIteration = False

        glBindFramebuffer(GL_FRAMEBUFFER, 0)
        glClear(GL_COLOR_BUFFER_BIT)

        glBindTexture(GL_TEXTURE_2D, blurCount != 0 and pingpongColourBuffers[int(not horizontal)] or fboTexture)
        screenQuad.draw()
        glBindTexture(GL_TEXTURE_2D, 0)

        fps = str(floor(clock.get_fps()))

        glUseProgram(uiShader)
        fpsCounter.setNumber(fps + "-"*(3-len(fps)))
        fpsCounter.draw()

        if frameCount % 10 == 0:
            tempTimes = times[-60:]
            updateTime.changeText(f"Update Time: {floor(sum(tempTimes)/len(tempTimes))}ms")
        updateTime.draw()

        musicUIHandler.update(frameCount)
        musicUIHandler.draw()

        pygame.display.flip()

        e = time() * 1000
        ft = e - s
        times.append(ft)

    print("Average ms Per Frame", sum(times) / len(times))


if __name__ == "__main__":
    """import cProfile, pstats

    profiler = cProfile.Profile()
    profiler.enable()
    main()
    profiler.disable()
    stats = pstats.Stats(profiler).sort_stats('cumtime')
    stats.print_stats()"""

    main()
