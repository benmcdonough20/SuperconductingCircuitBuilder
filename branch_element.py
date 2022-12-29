from constants import *
from canvas_element import CanvasElement
from node import Node, Ground
from connection import Connection
import numpy as np
from PyQt6.QtGui import QIcon, QTransform, QPen, QColorConstants, QAction
from PyQt6.QtWidgets import QToolBar, QWidget, QLabel, QLineEdit, QHBoxLayout, QSpacerItem, QSizePolicy, QPushButton
from math import pi
from numpy.linalg import matrix_power

class BranchElement(CanvasElement):

    def __init__(self, point, circuit, handle_distance = 1):

        super().__init__(point.snaptogrid())

        self.properties = {}
        handle_disp = Point(handle_distance, 0)
        self.nodes = []
        self.nodes.append(Node(Point(-SPACING,0)-SPACING*handle_disp+point.snaptogrid(), circuit))
        self.nodes.append(Node(Point(SPACING,0)+SPACING*handle_disp+point.snaptogrid(), circuit))

        self.connections = []
        self.connections.append(Connection(self, self.nodes[0], -1*handle_disp, circuit))
        self.connections.append(Connection(self, self.nodes[1], handle_disp, circuit))

        for node, connection in zip(self.nodes, self.connections):
            node.connections.append(connection)

        for node in self.nodes:
            node.elements.append(self)

        self.disps = []
        self.circuit = circuit
        self.circuit.add_element(self)


    def __str__(self):
        props_rep = []
        for prop in self.properties:
            props_rep.append(f"{self.properties[prop]},")
        props_string = "".join(props_rep)
        props_string = props_string[:-1]
        return f"- [{self.name},{self.nodes[0].idx},{self.nodes[1].idx},{props_string}]"

    def paint(self, painter):
        painter.setPen(QPen(QColorConstants.Black, 3))
        for i, prop in enumerate(self.properties):
            painter.drawText(int(SPACING/2+self.x), int(self.y-SPACING/2-i*FONTSIZE*1.5), str(prop) + " = "+str(self.properties[prop]))
        
        width = self.bbox.width
        height = self.bbox.height
        if self.rot % 2== 0:
            disp = [SPACING, 0]
        else:
            disp = [0,SPACING]
        painter.drawPixmap(int(self.x-width/2-disp[0]/2), int(self.y-height/2-disp[1]/2), int(width+disp[0]), int(height+disp[1]), self.icon)

    def in_bbox(self,point):
        self.disps.clear()
        for node in self.nodes:
            self.disps.append(Point(node.x-self.x, node.y-self.y))
        return super().in_bbox(point)

    def drag(self, point):
        for obj in self.circuit:
            if obj.in_bbox(point.snaptogrid()) and not obj is self:
                return
        super().drag(point)
        for node,disp in zip(self.nodes,self.disps):
            if len(node.elements) == 1 and all([len(conn.anchors)==0 for conn in node.connections]):
                node.drag(Point(self.x, self.y) + disp)
    
    def setIcon(self, path, width, height):
        self.icon_path = path
        self.icon = QIcon(path).pixmap(width*IMG_RES_FACTOR, height*IMG_RES_FACTOR)
        self.bbox = Bbox(width, height)

    def rotate(self):
        self.rotate_icon()

        for connection in self.connections:
            connection.reorient()
               
        for node in self.nodes:
            if len(node.elements) == 1 and all([len(conn.anchors)==0 for conn in node.connections]):
                node.x -= self.x
                node.y -= self.y
                (node.x,node.y) = np.array([node.x, node.y]) @ np.array([[0,-1],[1,0]])
                node.x += self.x
                node.y += self.y
                node.rotate()
    
    def rotate_icon(self):
        super().rotate() 
        rotatemat = QTransform() 
        rotatemat.rotate(-90)
        self.icon = self.icon.transformed(rotatemat)
        w,h = self.bbox.width, self.bbox.height
        self.bbox = Bbox(h,w) 
        
    def toolbar(self, update):
        toolbar = QToolBar()
        def rotateandupdate():
            self.rotate()
            update()
        rotate = QAction("",toolbar)
        rotate.setIcon(QIcon("./icons/rotate"))
        rotate.triggered.connect(rotateandupdate)
        toolbar.addAction(rotate)
        for prop in self.properties:
            propedit = PropEdit(prop, self.properties, update) 
            toolbar.addWidget(propedit)
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Ignored)
        toolbar.addWidget(spacer)
        return toolbar
    
    def delete(self):
        self.circuit.remove_element(self)


    class ElementMomento:
        def __init__(self, element):
            self.nodes = []
            self.grounds = []
            self.name = element.name
            for node in element.nodes:
                if type(node) is Ground:
                    self.grounds.append(node.idx)
                else:
                    self.nodes.append(node.idx)
            self.loc = Point(element.x, element.y)
            self.icon = element.icon_path
            self.properties = element.properties.copy()
            self.conn_memos = []
            for connection in element.connections:
                self.conn_memos.append(Connection.ConnectionMomento(connection))
            self.rot = element.rot
        
class Capacitor(BranchElement):


    def __init__(self, point, circuit):
        super().__init__(point, circuit)
        self.name = "C"
        self.C = .02
        self.properties["C"] = self.C
        self.icon_path = "./capacitor.svg"
        self.setIcon(self.icon_path, SPACING, SPACING)


class JosephsonJunction(BranchElement):


    def __init__(self, point, circuit):
        super().__init__(point, circuit)
        self.name = "JJ"
        self.EJ = 21
        self.EC = 1.2
        self.properties["EC"] = self.EC
        self.properties["EJ"] = self.EJ
        self.icon_path = "./JJ.svg"
        self.setIcon(self.icon_path, SPACING, SPACING)

class Inductor(BranchElement):

    def __init__(self, point, circuit):
        super().__init__(point, circuit)
        self.name = "L"
        self.L = 1.2
        self.properties["L"] = self.L
        self.icon_path = "./Inductor.svg"
        self.setIcon(self.icon_path, SPACING, SPACING)

class PropEdit(QWidget):
    def __init__(self, key, properties, update):
        super().__init__()
        self.key = key
        self.properties = properties
        self.update = update
        self.initGui()
    
    def initGui(self):
        layout = QHBoxLayout()
        self.setLayout(layout)
        layout.addWidget(QLabel(self.key))
        propedit =QLineEdit(str(self.properties[self.key]))
        propedit.setMaximumWidth(70)
        propedit.editingFinished.connect(self.update)
        def textchange(text):
            self.properties[self.key] = text
        propedit.textChanged.connect(textchange)
        layout.addWidget(propedit)
        layout.addSpacerItem(QSpacerItem(
            0,
            0,
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Ignored
        ))
    

