from constants import *
from canvas_element import CanvasElement
from PyQt6.QtGui import QPen, QColorConstants

class Connection(CanvasElement):

    def __init__(self, origin, dest, d, canvas):
        super().__init__(origin.x, origin.y, canvas)
        self.anchors = []
        self.wires = []
        self.origin = origin
        self.dest = dest
        self.d = d
        self.links = []
        self.canvas = canvas
        self.selected_link = None
        canvas.add_object(self)
        self.rewire()
        self.selected_anchor = None
    
    def rewire(self):
        self.links.clear()
 
        oy = round(self.origin.y/SPACING)
        oy += self.d[1]

        ox = round(self.origin.x/SPACING)
        ox += self.d[0]
       

        tx,ty = round(self.dest.x/SPACING), round(self.dest.y/SPACING)

        if self.anchors:
            a1x, a1y = ox, oy
            for i,a in enumerate(self.anchors):
                ax, ay = round(self.anchors[i].x/SPACING), round(self.anchors[i].y/SPACING)
                self.wire(a1x, a1y, ax, ay)
                a1x, a1y = ax, ay  
            
            self.wire(a1x, a1y, tx, ty)
        else:
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

        if self.d[0]:
            if (ox < tx and self.d[0] < 0) or (ox > tx and self.d[0] > 0):
                linky(ox)
                linkx(ty)
            else:
                linkx(oy)
                linky(tx)

        elif self.d[1]:
            if (oy < ty and self.d[1] < 0) or (oy > ty and self.d[1] > 0):
                linkx(oy)
                linky(tx)
            else:
                linky(ox)
                linkx(ty)
        else:
            linkx(oy)
            linky(tx)

        if self.links:
            self.links[-1].clickable = False

            
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

        for anchor in self.anchors:
            anchor.paint(painter)

    def in_bbox(self, x, y):
        for anchor in self.anchors:
            if anchor.in_bbox(x,y):
                return anchor
        for link in self.links[1:]:
            if link.in_bbox(x,y):
                self.selected_link = link
                return True
        return False
    
    def press(self, x, y):
        for anchor in self.anchors:
            if anchor.in_bbox(x,y):
                self.selected_anchor = anchor
                break
        else:
            newanchor = Anchor(self.selected_link.x*SPACING, self.selected_link.y*SPACING, self)
            self.anchors.append(newanchor)
            self.selected_anchor = newanchor
            
    
    def drag(self, x, y):
        if self.selected_anchor:
            self.selected_anchor.drag(x,y)
        

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
