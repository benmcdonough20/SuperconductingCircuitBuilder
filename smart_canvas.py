from tkinter import Canvas
from constants import *
from node import Node, Ground
from connection import Anchor
from branch_element import BranchElement


class SmartCanvas(Canvas):
    
    def __init__(self, gui, *args, **kwargs):

        super().__init__(gui.window, *args, **kwargs)

        self.gui = gui

        self.bind("<Configure>", lambda event : self.redraw())
        self.bind("<Button-4>", lambda event : self.zoom(event, 1))
        self.bind("<Button-5>", lambda event : self.zoom(event,-1))
        self.bind("<B2-Motion>", lambda event : self.pan(event))
        self.bind("<Button-2>", lambda event : self.middle_press(event))
        self.bind("<Button-1>", lambda event : self.left_press(event))
        self.bind("<B1-Motion>", lambda event : self.left_drag(event))
        self.bind("<ButtonRelease-1>", lambda event : self.left_release(event))

        self.dx = 0
        self.dy = 0

        self.offsetx = kwargs["width"]/2
        self.offsety = kwargs["height"]/2
        self.zoom_factor = 1

        self.active_object = None
        self.toplayer = []
        self.bottomlayer = []

        self.state = State()

    def left_press(self, event):
        x,y = self.abs_coords(event.x, event.y)
        self.active_object = self.object_under_mouse(x,y)

    def middle_press(self, event):
        self.state.dragging()
        x,y = self.abs_coords(event.x, event.y)
        self.dx = x
        self.dy = y

    def left_drag(self, event):
        x, y = self.abs_coords(event.x, event.y)
        if self.active_object:
            self.active_object.drag(x, y)
            self.redraw()
        self.state.dragging()

    def left_release(self, event):
        x, y = self.abs_coords(event.x, event.y)
        if self.state == "dragging":
            self.drop(x,y)
        elif self.state == "None":
            self.left_click(x,y)

        self.state.reset() 

    def object_under_mouse(self, x, y, exclude = None):
        object = None
        
        for obj in self.toplayer:
            if obj.in_bbox(x, y) and obj is not exclude:
                return obj

        for obj in self.bottomlayer:
            if obj.in_bbox(x,y) and obj is not exclude:
                return obj

        return object

    def add_object(self, object):
        if object.layer == TOP:
            self.toplayer.append(object)
        elif object.layer == BOTTOM:
            self.bottomlayer.append(object)
        self.redraw()
        
    def left_click(self, x, y):
        self.active_object = self.object_under_mouse(x, y)
        if self.active_object:
            self.active_object.rotate()

        self.state.reset()
        self.redraw()

    def drop(self, x,y):
        other = self.object_under_mouse(x, y, self.active_object)

        if (type(self.active_object) is Node and (type(other) is Node or type(other) is Ground)):
            self.node_merge(self.active_object, other) 

        if type(self.active_object) is Anchor and type(other) is Anchor:
            if self.active_object.connection.dest is other.connection.dest:
                self.active_object.merge(other)

        self.state.reset()
        
    def redraw(self):

        self.delete("all")

        width = self.winfo_width()
        height = self.winfo_height()
       
        xstart, ystart = self.abs_coords(0, 0)
        xstop, ystop = self.abs_coords(width, height)

        for i in range(0,round(xstop/SPACING)+1):
            self.rel_line((i+.5)*SPACING, ystart, (i+.5)*SPACING, ystop, fill = LINECOLOR, width = LINEWIDTH, tags="bg")

        for i in range(0,round(xstart/SPACING)-1, -1):
            self.rel_line((i-.5)*SPACING, ystart, (i-.5)*SPACING, ystop, fill = LINECOLOR, width = LINEWIDTH, tags="bg")

        for j in range(0, round(ystop/SPACING)+1):
            self.rel_line(xstart, (j+.5)*SPACING, xstop, (j+.5)*SPACING, fill = LINECOLOR, width = LINEWIDTH, tags="bg")

        for j in range(0, round(ystart/SPACING)-1, -1):
            self.rel_line(xstart, (j-.5)*SPACING, xstop, (j-.5)*SPACING, fill = LINECOLOR, width = LINEWIDTH, tags="bg")

        for object in self.bottomlayer:
            object.draw() 
        for object in self.toplayer:
            object.draw()
        
    def zoom(self,event,direction):
        if self.zoom_factor < MIN_ZOOM and direction < 0:
            return
        if self.zoom_factor > MAX_ZOOM and direction > 0:
            return
        x,y = self.abs_coords(event.x, event.y)
        self.shift(-x*direction*self.zoom_factor*ZOOM_SPEED, -y*self.zoom_factor*direction*ZOOM_SPEED)
        self.scale(1+direction*ZOOM_SPEED) 


    def pan(self, event):
        x,y = self.abs_coords(event.x, event.y)
        self.shift(x-self.dx, y-self.dy)        
        
    def scale(self, factor):
        self.zoom_factor*=factor
        self.redraw()

    def shift(self, offsetx, offsety):
        self.offsetx += offsetx
        self.offsety += offsety
        self.redraw()
       
    def rel_line(self, x1, y1, x2, y2, **kwargs):
        x1r, y1r = self.rel_coords(x1,y1)
        x2r, y2r = self.rel_coords(x2,y2)
        self.create_line(x1r, y1r, x2r, y2r, **kwargs)

    def rel_curve(self, p1, p2, p3, **kwargs):
        p1r = self.rel_coords(*p1)
        p2r = self.rel_coords(*p2)
        p3r = self.rel_coords(*p3)

        self.create_line(*p1r, *p2r, *p3r, **kwargs, smooth=1)

    def rel_point(self, x, y, **kwargs):
        x1, y1 = (x-POINT_SIZE), (y-POINT_SIZE)
        x2, y2 = (x+POINT_SIZE), (y+POINT_SIZE)
        x1r, y1r = self.rel_coords(x1,y1)
        x2r, y2r = self.rel_coords(x2,y2)
        self.create_oval(x1r, y1r, x2r, y2r, **kwargs)
    
    def rel_poly(self, *pts, **kwargs):
        rel_pts = [self.rel_coords(*pt) for pt in pts]
        self.create_polygon(rel_pts, **kwargs)
   
    def rel_box(self, x1, y1, x2, y2, **kwargs):
        x1r, y1r = self.rel_coords(x1,y1)
        x2r, y2r = self.rel_coords(x2,y2)
        self.create_rectangle(x1r, y1r, x2r, y2r, **kwargs)

    def rel_circle(self, x, y, r, **kwargs):
        x1, y1 = (x-r), (y-r)
        x2, y2 = (x+r), (y+r)
        x1r, y1r = self.rel_coords(x1,y1)
        x2r, y2r = self.rel_coords(x2,y2)
        self.create_oval(x1r, y1r, x2r, y2r, **kwargs)

    def rel_coords(self, x, y):
        return ((self.offsetx+x*self.zoom_factor)*SPACING, (self.offsety+y*self.zoom_factor)*SPACING)

    def abs_coords(self, x, y):
        return((x-self.offsetx)/self.zoom_factor, (y-self.offsety)/self.zoom_factor)

    def node_merge(self, node, other):

        self.toplayer.remove(node)
        self.gui.remove_node(node)

        other.merge(node)
        self.active_object = other
        self.redraw()

class State:
    def __init__(self):
        self.reset()
    def dragging(self):
        self.state = "dragging"
    def reset(self):
        self.state = "None"
    def edit(self):
        self.state = "editing"
    def delete(self):
        self.state = "deleting"
    def __eq__(self, other):
        return self.state == other