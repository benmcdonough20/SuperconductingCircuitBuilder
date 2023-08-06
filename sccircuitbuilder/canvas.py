from PySide6.QtWidgets import QFrame, QApplication
from PySide6.QtGui import QColorConstants, QTransform, QPen, QPainter, QBrush, QNativeGestureEvent, QInputDevice
from PySide6.QtCore import Qt

from sccircuitbuilder.circuit import Circuit
from sccircuitbuilder.constants import *
from sccircuitbuilder.node import Ground
from sccircuitbuilder.branch_element import Capacitor, Inductor, JosephsonJunction, BranchElement

class SmartCanvas(QFrame):
    
    def __init__(self, gui):
        super().__init__()

        self.setAcceptDrops(True)
            
        self.painter = QPainter()
        self.gui = gui

        #world transform and put origin at center of screen
        self._transform = QTransform()
        self._transform.translate(self.width()/2, self.height()/2)

        self.objects = Circuit() #list of objects that can be clicked
        self.selected_object = None #object that is currently selected
        self.selected_group = SelectedGroup()

        self.objectfactory = ObjectFactory(self.objects)

        self.object_toolbar = None

        self._dragging = False

        self._zoom_factor = 1 #limit zoom due to buggy rounding behavior

        self._mouse_button = None

    def world_point(self, event):
        return self.map(Point(event.pos().x(), event.pos().y()))

    def wheelEvent(self, event): #wheel scroll #for windows?
        if event.device().type() == QInputDevice.DeviceType.TouchPad:
            self._transform.translate(event.pixelDelta().x(), event.pixelDelta().y())
        else:
            self._zoomEvent(event.angleDelta().y(), event)
        self.update()

    def event(self, event):
        if isinstance(event, QNativeGestureEvent):
            if isinstance(event, QNativeGestureEvent) and event.gestureType() == Qt.NativeGestureType.ZoomNativeGesture:
                return self._zoomEvent(event.value()*1000, event)
        return super().event(event)

    def zoomNativeEvent(self, event): #MacOS compatibility
        self._zoomEvent(event.value(), event)
    
    def _zoomEvent(self, value, event):
        direction = 0
        if value > 0:
            if MAX_ZOOM > self._zoom_factor:
                direction = value 
        else:
            if MIN_ZOOM < self._zoom_factor:
                direction = value

        #zoom on mouse pointer
        center_on = self.world_point(event)
        self._zoom(center_on, direction)

        self.update()

    def object_under(self, point, skip = False, skip_obj = None):
        for object in self.objects:
            if skip and object is skip_obj:
                continue
            if object.in_bbox(point):
                return object
        return None
    
    def _zoom(self, center, direction):
        self._zoom_factor *= (1+direction*ZOOM_SPEED) #keep track of zoom amount

        #zoom centered on mouse pointer
        self._transform.translate(
            -center.x*direction*ZOOM_SPEED, 
            -center.y*direction*ZOOM_SPEED
            )
        self._transform.scale(1+direction*ZOOM_SPEED, 1+direction*ZOOM_SPEED)
        

    def paintEvent(self, event):
        self.painter.begin(self)
        self.painter.setTransform(self._transform)
        self.painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        self._background()

        for object in self.objects:
            object.paint(self.painter)

        if self.selected_group:
            self._selection_box()

        self.selected_group.paint(self.painter)
        self.painter.end()

    def _selection_box(self):

        pen = QPen(QColorConstants.Red, 2, Qt.PenStyle.DashLine)
        self.painter.setPen(pen)
        for object in self.selected_group:
            if object.bbox:
                self.painter.drawRect(
                    int(object.x-object.bbox.width/2),
                    int(object.y-object.bbox.height/2),
                    int(object.bbox.width),
                    int(object.bbox.height)
                )

    def _background(self): #solid background with grid
        painter = self.painter

        width = self.width()
        height = self.height()

        start = self.map(ORIGIN)
        stop = self.map(Point(width, height))

        painter.fillRect(
            int(start.x),
            int(start.y), 
            int(stop.x-start.x), 
            int(stop.y-start.y), 
            BGCOLOR)

        painter.setPen(QPen(QColorConstants.LightGray, 1))
        for i in range(round(start.x/SPACING),round(stop.x/SPACING)+1):
            painter.drawLine(int((i+.5)*SPACING), int(start.y), int((i+.5)*SPACING), int(stop.y))

        for j in range(round(start.y/SPACING), round(stop.y/SPACING)+1):
            painter.drawLine(int(start.x), int((j+.5)*SPACING), int(stop.x), int((j+.5)*SPACING))


    def map(self, point): #map device coordinates to world coordinates
        inverse_transform,_ = self._transform.inverted()
        return Point(*inverse_transform.map(point.x, point.y))
    
    def mouseMoveEvent(self, event) -> None: #TODO: how to detect trackpad?
        mouseloc = self.world_point(event) 
        if event.buttons() == Qt.MouseButton.LeftButton: #left button drag
            if self.selected_object:
                self._dragging = True
                self._drag(mouseloc)
            else:
                self._pan(event)
        elif event.buttons() == Qt.MouseButton.RightButton:
            self.selected_group.selecting = True
            self.selected_group.drag(mouseloc)

        self.update()
    
    def _drag(self, point):
        if len(self.selected_group) > 1:
            self.selected_group.drag(point)
        elif self.selected_object:
            self.selected_object.drag(point)

    def _pan(self, event):
        #get mouse displacement in world coordinates
        displacement = Point(event.pos().x(), event.pos().y()) - self._displacement

        #scale displacement relative to coordinate scaling and translate
        self._transform.translate(displacement.x/self._zoom_factor, displacement.y/self._zoom_factor)
        #update position to compute next displacement
        self._displacement += displacement
        
    def mousePressEvent(self, event) -> None:
        self._displacement = Point(event.pos().x(), event.pos().y())
        mouseloc = self.world_point(event) 
        if event.buttons() == Qt.MouseButton.LeftButton: #select object under mouse
            self.leftButtonPress(mouseloc)
        elif event.buttons() == Qt.MouseButton.RightButton:
            self.rightButtonPress(mouseloc) 
        self._mouse_button = event.buttons()
    
    def leftButtonPress(self, mouseloc):
        self.selected_group.set_orig(mouseloc) #set relative origin before triggering drag
        obj = self.object_under(mouseloc)
        if obj:
            self.selected_object = obj
            obj.press(mouseloc)
        else:
            self.selected_object = None

    def rightButtonPress(self, mouseloc):
        self.selected_group.set_orig(mouseloc) #set left corner of selection box
       
    def mouseReleaseEvent(self,event):
        mouseloc = self.world_point(event)
        if self._mouse_button == Qt.MouseButton.LeftButton:
            self.leftButtonRelease(mouseloc)
        elif self._mouse_button == Qt.MouseButton.RightButton:
            self.rightButtonRelease(mouseloc)
        self.update()
    
    def leftButtonRelease(self, mouseloc):
        if self._dragging:
            self.drop(mouseloc)
        else:
            self.leftclick(mouseloc)
        self._dragging = False

    def rightButtonRelease(self, mouseloc):
            if self.selected_group.selecting:
                self.group_select()
            else:
                self.rightclick(mouseloc) 

    def drop(self, point):
        for object in self.objects:
            if object is self.selected_object:
                continue
            if object.in_bbox(point) and self.selected_object:
                self.selected_object.drop(point, object)
                break
        self.gui.take_snapshot()
        self.selected_object = None

    def import_circuit(self, circuit):
        self.selected_group.clear()
        self.selected_group += circuit.nodes
        self.selected_group += circuit.anchors
        self.selected_group += circuit.elements
        self.selected_group += circuit.grounds
        self.objects.add_circuit(circuit)
        self.update()

    def clear(self):
        self.objects.clear()
        self.selected_group.clear()
        self.gui.take_snapshot()
        self.load_options()
        self.update()

    def group_select(self):
        if self.selected_group.selecting:
            self.selected_group.selecting = False
            self.selected_group.clear()
            for object in self.objects:
                if self.selected_group.in_bbox(object):
                    self.selected_group.append(object)
            self.load_options()
            return

    def load_options(self):
        if self.object_toolbar:
            self.gui.removeToolBar(self.object_toolbar)
            self.object_toolbar = None
        if len(self.selected_group) == 1:
            object, = self.selected_group
            def update_and_check():
                self.update()
                if not object in self.objects:
                    self.gui.removeToolBar(self.object_toolbar)
                    self.object_toolbar = None
                    self.selected_group.clear()
                self.gui.take_snapshot()
            try:
                self.object_toolbar = object.toolbar(update_and_check)
                self.gui.addToolBar(self.object_toolbar)
            except:
                pass
          
    def dragEnterEvent(self, event) -> None:
        event.accept()
    
    def dropEvent(self, event) -> None:
        eventloc = self.world_point(event)
        if not self.object_under(eventloc):
            self.objectfactory.create(event.mimeData().text(), eventloc)
            self.update()
            self.gui.take_snapshot()

    def rightclick(self, mouseloc) :
        modifiers = QApplication.keyboardModifiers()
        shift_modifier = (modifiers == Qt.KeyboardModifier.ShiftModifier)

        object = self.object_under(mouseloc)
        if object:
            in_group = (object in self.selected_group)
            in_bbox = (object.in_bbox(mouseloc))
            group_select = len(self.selected_group) > 1

            if in_bbox:
                if in_group:
                    if shift_modifier or (not shift_modifier and not group_select):
                        self.selected_group.remove(object)
                    else:
                        self.selected_group.clear()
                        self.selected_group.append(object)
                else:
                    if not shift_modifier:
                        self.selected_group.clear()
                    self.selected_group.append(object)
        else:
            self.selected_group.clear()
        self.load_options()
                        
    def leftclick(self, mouseloc):
        if self.selected_object:
            self.selected_object.rotate()
            self.gui.take_snapshot()
    
    def restore(self, memento):
        try:
            self.selected_group.clear()
            self.objects.restore(memento)
            self.update()
        except:
            pass

