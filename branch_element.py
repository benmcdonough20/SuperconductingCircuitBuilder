from constants import *
from canvas_element import CanvasElement
from node import Node
from connection import Connection
import numpy as np

class BranchElement(CanvasElement):

    layer = TOP

    def __init__(self, x, y, canvas, s = 1):

        self.properties = {}

        super().__init__(x*SPACING, y*SPACING, canvas)
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

    def draw(self):
        for i, prop in enumerate(self.properties):
            self.canvas.rel_text(SPACING+self.x, self.y-SPACING-i*FONTSIZE*1.5, str(prop) + " = "+str(self.properties[prop]), fill = self.color)

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


    def rotate(self):
        super().rotate() 
        for connection in self.connections:
            d = np.array(connection.d)
            d = d @ [[0,-1],[1,0]]
            
            connection.d = list(d)
            connection.rewire()
        
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


    def draw(self):
        super().draw()
        if self.rot == 1 or self.rot == 3:
            self.canvas.rel_line(self.x, self.y+SPACING, self.x, self.y-SPACING, width =3, fill = self.color)
            self.canvas.rel_line(self.x+SPACING*.75, self.y-5, self.x-SPACING*.75, self.y-5, width = 4, fill = self.color)
            self.canvas.rel_line(self.x+SPACING*.75, self.y+5, self.x-SPACING*.75, self.y+5, width =4, fill = self.color)
            self.canvas.rel_box(self.x+SPACING*.75, self.y+3, self.x-SPACING*.75, self.y-3,fill="white",width=0)

        if self.rot == 0 or self.rot == 2:
            self.canvas.rel_line(self.x+SPACING, self.y, self.x-SPACING, self.y, width =3, fill = self.color)
            self.canvas.rel_line(self.x+5, self.y+SPACING*.75, self.x+5, self.y-SPACING*.75, width=4, fill = self.color)
            self.canvas.rel_line(self.x-5, self.y+SPACING*.75, self.x-5, self.y-SPACING*.75, width =4, fill = self.color)
            self.canvas.rel_box(self.x+3, self.y+SPACING*.75, self.x-3, self.y-SPACING*.75,fill="white",width=0)



class JosephsonJunction(BranchElement):

    layer = TOP
    name = "JJ"

    def __init__(self, x, y, canvas):
        super().__init__(x, y, canvas)
        self.EJ = 21
        self.EC = 1.2
        self.properties["EC"] = self.EC
        self.properties["EJ"] = self.EJ

    def draw(self):
        super().draw()
        if self.rot == 1 or self.rot == 3:
            self.canvas.rel_line(self.x, self.y+SPACING, self.x, self.y-SPACING, width =3, fill = self.color)

        if self.rot == 0 or self.rot == 2:
            self.canvas.rel_line(self.x+SPACING, self.y, self.x-SPACING, self.y, width =3, fill = self.color)
       
        self.canvas.rel_box(self.x-SPACING*.75, self.y-SPACING*.75, self.x+SPACING*.75, self.y+SPACING*.75, fill="white", width = 4) 
        self.canvas.rel_line(self.x-SPACING*.75, self.y-SPACING*.75, self.x+SPACING*.75, self.y+SPACING*.75, width = 4, fill = self.color) 
        self.canvas.rel_line(self.x+SPACING*.75, self.y-SPACING*.75, self.x-SPACING*.75, self.y+SPACING*.75, width = 4, fill = self.color) 

        

class Inductor(BranchElement):

    layer = TOP
    name = "L"

    def __init__(self, x, y, canvas):
        super().__init__(x, y, canvas, s = 2)
        self.L = 1.2
        self.properties["L"] = self.L



    def draw(self):
        super().draw()
        if self.rot == 0 or self.rot == 2:
            for i in range(3):
                self.canvas.rel_arc(self.x-SPACING+i*SPACING, self.y, SPACING/2, 0, 180, width = 3)
                self.canvas.rel_box(self.x-SPACING*1.5+i*SPACING, self.y-2,self.x-SPACING*1.5+(i+1)*SPACING ,self.y+2, fill = "white", width = 0)
            self.canvas.rel_line(self.x+SPACING*1.5, self.y, self.x+SPACING*2, self.y, width =3, fill = self.color)
            self.canvas.rel_line(self.x-SPACING*1.5, self.y, self.x-SPACING*2, self.y, width =3, fill = self.color)

        if self.rot == 1 or self.rot == 3:
            for i in range(3):
                self.canvas.rel_arc(self.x, self.y-SPACING + i*SPACING, SPACING/2, 90,180, width = 3)
                self.canvas.rel_box(self.x-2, self.y-SPACING*1.5 + i*SPACING, self.x+2, self.y+SPACING*1.5, fill = "white", width = 0)
            self.canvas.rel_line(self.x, self.y+SPACING*1.5, self.x, self.y+SPACING*2, width =3, fill = self.color)
            self.canvas.rel_line(self.x, self.y-SPACING*1.5, self.x, self.y-SPACING*2, width =3, fill = self.color)

