import colorsys
from degreesMath import *
from vector import *
from colour import *
import VBOHandler


class Circle:
    def __init__(self, shader, centre, radius, edgeCount):
        self.vertices = []
        self.colours = []

        for i in range(edgeCount):
            angle = i/edgeCount * 360

            width = sin(angle) * radius
            height = cos(angle) * radius

            self.vertices.append(
                Vector3(width, height, 0) + centre
            )

            self.colours.append(
                Colour(*colorsys.hsv_to_rgb(i/edgeCount, 1, 1), alpha=0.5)
            )

        self.VBO = VBOHandler.VBO(shader, self.vertices, self.colours)
        self.shader, self.centre, self.radius, self.edgeCount = shader, centre, radius, edgeCount

    def closestVertex(self, pos):
        tempVertices = sorted(self.vertices, key=lambda vertexPos: (vertexPos - pos).magnitude)
        print(tempVertices[0])
        return tempVertices[0]

    def draw(self):
        self.VBO.draw()


class GameObjectHolder:
    def __init__(self):
        self.objects = []
        self.objectOrderIndex = []

    def addObject(self, object):
        if object not in self.objects:
            self.objects.append(object)
            self.objectOrderIndex.append(len(self.objects) - 1)

    def removeObject(self, object):
        if object in self.objects:
            objectIndex = self.objects.index(object)

            del self.objects[objectIndex]

            self.objectOrderIndex = [index for index in self.objectOrderIndex if index != objectIndex]

    def orderObjects(self, cameraPos):
        self.objectOrderIndex.sort(key=lambda index: (self.objects[index].centre - cameraPos).magnitude, reverse=True)

    def draw(self):
        for index in self.objectOrderIndex:
            self.objects[index].draw()
