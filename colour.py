import colorsys

import line_profiler_pycharm

from errors import *

functionDict = {
    "+": lambda a, b: a + b,
    "-": lambda a, b: a - b,
    "*": lambda a, b: a * b,
    "/": lambda a, b: a / b,
}

operationText = {
    "+": ["Added", "Addition"],
    "-": ["Subtracted", "Subtraction"],
    "*": ["Multiplied", "Multiplication"],
    "/": ["Divided", "Division"],
}

errorRange = False


class Colour:
    #@line_profiler_pycharm.profile
    def __init__(self, r, g, b, isHSV=False, convertToDecimal=False, alpha: float = 0):
        """if type(r) != int and type(r) != float:
            raise ColourError("R/H Has To Be Of Class int/float")
        if type(g) != int and type(g) != float:
            raise ColourError("G/S Has To Be Of Class int/float")
        if type(b) != int and type(b) != float:
            raise ColourError("B/V Has To Be Of Class int/float")"""

        if convertToDecimal:
            r /= 255
            g /= 255
            b /= 255

        if errorRange:
            if r > 1 or r < 0:
                raise ColourError("R/H Has To Be Between 0 & 1")
            if g > 1 or g < 0:
                raise ColourError("G/S Has To Be Between 0 & 1")
            if b > 1 or b < 0:
                raise ColourError("B/V Has To Be Between 0 & 1")

        if not isHSV:
            self._r = r
            self._g = g
            self._b = b
        else:
            self._r, self._g, self._b = colorsys.hsv_to_rgb(r, g, b)

        self.alpha = alpha

        self.RGBList = [self.r, self.g, self.b]
        self.RGBAList = [self.r, self.g, self.b, self.alpha]

        self.RGBTuple = tuple(self.RGBList)

    @property
    def r(self):
        return self._r

    @property
    def g(self):
        return self._g

    @property
    def b(self):
        return self._b

    @r.setter
    def r(self, newVal):
        raise ColourError("Cannot Edit r Attribute")

    @g.setter
    def g(self, newVal):
        raise ColourError("Cannot Edit g Attribute")

    @b.setter
    def b(self, newVal):
        raise ColourError("Cannot Edit b Attribute")

    def equals(self, other):
        return self.r == other.r and self.g == other.g and self.b == other.b

    def __eq__(self, other):
        return self.equals(other)

    def __repr__(self):
        return f"Colour3 R:{int(self.r*255)} G:{int(self.g*255)} B:{int(self.b*255)}"


if __name__ == "__main__":
    for x in range(1000):
        testColour = Colour(x/1000, 1, 2, isHSV=True, alpha=1)
