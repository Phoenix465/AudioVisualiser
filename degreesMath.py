"""
Custom Math Class that uses Degrees instead of Radians

"""

from math import sin as oSin
from math import cos as oCos
from math import tan as oTan
from math import asin as oASin
from math import acos as oACos
from math import atan as oATan

from math import pi


def sin(angle: float):
    return oSin(angle * pi / 180)


def cos(angle: float):
    return oCos(angle * pi / 180)


def tan(angle: float):
    return oTan(angle * pi / 180)


def asin(division: float):
    return oASin(division) * 180 / pi


def acos(division: float):
    return oACos(division) * 180 / pi


def atan(division: float):
    return oATan(division) * 180 / pi


def average(*args):
    return sum(args) / len(args)


def pythagoras(a, b):
    return (a ** 2 + b ** 2) ** 0.5


def sign(num: float):
    if num == 0:
        return 1
    elif num > 0:
        return 1
    elif num < 0:
        return -1
