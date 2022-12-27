from constants import *
from PyQt6.QtGui import QColorConstants, QPen

class CanvasElement:
    
    def __init__(self, x, y, canvas):
        self.x = x #int specifying x position on grid
        self.y = y #int specigying y position on grid
        self.rot = 0 #four different orientations
        self.bbox = Bbox(SPACING, SPACING)
        self.clickable = False
        self.width = SPACING
        self.canvas = canvas
        canvas.add_object(self)

    def paint(self, painter):
        color = QColorConstants.Black
        if self.active:
            color = QColorConstants.Red
        pen = QPen(color, 3)
        painter.setPen(pen)
        painter.drawRect(int(self.x-self.width/2),int(self.y-self.width/2),SPACING,SPACING)

    def rotate(self):
        self.rot = (self.rot+1)%4

    def in_bbox(self, x, y):
        if not self.bbox:
            return None
        if (x > self.x-self.bbox.width/2 and x < self.x + self.bbox.width/2 and y > self.y-self.bbox.height/2 and y < self.y+self.bbox.height/2):
            return self
        return None

    def drag(self, x, y):
        self.x = SPACING*round(x/SPACING)
        self.y = SPACING*round(y/SPACING)
    
    def press(self, x, y):
        pass
    
    def drop(self, x, y, other):
        pass