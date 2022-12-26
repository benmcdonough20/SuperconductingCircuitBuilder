from PyQt6.QtWidgets import QGraphicsView, QGraphicsScene, QFrame 
from PyQt6.QtGui import QPainter
from PyQt6.QtGui import QPixmap, QColorConstants, QTransform, QPen
from constants import *
from node import Node, Ground
from connection import Anchor
from PyQt6.QtCore import QEvent, Qt
from math import sqrt


class SmartCanvas(QFrame):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.painter = QPainter()
        self._transform = QTransform()
        self._transform.translate(self.width()/2, self.height()/2)

        self.objects = []
        self.active_object = None

    def wheelEvent(self, event):
        scale = self.getScale()
        if event.angleDelta().y() > 0:
            if MIN_ZOOM < scale:
                self._transform.scale(1+ZOOM_SPEED, 1+ZOOM_SPEED)
        else:
            if MAX_ZOOM > scale:
                self._transform.scale(1-ZOOM_SPEED, 1-ZOOM_SPEED)
        self.update()

    def paintEvent(self, event):
        self.painter.begin(self)
        self.painter.setTransform(self._transform)
        self.painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        self.background()
        for object in self.objects:
            object.draw()
        self.painter.end()

    def background(self):
        painter = self.painter
        painter.setBackground(QColorConstants.White)

        width = self.width()
        height = self.height()

        xstart, ystart = self.unmap(0, 0)
        xstop, ystop = self.unmap(width, height)

        painter.setPen(QPen(QColorConstants.LightGray, 1))

        for i in range(0,round(xstop/SPACING)+1):
            painter.drawLine(int((i+.5)*SPACING), int(ystart), int((i+.5)*SPACING), int(ystop))

        for i in range(0,round(xstart/SPACING)-1, -1):
            painter.drawLine(int((i-.5)*SPACING), int(ystart), int((i-.5)*SPACING), int(ystop))

        for j in range(0, round(ystop/SPACING)+1):
            painter.drawLine(int(xstart), int((j+.5)*SPACING), int(xstop), int((j+.5)*SPACING))

        for j in range(0, round(ystart/SPACING)-1, -1):
            painter.drawLine(int(xstart), int((j-.5)*SPACING), int(xstop), int((j-.5)*SPACING))


    def map(self, x, y):
        return self._transform.map(x,y)
    
    def unmap(self, x, y):
        inverse_transform,_ = self._transform.inverted()
        return inverse_transform.map(x,y)
    
    def getScale(self):
        mx, my = self.unmap(1,0)
        ox, oy = self.unmap(0,0)
        return sqrt((mx-ox)**2+(my-oy)**2)
   
    def mouseMoveEvent(self, event) -> None:
        if event.buttons() == Qt.MouseButton.MiddleButton:
            mx, my = self.unmap(event.position().x()-self._d.x(), event.position().y()-self._d.y())
            ox, oy = self.unmap(0,0)
            self._transform.translate(mx-ox, my-oy)
            self._d = event.position()
            self.update()
    
    def mousePressEvent(self, event) -> None:
        if event.buttons() == Qt.MouseButton.MiddleButton:
            self._d = event.position()