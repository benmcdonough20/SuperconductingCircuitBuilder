from constants import *
from canvas_element import CanvasElement
from PyQt6.QtGui import QPen, QColorConstants

class Connection(CanvasElement):

    def __init__(self, origin, dest, d, canvas):
        super().__init__(origin.x, origin.y, canvas)
        self.anchors = []
        self.wires = []
        newwire = Wire(origin, dest, d)

        orientation = 0
        oy = round(origin.y/SPACING)
        oy += d[1]

        ox = round(origin.x/SPACING)
        ox += d[0]

        tx,ty = round(dest.x/SPACING), round(dest.y/SPACING)
        if d[0]:
            if (ox < tx and d[0] < 0) or (ox > tx and d[0] > 0):
                orientation = 1 

        elif d[1]:
            if not ((oy < ty and d[1] < 0) or (oy > ty and d[1] > 0)):
                orientation = 1

        newwire.orientation = orientation
        self.wires.append(newwire)

        self.origin = origin
        self.dest = dest
        self.d = d
        self.links = []
        self.canvas = canvas
        self.selected_anchor = None
        self.selected_wire = None
            
    def paint(self, painter):
        for wire in self.wires:
            wire.paint(painter)

        for anchor in self.anchors:
            anchor.paint(painter)

    def in_bbox(self, x, y):
        for anchor in self.anchors:
            if anchor.in_bbox(x,y):
                self.selected_anchor = anchor
                return True
        self.selected_anchor = None
        for wire in self.wires:
            if wire.in_bbox(x,y):
                self.selected_wire = wire
                return True
        self.selected_wire = None
        return False    
    
    def press(self, x, y):
        if not self.selected_anchor:
            newanchor = Anchor(round(x/SPACING)*SPACING, round(y/SPACING)*SPACING, self)
            self.anchors.append(newanchor)
            self.selected_anchor = newanchor
            newwire = Wire(newanchor, self.selected_wire.dest, [0,0])
            newwire.orientation = self.selected_wire.orientation
            self.selected_wire.dest = newanchor
            self.wires.append(newwire)

    def rewire(self):
        for wire in self.wires:
            wire.rewire()
    
    def drag(self, x, y):
        if self.selected_anchor:
            self.selected_anchor.drag(x,y)

    def change_dest(self, newdest):
        self.dest = newdest
        self.wires[-1].dest = newdest
        

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
        oy += self.d[1]

        ox = round(self.origin.x/SPACING)
        ox += self.d[0]
       

        tx,ty = round(self.dest.x/SPACING), round(self.dest.y/SPACING)
        self.wire(ox, oy, tx, ty)


    def wire(self, ox, oy, tx, ty):
        
        def linkx(sy): 
            if tx > ox:
                for x in range(ox, tx):
                    if (x*SPACING, sy*SPACING) == (self.origin.x, self.origin.y) and not self.d == [0,0]:
                        for i in range(3):
                            self.links.append(Link(x+i-1,sy-1))
                    else:
                        self.links.append(Link(x,sy))

            else:
                for x in range(ox, tx, -1):
                    if (x*SPACING, sy*SPACING) == (self.origin.x, self.origin.y) and not self.d == [0,0]:
                        for i in range(3):
                            self.links.append(Link(x-i+1, sy+1))
                    else:
                        self.links.append(Link(x, sy))
                        

        def linky(sx): 
            if ty > oy:
                for y in range(oy, ty):
                    if (sx*SPACING, y*SPACING) == (self.origin.x, self.origin.y) and not self.d == [0,0]:
                        for i in range(3):
                            self.links.append(Link(sx-1,y+i-1))

                    self.links.append(Link(sx,y))
            else:
                for y in range(oy, ty, -1):
                    if (sx*SPACING, y*SPACING) == (self.origin.x, self.origin.y) and not self.d == [0,0]:
                        for i in range(3):
                            self.links.append(Link(sx-1,y+i-1))
                    self.links.append(Link(sx, y))

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

    def in_bbox(self, x, y):
        for link in self.links[1:]:
            if link.in_bbox(x,y):
                self.selected_link = link
                return True
        return False

class Link:
    
    def __init__(self, x, y): 
        self.x = x
        self.bbox = Bbox(SPACING, SPACING)
        self.y = y
    
    def in_bbox(self, x, y):
        sx = self.x*SPACING
        sy = self.y*SPACING
        if (x > sx-self.bbox.width/2 and x < sx + self.bbox.width/2 and y > sy-self.bbox.height/2 and y < sy+self.bbox.height/2):
            return self
        return None

    def paint(self, painter):
        painter.drawPoint(self.x*SPACING, self.y*SPACING)


class Anchor(CanvasElement):

    layer = 1

    def __init__(self,x,y,connection):
        self.connection = connection
        self.bbox = Bbox(SPACING, SPACING)
        self.x = x
        self.y = y

    def paint(self, painter):
        painter.setPen(QPen(QColorConstants.Black, 1))
        painter.drawEllipse(self.x-5, self.y-5, 10,10)

    def in_bbox(self, x, y):
        if super().in_bbox(x,y):
            return self
        return None
