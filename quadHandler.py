from OpenGL.GL import glDeleteTextures
from glm import vec2

import extra
import texture
from VBOHandler import VBOImage


class Quad:
    def __init__(self,
                 shader,
                 corners,
                 colour,
                 texture):

        self.corners = corners
        self.colours = [colour] * len(self.corners)

        self.texture = texture
        self.textureCorners = [(0, 0), (1, 0), (1, 1), (0, 1)]

        self.VBO = VBOImage(shader, self.corners, self.colours, self.textureCorners, self.texture)

    def edit(self, corners, colour):
        self.corners = corners
        self.colours = [colour] * len(self.corners)

        self.VBO.vertices = self.corners
        self.VBO.colours = self.colours
        self.VBO.update()

    def changeTexture(self, newTexture):
        self.texture = newTexture
        self.VBO.texture = newTexture

    def draw(self):
        self.VBO.draw()


class TextQuad:
    def __init__(self, shader, text, fontPath, topLeft, height, displayV, colour, isTopRight=False):
        self.height = height
        self.displayV = displayV
        self.fontPath = fontPath
        self.colour = colour
        self.topLeft = topLeft
        self.isTopRight = isTopRight

        self.text = text
        self.textTexture, textSize = texture.GenTextTextureSize(text,
                                                                height,
                                                                displayV,
                                                                fontPath,
                                                                customColour=colour
                                                                )

        self.quad = Quad(shader,
                         extra.generateRectangleCoordsTopLeft(topLeft, textSize)
                         if not self.isTopRight else
                         extra.generateRectangleCoordsTopLeft(self.topLeft - vec2(textSize.x, 0), textSize),
                         colour,
                         self.textTexture
                         )

    def changeText(self, newText):
        if newText != self.text:
            self.text = newText

            self.textTexture, textSize = texture.GenTextTextureSize(self.text,
                                                                    self.height,
                                                                    self.displayV,
                                                                    self.fontPath,
                                                                    customColour=self.colour
                                                                    )

            oldTexture = self.quad.texture
            glDeleteTextures(1, [oldTexture])

            self.quad.changeTexture(self.textTexture)
            self.quad.edit(extra.generateRectangleCoordsTopLeft(self.topLeft, textSize)
                           if not self.isTopRight else
                           extra.generateRectangleCoordsTopLeft(self.topLeft-vec2(textSize.x, 0), textSize),
                           self.colour)

    def draw(self):
        self.quad.draw()
