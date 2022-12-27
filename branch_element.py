from constants import *
from canvas_element import CanvasElement
from node import Node
from connection import Connection
import numpy as np
from PyQt6.QtGui import QIcon, QTransform, QPen, QColorConstants
from math import pi
from numpy.linalg import matrix_power

class BranchElement(CanvasElement):

    def __init__(self, x, y, canvas, s = 1):

        super().__init__(x*SPACING, y*SPACING, canvas)

        self.clickable = True

        self.properties = {}
        self.w = 75
        self.h = 75

        self.nodes = []
        self.nodes.append(Node(self.x+SPACING*2, self.y, canvas))
        self.nodes.append(Node(self.x-SPACING*2, self.y, canvas))

        self.connections = []
        self.connections.append(Connection(self, self.nodes[0], [s,0], canvas))
        self.connections.append(Connection(self, self.nodes[1], [-s,0], canvas))

        for node, connection in zip(self.nodes, self.connections):
            node.connections.append(connection)

        for node in self.nodes:
            node.elements.append(self)

        self.disps = []

    def __str__(self):
        props_rep = []
        for prop in self.properties:
            props_rep.append(f"{self.properties[prop]},")
        props_string = "".join(props_rep)
        props_string = props_string[:-1]
        return f"- [{self.name},{self.nodes[0].idx},{self.nodes[1].idx},{props_string}]"

    def paint(self, painter):
        for i, prop in enumerate(self.properties):
            painter.drawText(SPACING+self.x, int(self.y-SPACING-i*FONTSIZE*1.5), str(prop) + " = "+str(self.properties[prop]))
        
        width = self.bbox.width
        height = self.bbox.height
        if self.rot % 2== 0:
            disp = [SPACING, 0]
        else:
            disp = [0,SPACING]
        painter.drawPixmap(int(self.x-width/2-disp[0]/2), int(self.y-height/2-disp[1]/2), int(width+disp[0]), int(height+disp[1]), self.icon)

    def in_bbox(self,x,y):
        self.disps.clear()
        for node in self.nodes:
            self.disps.append((node.x-self.x, node.y-self.y))
        return super().in_bbox(x,y)

    def drag(self, x, y):
        super().drag(x,y)
        for node,disp in zip(self.nodes,self.disps):
            if len(node.elements) == 1 and all([len(conn.anchors)==0 for conn in node.connections]):
                node.drag(disp[0]+self.x, disp[1]+self.y)
    
    def setIcon(self, path, width, height):
        self.icon = QIcon(path).pixmap(width*IMG_RES_FACTOR, height*IMG_RES_FACTOR)
        self.bbox = Bbox(width, height)

    def rotate(self):
        super().rotate() 
        for connection in self.connections:
            d = np.array(connection.d)
            d = d @ [[0,-1],[1,0]]
            
            connection.d = list(d)
            connection.rewire()
    
        rotatemat = QTransform() 
        rotatemat.rotate(self.rot* 90)
        self.icon = self.icon.transformed(rotatemat)
        self.bbox = Bbox(self.icon.width(), self.icon.height())
        
        
        for node in self.nodes:
            if len(node.elements) == 1 and all([len(conn.anchors)==0 for conn in node.connections]):
                node.x -= self.x
                node.y -= self.y
                (node.x,node.y) = np.array([node.x, node.y]) @ np.array([[0,-1],[1,0]])
                node.x += self.x
                node.y += self.y
                node.rotate()
        
        
class Capacitor(BranchElement):

    layer = TOP
    name = "C"

    def __init__(self, x, y, canvas):
        super().__init__(x, y, canvas)
        self.C = .02
        self.properties["C"] = self.C
        self.setIcon("./capacitor.svg", SPACING, SPACING)



class JosephsonJunction(BranchElement):

    layer = TOP
    name = "JJ"

    def __init__(self, x, y, canvas):
        super().__init__(x, y, canvas)
        self.EJ = 21
        self.EC = 1.2
        self.properties["EC"] = self.EC
        self.properties["EJ"] = self.EJ
        self.setIcon("./JJ.svg", SPACING, SPACING)

class Inductor(BranchElement):

    layer = TOP
    name = "L"

    def __init__(self, x, y, canvas):
        super().__init__(x, y, canvas, s = 2)
        self.L = 1.2
        self.properties["L"] = self.L
        self.setIcon("./Inductor.svg", SPACING*3, SPACING)

        

