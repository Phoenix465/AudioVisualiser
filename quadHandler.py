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
