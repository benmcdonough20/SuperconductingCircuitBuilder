from sccircuitbuilder.constants import *
from sccircuitbuilder.canvas_element import CanvasElement
from PySide6.QtGui import QPen, QColorConstants, QAction, QIcon
import numpy as np
from PySide6.QtWidgets import QToolBar, QWidget, QSizePolicy, QPushButton
import os

class Connection(CanvasElement):

    def __init__(self, origin, dest, displacement, circuit):
        super().__init__(origin)
        self.anchors = []
        self.wires = []
        self.bbox = None
        self.origin = origin
        self.dest = dest
        self.displacement = displacement
        self.links = []
        self.circuit = circuit
        self.selected_anchor = None
        self.selected_wire = None
        self.circuit.add_connection(self)
        self.disps = []

        self.wires.append(Wire(origin, dest, displacement))
            
    def paint(self, painter):
        for anchor in self.anchors:
            anchor.paint(painter)
        for wire in self.wires:
            wire.paint(painter)

    def in_bbox(self, point):
        for anchor in self.anchors:
            if anchor.in_bbox(point):
                self.selected_anchor = anchor
                return True
        self.selected_anchor = None
        for wire in self.wires:
            if wire.in_bbox(point):
                self.selected_wire = wire
                return True
        self.selected_wire = None
        return False    
    
    def press(self, point):
        if not self.selected_anchor:
            newanchor = Anchor(point.snaptogrid(), self.circuit, self)
            self.anchors.append(newanchor)
            self.selected_anchor = newanchor

            self.wires.append(Wire(newanchor, self.selected_wire.dest, Point(0,0)))
            self.selected_wire.dest = newanchor
            self.rewire()

    def rewire(self):
        for wire in self.wires:
            wire.rewire()

    def change_dest(self, newdest):
        self.dest = newdest
        self.wires[-1].dest = newdest

    def reorient(self):
        wire = self.wires[0]
        wire.d = wire.d * ROT_MAT
        wire.rewire()

    def remove_anchor(self, anchor):
        head = None
        tail = None
        for wire in self.wires:
            if wire.dest is anchor:
                head = wire
            if wire.origin is anchor:
                tail = wire
        self.anchors.remove(anchor)
        self.circuit.remove_anchor(anchor)
        self.wires.remove(tail)
        head.dest = tail.dest

    def toolbar(self, update):
        if self.selected_anchor:
            return self.selected_anchor.toolbar(update)
        else:
            return QToolBar()
    
    class ConnectionMomento:
        def __init__(self, connection):
            self.dest = connection.dest.idx
            self.anchors = []
            wire = connection.wires[0]
            while True: #add anchors in path order
                if wire.dest in connection.anchors:
                    self.anchors.append(Point(wire.dest.x, wire.dest.y))
                for newwire in connection.wires:
                    if newwire.origin is wire.dest:
                        wire = newwire
                        break
                else:
                    break
                    
            self.d = connection.wires[0].d


class Wire(CanvasElement):

    def __init__(self, origin, dest, d):
        self.origin = origin
        self.dest = dest
        self.d = d
        self.links = []
        self.selected_link = None
        self.orientation = 0
        self.rewire()
    
    def rewire(self):
        self.links.clear()
 
        oy = round(self.origin.y/SPACING)
        oy += self.d.y

        ox = round(self.origin.x/SPACING)
        ox += self.d.x
       

        tx,ty = round(self.dest.x/SPACING), round(self.dest.y/SPACING)

        self.orientation = 0
        if self.d.x:
            if (ox < tx and self.d.x < 0) or (ox > tx and self.d.x > 0):
                self.orientation = 1

        elif self.d.y:
            if not ((oy < ty and self.d.y < 0) or (oy > ty and self.d.y > 0)):
                self.orientation = 1

        self.wire(ox, oy, tx, ty)


    def wire(self, ox, oy, tx, ty):
        
        def linkx(sy): 
            disp = int(tx > ox)*2-1
            for x in range(ox, tx, disp):
                self.links.append(Link(x,sy))

        def linky(sx): 
            disp = int(ty > oy)*2-1
            for y in range(oy, ty, disp):
                self.links.append(Link(sx,y))

        if self.orientation == 0:
            linkx(oy)
            linky(tx)
        else:
            linky(ox)
            linkx(ty)

            
    def paint(self, painter):
        self.rewire()
        pen = QPen(QColorConstants.Black, 2)
        painter.setPen(pen)

        if len(self.links) == 0:
            return
        link2 = None
        for i in range(len(self.links)-1):
            link1 = self.links[i] 
            link2 = self.links[i+1] 

            painter.drawLine(link1.x*SPACING, link1.y*SPACING, link2.x*SPACING, link2.y*SPACING)
            
        painter.drawLine(self.links[-1].x*SPACING, self.links[-1].y*SPACING, self.dest.x, self.dest.y)

    def in_bbox(self, point):
        for link in self.links[1:]:
            if link.in_bbox(point):
                self.selected_link = link
                return True
        return False

class Link:
    
    def __init__(self, x, y): 
        self.x = x
        self.bbox = Bbox(SPACING, SPACING)
        self.y = y
    
    def in_bbox(self, point):
        sx = self.x*SPACING
        sy = self.y*SPACING
        if (point.x > sx-self.bbox.width/2 and point.x < sx + self.bbox.width/2 \
            and point.y > sy-self.bbox.height/2 and point.y < sy+self.bbox.height/2):
            return self
        return None


class Anchor(CanvasElement):

    layer = 1

    def __init__(self, point, circuit, connection):
        super().__init__(point)
        circuit.add_anchor(self)
        self.connection = connection

    def paint(self, painter):
        painter.setPen(QPen(QColorConstants.Black, 1))
        painter.drawEllipse(self.x-5, self.y-5, 10,10)

    def in_bbox(self, point):
        if super().in_bbox(point):
            return self
        return None
    
    def delete(self):
        self.connection.remove_anchor(self)

    def toolbar(self, update):
        toolbar = QToolBar()
        delete = QAction("",toolbar)
        delete.setIcon(QIcon(os.path.join(os.path.dirname(__file__),"icons/trash")))
        def deleteandupdate():
            self.delete()
            update()
        delete.triggered.connect(deleteandupdate)
        toolbar.addAction(delete)
        return toolbar
