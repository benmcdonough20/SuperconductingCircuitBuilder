from collections import namedtuple
from PySide2.QtCore import QSize 
from PySide2.QtGui import QColorConstants
import numpy as np

class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __mul__(self, other):
        if type(other) is list or type(other) is np.ndarray:
            x,y = np.array([self.x, self.y]) @ other
            return Point(x,y)
        elif type(other) is int or type(other) is float:
            return Point(self.x*other, self.y*other)
        else:
            raise Exception("Type", str(type(other)))
        
    def __rmul__(self, other):
        return self.__mul__(other)
    
    def __sub__(self, other):
        return Point(self.x-other.x, self.y-other.y)

    def __add__(self, other):
        return Point(self.x+other.x, self.y+other.y)
    
    def snaptogrid(self):
        return Point(round(self.x/SPACING)*SPACING, round(self.y/SPACING)*SPACING)

SPACING =  50
BGCOLOR = QColorConstants.White
NODE_SIZE = 6
ZOOM_SPEED = .001
POINT_SIZE = 4
WIRE_SIZE = 3
MAX_ZOOM = 5
MIN_ZOOM = .3
DEFAULT_WIDTH = 800
DEFAULT_HEIGHT = 600
FONTSIZE = 10
IMG_RES_FACTOR = 5
ICON_SIZE = 100
MINSIZE = QSize(1000,600)
ORIGIN = Point(0,0)
DROP_DISPLACEMENT = Point(50,50)
ROT_MAT = [[0,-1],[1,0]]

Bbox = namedtuple("Bbox", ("width", "height"))