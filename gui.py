from tkinter import Tk, Frame, mainloop, Toplevel, StringVar
from tkinter.ttk import Button, Label, Entry

from PyQt6.QtWidgets import (
    QMainWindow, 
    QApplication, 
    QGraphicsView, 
    QSpacerItem,
    QSizePolicy,
    QToolBar, 
    QDockWidget,
    QWidget,
    QVBoxLayout,
    QPushButton,
    QToolBox,
    QLabel,
)
from PyQt6.QtGui import QAction, QDrag 
from PyQt6.QtCore import Qt, QSize, QMimeData

import sys
from constants import *
from node import Ground
from connection import Anchor
from canvas import SmartCanvas
from branch_element import Capacitor, JosephsonJunction, Inductor, BranchElement 
from circuit import Circuit

MINSIZE = QSize(800,600)

class CircuitGui(QMainWindow):

    def __init__(self):
        super().__init__()
        self.circuit = Circuit()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Circuit Builder")
        self.setMinimumSize(MINSIZE)

        canvas = SmartCanvas()

        self.init_menu()
        self.init_toolbar()
        self.init_toolbox()

        self.setCentralWidget(canvas)
        self.show()

    def init_toolbar(self):
        toolbar = QToolBar()
        undo = QAction("Undo", toolbar)
        redo = QAction("Redo", toolbar)

        toolbar.addAction(undo)
        toolbar.addAction(redo)

        self.addToolBar(toolbar)
    
    def init_toolbox(self):
        toolsdock = self.ToolsPanel(self) 

        items_palette = toolsdock.add_section("Branch Elements")
        add_capacitor = DragLabel("Add Capacitor", "capacitor")
        add_inductor = DragLabel("Add Inductor", "inductor")
        add_junction = DragLabel("Add Josephson Junction", "junction")
        #more items
        items_palette.addWidget(add_capacitor)
        items_palette.addWidget(add_inductor)
        items_palette.addWidget(add_junction)

        nodes_palette = toolsdock.add_section("Nodes")
        add_ground = QPushButton("Add Ground")
        nodes_palette.addWidget(add_ground)

        circuits_palette = toolsdock.add_section("Circuits")
        transmon = QPushButton("Transmon")
        #more circuits
        circuits_palette.addWidget(transmon)

        toolsdock.squash(items_palette)
        toolsdock.squash(circuits_palette)
        toolsdock.squash(nodes_palette)

        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, toolsdock) 
    
    def init_menu(self):
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu('&File')
        edit_menu = menu_bar.addMenu('&Edit')
        help_menu = menu_bar.addMenu('&Help')

    def export(self):
        print("--------")
        for element in self.branch_elements:
            print(element)

    def edit_mode(self):
        self.canvas.state.edit()

    def delete_mode(self):
        self.canvas.state.delete()

    def edit(self, object):
        self.buttons_pane.editor.open(object)

    def add_branch_element(self, element):
        self.branch_elements.append(element)
        for node in element.nodes:
            self.add_node(node)

    def delete(self, object):
        if issubclass(type(object), BranchElement):
            self.delete_branch_element(object)
        elif type(object) == Anchor:
            object.delete()
            
    def delete_branch_element(self, element):
        self.branch_elements.remove(element)
        self.canvas.toplayer.remove(element)
        for node in element.nodes:
            if len(node.elements) == 1:
                self.nodes.remove(node)
                self.canvas.toplayer.remove(node)
            else:
                node.elements.remove(element)
        for connection in element.connections:
            self.canvas.bottomlayer.remove(connection)
        self.canvas.redraw()

    def remove_node(self, node):
        self.nodes.remove(node)
        for i,node in enumerate(self.nodes):
            node.idx = i+1

    def add_node(self, node):
        node.idx = len(self.nodes)+1
        self.nodes.append(node)

    def add_ground(self, node):
        self.grounds.append(node)
    

    class ToolsPanel(QDockWidget):
        
        def __init__(self, *args, **kwargs):

            super().__init__(*args, **kwargs)

            self.toolbox = QToolBox(self)
            self.setWidget(self.toolbox)
        
        def add_section(self,name):
            section = QWidget(self.toolbox)
            layout = QVBoxLayout()
            section.setLayout(layout)
            self.toolbox.addItem(section, name)
            return layout
        
        def squash(self, section):
            spacer = QSpacerItem(0,0,QSizePolicy.Policy.Ignored, QSizePolicy.Policy.MinimumExpanding)
            section.addItem(spacer)


class DragLabel(QLabel):
    def __init__(self, text, element):
        super().__init__(text)
        self.element = element
    
    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton:
            mime_data = QMimeData()
            mime_data.setText(self.element)
            drag = QDrag(self)
            drag.setMimeData(mime_data)
            drag.setPixmap(self.grab(self.rect()))
            drag.exec(Qt.DropAction.MoveAction)
            event.accept()

if __name__ == '__main__':

    app = QApplication(sys.argv)
    gui = CircuitGui()
    app.exec()