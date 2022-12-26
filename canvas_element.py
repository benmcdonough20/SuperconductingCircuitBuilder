from constants import *
from PyQt6.QtWidgets import QGraphicsItem

class CanvasElement(QGraphicsItem):
    
    def __init__(self, x, y, rot, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ACTIVE = False
        self.x = x #int specifying x position on grid
        self.y = y #int specigying y position on grid
        self.rot = rot #four different orientations

    def paint(self, *args, **kwargs):
        raise NotImplementedError

    def rotate(self):
        self.rot = (self.rot+1)%4

    def in_bbox(self, x, y):
        if not self.bbox:
            return False
        if (x > self.x-self.bbox.width and x < self.x + self.bbox.width and y > self.y-self.bbox.height and y < self.y+self.bbox.height):
            return True
        return False

    def drag(self, x, y):
        self.x = SPACING*round(x/SPACING)
        self.y = SPACING*round(y/SPACING)