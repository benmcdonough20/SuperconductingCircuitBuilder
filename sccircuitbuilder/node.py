from sccircuitbuilder.canvas_element import CanvasElement
from sccircuitbuilder.constants import *
from math import sin, cos, pi
from PySide6.QtGui import QPen, QColorConstants, QPolygon, QIcon, QAction
from PySide6.QtCore import QPoint
from PySide6.QtWidgets import QToolBar, QWidget, QSizePolicy, QPushButton
from numpy.linalg import matrix_power

GROUND_RAD = .3*SPACING

class Node(CanvasElement):
    def __init__(self, point, circuit):
        super().__init__(point.snaptogrid())
        
        self.idx = 0
        self.elements = []
        self.connections = []
        self.circuit = circuit
        self.add_to_circuit()
    
    def add_to_circuit(self):
        self.circuit.add_node(self)

    def drop(self, point, other):
        if not issubclass(type(other), Node):
            return
        self.circuit.remove_node(self)
        other.connections += self.connections
        other.elements += self.elements
        for conn in self.connections:
            conn.change_dest(other)
        for elem in self.elements:
            for i,node in enumerate(elem.nodes):
                if node == self:
                    elem.nodes[i] = other
   
    def drag(self, point):
        super().drag(point)
        for conn in self.connections:
            conn.rewire()

    def paint(self, painter):
        pen = QPen(QColorConstants.Black, NODE_SIZE)
        painter.setPen(pen)
        painter.drawText(int(self.x+FONTSIZE), int(self.y-FONTSIZE), str(self.idx))
        painter.drawPoint(self.x, self.y)
    
    def toolbar(self, update):
        toolbar = QToolBar()
        split = QPushButton("Split Node")
        def splitandupdate():
            self.split()
            update()
        split.clicked.connect(splitandupdate)
        toolbar.addWidget(split)
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Ignored)
        toolbar.addWidget(spacer)
        return toolbar
    
    def split(self):
        if len(self.elements) > 1:
            self.circuit.remove_node(self)
            for element in self.elements:
                displacement = Point(0,0)
                conn = None
                for connection in element.connections:
                    if connection.dest is self:
                        displacement = connection.displacement
                        conn = connection
                conn.anchors.clear()
                newnode = Node(Point(element.x, element.y)+displacement*SPACING*matrix_power(ROT_MAT, element.rot), self.circuit)
                newnode.elements.append(element)
                newnode.connections.append(conn)
                conn.change_dest(newnode)
                for i,node in enumerate(element.nodes):
                    if node is self: 
                        element.nodes[i] = newnode
    
    def delete(self):
        self.circuit.remove_node(self)

    class NodeMemento:

        def __init__(self, node):
            self.idx = node.idx
            self.loc = Point(node.x, node.y)
            self.rot = node.rot
        
         
class Ground(Node):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def toolbar(self, update):
        toolbar = QToolBar()
        def rotateandupdate():
            self.rotate()
            update()
        rotate = QAction("",toolbar)
        rotate.setIcon(QIcon(os.path.join(os.path.dirname(__file__), "icons/rotate")))
        rotate.triggered.connect(rotateandupdate)
        toolbar.addAction(rotate)

        if not self.elements:
            toolbar = QToolBar()
            delete = QAction("",toolbar)
            delete.setIcon(QIcon(os.path.join(os.path.dirname(__file__),"icons/trash")))
            def deleteandupdate():
                self.delete()
                update()
            delete.triggered.connect(deleteandupdate)
            toolbar.addAction(delete)

        return toolbar

    def add_to_circuit(self):
        self.circuit.add_ground(self)

    def paint(self, painter):
        painter.setPen(QPen(QColorConstants.Black, WIRE_SIZE))
        p1 = QPoint(int(self.x+GROUND_RAD*cos(self.rot*pi/2)), int(self.y+GROUND_RAD*sin(self.rot*pi/2)))
        p2 = QPoint(int(self.x+GROUND_RAD*sin(self.rot*pi/2)), int(self.y+GROUND_RAD*cos(self.rot*pi/2)))
        p3 = QPoint(int(self.x-GROUND_RAD*cos(self.rot*pi/2)), int(self.y-GROUND_RAD*sin(self.rot*pi/2)))

        painter.drawPolygon(QPolygon([p1,p2,p3]))

    def delete(self):
        self.circuit.remove_ground(self)

