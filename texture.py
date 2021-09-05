from os.path import exists, splitext

import pygame
import pygame.image as image
from OpenGL.GL import *
from glm import vec2
from pygame import BLEND_RGBA_MULT


def loadTexture(imagePath, alpha=0, imageLoad=None):
    oldTextureSurface = imageLoad or image.load(imagePath).convert_alpha()

    width = oldTextureSurface.get_width()
    height = oldTextureSurface.get_height()

    textureSurface = oldTextureSurface.copy()
    if alpha != 0:
        textureSurface.fill((255, 255, 255, alpha), None, special_flags=BLEND_RGBA_MULT)
    # textureSurface.fill((0, 255, 100))

    textureData = image.tostring(textureSurface, "RGBA", True)

    # glEnable(GL_TEXTURE_2D)
    textureId = glGenTextures(1)
    # https://learnopengl.com/Advanced-OpenGL/Anti-Aliasing

    glBindTexture(GL_TEXTURE_2D, textureId)

    # glPixelStorei(GL_UNPACK_ALIGNMENT, 1)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, textureData)

    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)

    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)

    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)

    glGenerateMipmap(GL_TEXTURE_2D)

    glBindTexture(GL_TEXTURE_2D, 0)

    return textureId


def loadAnimation(imageFirstPath, returnImage=False):  # Example: menu-back@2x.png
    pathSplit = splitext(imageFirstPath)
    imageFormat = pathSplit[0] + "{||}" + pathSplit[1]

    if "@2x" in imageFormat:
        imageFormat = imageFormat.replace("@2x{||}", "{||}@2x", 1)

    imageLoads = []  # Ignore First
    animationTextures = []

    i = 0
    while True:
        newImagePath = imageFormat.replace(r"{||}", f"-{i}", 1)

        if not exists(newImagePath):
            break

        imageLoads.append(newImagePath)

        i += 1

    for imageLoadPath in imageLoads:
        animationTextures.append(loadTexture(imageLoadPath))

    if not returnImage:
        return animationTextures
    else:
        return animationTextures, imageLoads


def GenFontSurface(text, fontPath, fontLoad=None, customColour=None):
    font = fontLoad or pygame.font.Font(fontPath, 128)
    textSurface = font.render(text, True, customColour or (255, 255, 255, 255))

    return textSurface


def GenTextureForText(text, fontPath, fontLoad=None):
    ## https://stackoverflow.com/questions/29015999/pygame-opengl-how-to-draw-text-after-glbegin

    font = fontLoad or pygame.font.Font(fontPath, 64)
    textSurface = font.render(text, True, (255, 255, 255, 255))

    width, height = textSurface.get_width(), textSurface.get_height()
    textureData = pygame.image.tostring(textSurface, "RGBA", True)
    # glPixelStorei(GL_UNPACK_ALIGNMENT, 1)

    textureId = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, textureId)

    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, textureData)

    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)

    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)

    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)

    #glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_DECAL)

    glBindTexture(GL_TEXTURE_2D, 0)

    return textureId


def GetImageScaleSize(image, scale, displayV, heightWidthScale=True, tuple=False):
    if heightWidthScale:
        lengthP = scale * displayV.y

        sizeRatio = image.get_width() / image.get_height()
        oLengthP = sizeRatio * lengthP
        oLength = oLengthP / displayV.x

        if tuple:
            return oLength, scale
        else:
            return vec2(oLength, scale)

    else:
        lengthP = scale * displayV.x
        sizeRatio = image.get_height() / image.get_width()

        oLengthP = sizeRatio * lengthP
        oLength = oLengthP / displayV.y

        if tuple:
            return scale, oLength
        else:
            return vec2(scale, oLength)


def GenTextTextureSize(title, heightScale, displayV, fontPath, fontLoad=None, customColour=None):
    titleRender = GenFontSurface(title, fontPath, fontLoad=fontLoad, customColour=customColour)  # 22/90 height

    titleHeight = heightScale
    titleHeightP = titleHeight * displayV.y
    titleRatio = titleRender.get_width() / titleRender.get_height()
    titleWidthP = titleRatio * titleHeightP
    titleWidth = titleWidthP / displayV.x
    titleSize = vec2(titleWidth, titleHeight)

    titleTexture = loadTexture("", imageLoad=titleRender)

    return titleTexture, titleSize