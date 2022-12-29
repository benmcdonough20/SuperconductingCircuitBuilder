from constants import *
from PyQt6.QtGui import QColorConstants, QPen

class CanvasElement:
    
    def __init__(self, point):
        self.x = point.x #int specifying x position on grid
        self.y = point.y #int specigying y position on grid
        self.rot = 0 #four different orientations
        self.bbox = Bbox(SPACING, SPACING)

    def paint(self, painter):
        color = QColorConstants.Black
        if self.active:
            color = QColorConstants.Red
        pen = QPen(color, 3)
        painter.setPen(pen)
        painter.drawRect(int(self.x-self.width/2),int(self.y-self.width/2),SPACING,SPACING)

    def rotate(self):
        self.rot = (self.rot+1)%4

    def in_bbox(self, point):
        if not self.bbox:
            return False
        if (point.x > self.x-self.bbox.width/2 and point.x < self.x + self.bbox.width/2 \
            and point.y > self.y-self.bbox.height/2 and point.y < self.y+self.bbox.height/2):
            return True
        return False

    def drag(self, point):
        self.x = point.snaptogrid().x
        self.y = point.snaptogrid().y
    
    def press(self, point):
        pass
    
    def drop(self, point, other):
        pass