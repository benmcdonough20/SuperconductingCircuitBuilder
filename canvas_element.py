from constants import *

class CanvasElement:
    
    layer = BOTTOM
    
    def __init__(self, x, y, canvas, bbox = None, rot = 0):
        self.x = x
        self.y = y
        self.rot = rot
        self.canvas = canvas
        if not bbox:
            self.bbox = Bbox(SPACING/2,SPACING/2)
        self.canvas.add_object(self)

    def draw(self):
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