class SelectedGroup(list):
    def __init__(self):
        super().__init__()
        self.offsets = []
        self.rel_orig = ORIGIN
        self.corner = ORIGIN
        self.selecting = False
   
    def set_orig(self, point):
        self.rel_orig = point
        self.corner = point
        self.offsets.clear()
        for obj in self:
            self.offsets.append(Point(obj.x, obj.y))
    
    def drop(self):
        self.selecting = False
    
    def in_bbox(self, point):
        xmin = min([self.corner.x, self.rel_orig.x])
        xmax = max([self.corner.x, self.rel_orig.x])
        ymin = min([self.corner.y, self.rel_orig.y])
        ymax = max([self.corner.y, self.rel_orig.y])
        return (point.x > xmin and point.x < xmax and point.y > ymin and point.y < ymax)
    
    def paint(self, painter):
        if self.selecting:
            pen = QPen(QColorConstants.Red, 2, Qt.PenStyle.DashLine)
            brush = QBrush(QColorConstants.Red, Qt.BrushStyle.Dense7Pattern)
            painter.setPen(pen)
            painter.fillRect(
                int(self.rel_orig.x), 
                int(self.rel_orig.y), 
                int(self.corner.x-self.rel_orig.x), 
                int(self.corner.y-self.rel_orig.y),
                brush
            )

    def drag(self, point):
        if self.selecting:
            self.corner = point
        else:
            disp = point-self.rel_orig
            for obj,offset in zip(self, self.offsets):
                obj.drag(offset + disp)

class ObjectFactory:

    capacitor = "capacitor"    
    inductor = "inductor" 
    junction = "junction"
    ground = "ground"

    def __init__(self, circuit):
        self.circuit = circuit
        self.factory = {
            self.capacitor : Capacitor,
            self.inductor : Inductor,
            self.junction : JosephsonJunction,
            self.ground : Ground
        }

    def create(self, key, point):
        self.factory[key](point, self.circuit)
