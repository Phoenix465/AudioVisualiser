from glm import vec2, vec4
from pygame.image import load

import extra
import quadHandler
import texture


class NumberShower:
    def __init__(self, shader, basePath, digitHeight, topLeftVector, displayV, maxDigitLength: int = 8, defaultNumber: str=None,
                 imageSpacingMultiplier=0.75, extraImagePaths=None):
        self.loadedNumberImages, imageLoadsPaths = texture.loadAnimation(basePath, returnImage=True)

        baseImage = load(imageLoadsPaths[0])

        self.currentNumberString = "0" * maxDigitLength

        self.imageSize = texture.GetImageScaleSize(baseImage, digitHeight, displayV)
        self.imageSpacing = self.imageSize * vec2(imageSpacingMultiplier, 1)

        self.digitQuads = []
        self.digitShowMask = [1] * maxDigitLength

        self.extraImagePath = extraImagePaths or {}
        self.extraImages = {}
        for key, path in self.extraImagePath.items():
            self.extraImages[key] = texture.loadTexture(path)

        for i in range(maxDigitLength):
            newNumberQuad = quadHandler.Quad(
                shader,
                extra.generateRectangleCoordsTopLeft(topLeftVector + vec2(i*self.imageSpacing.x, 0), self.imageSize),
                vec4(1, 1, 1, 1),
                self.loadedNumberImages[i],
            )

            self.digitQuads.append(newNumberQuad)

        if defaultNumber:
            self.setNumber(defaultNumber)

    def setNumber(self, num: str):
        for i, char in enumerate(num):
            if char == "-":
                self.digitShowMask[i] = 0
            elif char in self.extraImages:
                self.digitShowMask[i] = 1
                self.digitQuads[i].changeTexture(self.extraImages[char])
            else:
                self.digitShowMask[i] = 1
                self.digitQuads[i].changeTexture(self.loadedNumberImages[int(char)])

    def draw(self):
        for i, quad in enumerate(self.digitQuads):
            if self.digitShowMask[i]:
                quad.draw()
