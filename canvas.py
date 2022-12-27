from PyQt6.QtWidgets import QFrame 
from PyQt6.QtGui import QColorConstants, QTransform, QPen, QPainter
from PyQt6.QtCore import Qt

from constants import *
from node import Node, Ground
from connection import Anchor
from branch_element import Capacitor, Inductor, JosephsonJunction

def event_loc(event):
    return event.position().x(), event.position().y()

class SmartCanvas(QFrame):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.painter = QPainter()

        #world transform and put origin at center of screen
        self._transform = QTransform()
        self._transform.translate(self.width()/2, self.height()/2)

        self.objects = [] #list of objects that can be clicked
        self.selected_object = None #object that is currently selected

        self._dragging = False

        self._zoom_factor = 1 #limit zoom due to buggy rounding behavior

        c = Capacitor(0,0,self)

    def add_object(self, object):
        self.objects.append(object)
    
    def remove_object(self, object):
        self.objects.remove(object)
        
    def wheelEvent(self, event): #wheel scroll
        direction = 0
        if event.angleDelta().y() > 0:
            if MAX_ZOOM > self._zoom_factor:
                direction = 1
        else:
            if MIN_ZOOM < self._zoom_factor:
                direction = -1

        #zoom on mouse pointer
        centeron = self.unmap(*event_loc(event))
        self._zoom(*centeron, direction)

        self.update()
    
    def _zoom(self, centerx, centery, direction):
        self._zoom_factor *= (1+direction*ZOOM_SPEED) #keep track of zoom amount

        #zoom centered on mouse pointer
        self._transform.translate(
            -centerx*direction*ZOOM_SPEED, 
            -centery*direction*ZOOM_SPEED
            )
        self._transform.scale(1+direction*ZOOM_SPEED, 1+direction*ZOOM_SPEED)
        

    def paintEvent(self, event):
        self.painter.begin(self)
        self.painter.setTransform(self._transform)
        self.painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        self._background()

        for object in self.objects:
            object.paint(self.painter)

        pen = QPen(QColorConstants.Red, 1)
        self.painter.setPen(pen)
        self.painter.end()

    def _background(self): #solid background with grid
        painter = self.painter

        width = self.width()
        height = self.height()

        xstart, ystart = self.unmap(0, 0)
        xstop, ystop = self.unmap(width, height)

        painter.fillRect(xstart,ystart, xstop-xstart, ystop-ystart, QColorConstants.White)

        painter.setPen(QPen(QColorConstants.LightGray, 1))
        for i in range(round(xstart/SPACING),round(xstop/SPACING)+1):
            painter.drawLine(int((i+.5)*SPACING), int(ystart), int((i+.5)*SPACING), int(ystop))

        for j in range(round(ystart/SPACING), round(ystop/SPACING)+1):
            painter.drawLine(int(xstart), int((j+.5)*SPACING), int(xstop), int((j+.5)*SPACING))


    def map(self, x, y): #map device coordinates to world coordinates
        return self._transform.map(x,y)
    
    def unmap(self, x, y): #map world coodinates to device coordinates
        inverse_transform,_ = self._transform.inverted()
        return inverse_transform.map(x,y)
    
    def mouseMoveEvent(self, event) -> None:
        mx,my = self.unmap(*event_loc(event))

        if event.buttons() == Qt.MouseButton.LeftButton: #left button drag
            self._dragging = True
            self._drag(mx, my)

        elif event.buttons() == Qt.MouseButton.MiddleButton: #middle button drag
            self._pan(event)

        self.update()
    
    def _drag(self, x, y):
        if self.selected_object:
            self.selected_object.drag(x,y)

    def _pan(self, event):
        #get mouse displacement in world coordinates
        mx, my = self.unmap(event.position().x()-self._d.x(), event.position().y()-self._d.y())
        #get origin displacement (no scaling)
        ox, oy = self.unmap(0,0)
        #subtract displacement between frames and translate
        self._transform.translate(mx-ox, my-oy)
        #update position to compute next displacement
        self._d = event.position()
        
    
    def mousePressEvent(self, event) -> None:
        if event.buttons() == Qt.MouseButton.MiddleButton: #initiate pan
            self._d = event.position()

        elif event.buttons() == Qt.MouseButton.LeftButton: #select object under mouse
            for object in self.objects:
                mx,my = self.unmap(event.position().x(), event.position().y())
                if object.in_bbox(mx,my):
                    self.selected_object = object
                    object.press(mx,my)
                    break
            else:
                self.selected_object = None
       
    def mouseReleaseEvent(self,event):
        mx,my = self.unmap(*event_loc(event))
        if self._dragging:
            self.drop(mx, my)
        else:
            self.click(event)
        self._dragging = False
        self.update()

    def drop(self, mx,my):
        for object in self.objects:
            if object is self.selected_object:
                continue
            if object.in_bbox(mx, my) and self.selected_object:
                self.selected_object.drop(mx, my, object)
                break
        self.selected_object = None

    def collision(self, object):
        for other in self.objects:
            if other == object:
                continue
            if abs(other.x - object.x < other.bbox.width/2 + object.bbox.width/2) or \
                abs(other.y - object.y < other.bbox.height/2 + object.bbox.height/2):
                return True
        return False
    
    def click(self, event):
        ...