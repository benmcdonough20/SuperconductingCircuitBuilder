from canvas_element import CanvasElement
from constants import *
from math import sin, cos, pi


class Node(CanvasElement):

    layer = TOP

    def __init__(self, x, y, canvas, rot = 0):
        super().__init__(x, y, canvas, rot = rot)
        self.elements = []
        self.connections = []

    def merge(self, other):
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

    def draw(self):
        self.canvas.rel_point(self.x, self.y, fill="red",width=0)
         
class Ground(Node):

    Layer = TOP

    def draw(self):
        p1 = (self.x+SPACING/2*cos(self.rot*pi/2), self.y+SPACING/2*sin(self.rot*pi/2))
        p2 = (self.x+SPACING/2*sin(self.rot*pi/2), self.y+SPACING/2*cos(self.rot*pi/2))
        p3 = (self.x-SPACING/2*cos(self.rot*pi/2), self.y-SPACING/2*sin(self.rot*pi/2))

        self.canvas.rel_poly(p1,p2,p3, width = 3)