import ctypes
from math import cos as radCos
from math import pi
from math import sin as radSin

from glm import vec2

user32 = ctypes.windll.user32


def degSin(angle):
    return radSin(angle * pi / 180)


def degCos(angle):
    return radCos(angle * pi / 180)


def generateCircleCorners(circlePos: vec2, cursorSize: float):
    return [circlePos + vec2(-1, 1) * (cursorSize / 2),  # Top Left
            circlePos + vec2(1, 1) * (cursorSize / 2),  # Top Right
            circlePos + vec2(1, -1) * (cursorSize / 2),  # Bottom Right
            circlePos + vec2(-1, -1) * (cursorSize / 2)  # Bottom Left
            ]


def generateCircleCornersRotation(circlePos: vec2, cursorSize: float, rotation: float):
    normalPoints = generateCircleCorners(vec2(0, 0), cursorSize)

    relPoints = [vec2(
        point.X*degCos(rotation) - point.Y*degSin(rotation),
        point.X*degSin(rotation) + point.Y*degCos(rotation)
    ) for point in normalPoints]

    return [circlePos + point for point in relPoints]


def generateRectangleCoords(anchorPoint: vec2, size: vec2):
    return [anchorPoint + vec2(-1, 1) * (size / 2),
            anchorPoint + vec2(1, 1) * (size / 2),
            anchorPoint + vec2(1, -1) * (size / 2),
            anchorPoint + vec2(-1, -1) * (size / 2)
            ]


def generateRectangleCoordsTopLeft(offset, size):
    return [
               offset + vec2(0, size.y),
               offset + vec2(size.x, size.y),
               offset + vec2(size.x, 0),
               offset + vec2(0, 0)
    ]


def translate(value, leftMin, leftMax, rightMin, rightMax):
    # Figure out how 'wide' each range is
    leftSpan = leftMax - leftMin
    rightSpan = rightMax - rightMin

    # Convert the left range into a 0-1 range (float)
    valueScaled = float(value - leftMin) / float(leftSpan)

    # Convert the 0-1 range into a value in the right range.
    return rightMin + (valueScaled * rightSpan)


def getMonitorSize():
    return user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)
