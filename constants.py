from collections import namedtuple

SPACING =  50
LINECOLOR = "#80ccff"
BGCOLOR = "#ffffff"
LINEWIDTH = 2
ZOOM_SPEED = .1
POINT_SIZE = 4
WIRE_SIZE = 3
MAX_ZOOM = 5
MIN_ZOOM = .6
N = 0
S = 1
E = 2
W = 3
DEFAULT_WIDTH = 800
DEFAULT_HEIGHT = 600

Bbox = namedtuple("Bbox", ("width", "height"))