from dataclasses import dataclass
from errors import InvalidColorValueError

@dataclass
class RGB:
    r: int
    g: int
    b: int
    def __post_init__(self):
        for name, val in [('R', self.r), ('G', self.g), ('B', self.b)]:
            if not (0 <= val <= 255): 
                raise InvalidColorValueError(name, val, 0, 255)

@dataclass
class CMYK:
    c: int
    m: int
    y: int
    k: int
    def __post_init__(self):
        for name, val in [('C', self.c), ('M', self.m), ('Y', self.y), ('K', self.k)]:
            if not (0 <= val <= 100): 
                raise InvalidColorValueError(name, val, 0, 100)

@dataclass
class HSV:
    h: int
    s: int
    v: int
    def __post_init__(self):
        if not (0 <= self.h <= 360): 
            raise InvalidColorValueError('H', self.h, 0, 360)
        
        for name, val in [('S', self.s), ('V', self.v)]:
            if not (0 <= val <= 100): 
                raise InvalidColorValueError(name, val, 0, 100)