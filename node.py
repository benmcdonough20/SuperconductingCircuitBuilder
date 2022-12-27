from canvas_element import CanvasElement
from constants import *
from math import sin, cos, pi
from PyQt6.QtGui import QPen, QColorConstants


class Node(CanvasElement):

    layer = TOP

    def __init__(self, x, y, canvas, idx=0):
        super().__init__(x, y, canvas)
        self.idx = idx
        self.elements = []
        self.connections = []
        self.clickable = True

    def drop(self, x, y, other):
        self.canvas.remove_object(other)
        self.connections += other.connections
        self.elements += other.elements
        for conn in other.connections:
            conn.dest = self
        for elem in other.elements:
            for i,node in enumerate(elem.nodes):
                if node == other:
                    elem.nodes[i] = self
   
    def drag(self, x, y):
        super().drag(x, y)
        for conn in self.connections:
            conn.rewire()

    def paint(self, painter):
        pen = QPen(QColorConstants.Black, 6)
        painter.setPen(pen)
        painter.drawText(self.x+FONTSIZE, self.y-FONTSIZE, str(self.idx))
        painter.drawPoint(self.x, self.y)
         
class Ground(Node):

    Layer = TOP

    def paint(self):
        p1 = (self.x+SPACING/2*cos(self.rot*pi/2), self.y+SPACING/2*sin(self.rot*pi/2))
        p2 = (self.x+SPACING/2*sin(self.rot*pi/2), self.y+SPACING/2*cos(self.rot*pi/2))
        p3 = (self.x-SPACING/2*cos(self.rot*pi/2), self.y-SPACING/2*sin(self.rot*pi/2))

        self.canvas.drawPolygon(p1,p2,p3)