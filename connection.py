from constants import *
from canvas_element import CanvasElement

class Connection(CanvasElement):

    layer = BOTTOM
    
    def __init__(self, origin, dest, d, canvas):
        self.anchors = []
        self.origin = origin
        self.dest = dest
        self.d = d
        self.links = []
        self.canvas = canvas
        self.selected_link = None
        canvas.add_object(self)
        self.rewire()
    
    def rotate(self):
        return

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

            
    def draw(self):
        self.rewire()
        if len(self.links) == 0:
            return
        for i in range(len(self.links)-1):
            link1 = self.links[i] 
            link2 = self.links[i+1] 

            self.canvas.rel_line(link1.x*SPACING, link1.y*SPACING, link2.x*SPACING, link2.y*SPACING, width = 3)
        self.canvas.rel_line(self.links[-1].x*SPACING, self.links[-1].y*SPACING, self.dest.x, self.dest.y, width = 3)

    def in_bbox(self, x, y):
        for link in self.links[1:]:
            ln = link.in_bbox(x,y)
            if ln:
                self.selected_link = ln
                break
        else:
            return False

        self.anchors.append(Anchor(self.selected_link.x*SPACING, self.selected_link.y*SPACING, self))

        return True

class Link:
    
    def __init__(self, x, y): 
        self.x = x
        self.bbox = Bbox(SPACING/2.5, SPACING/2.5)
        self.y = y
    
    def in_bbox(self, x, y):
        sx = self.x*SPACING
        sy = self.y*SPACING
        if (x > sx-self.bbox.width and x < sx + self.bbox.width and y > sy-self.bbox.height and y < sy+self.bbox.height):
            return self
        return None

class Anchor(CanvasElement):

    layer = 1

    def __init__(self,x,y,connection):
        super().__init__(x,y,connection.canvas)
        self.connection = connection
        self.canvas.active_object = self

    def draw(self):
        self.canvas.rel_point(self.x, self.y, width = 2)

    def merge(self, other):
        self.canvas.toplayer.remove(other)
        idx = other.connection.anchors.index(other)
        other.connection.anchors[idx] = self
    
    def delete(self):
        self.canvas.toplayer.remove(self)
        self.connection.anchors.remove(self)
