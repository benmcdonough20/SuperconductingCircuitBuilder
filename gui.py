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
    QToolBox
)
from PyQt6.QtGui import QAction
from PyQt6.QtCore import Qt, QSize

import sys
from constants import *
from node import Ground
from connection import Anchor
from canvas import SmartCanvas
from branch_element import Capacitor, JosephsonJunction, Inductor, BranchElement 
from circuit import Circuit

MINSIZE = QSize(600,400)

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
        add_capacitor = QPushButton("Add Capacitor")
        #more items
        items_palette.addWidget(add_capacitor)

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
    
    class ElementMegawidget(Frame):
    
        def __init__(self, gui):
            super().__init__(gui.window)

            self.gui = gui
            self.editor = gui.PropertyEditor(self.gui)

            self.capacitor_button = Button(self, text = "Add Capacitor", command=lambda : self.gui.add_branch_element(Capacitor(0,0,self.gui.canvas)))
            self.inductor_button = Button(self, text = "Add Inductor", command=lambda : self.gui.add_branch_element(Inductor(0,0,self.gui.canvas)))
            self.jj_button = Button(self, text = "Add Josephson Junction", command=lambda : self.gui.add_branch_element(JosephsonJunction(0,0,self.gui.canvas)))
            self.ground_button = Button(self, text = "Add Ground", command=lambda : self.gui.add_ground(Ground(0,0,self.gui.canvas)))
            self.editor_button = Button(self, text = "Edit Properties", command = lambda: self.gui.edit_mode())
            self.export_button = Button(self, text = "Export to scQubits", command = lambda:self.gui.export())
            self.delete_button = Button(self, text = "Delete", command = lambda:self.gui.delete_mode())

            self.capacitor_button.grid(row = 0, column = 0, sticky = "ew")
            self.inductor_button.grid(row = 1, column = 0, sticky = "ew")
            self.jj_button.grid(row = 2, column = 0, sticky = "ew")
            self.ground_button.grid(row = 3, column = 0, sticky = "ew")
            self.editor_button.grid(row = 4, column = 0, sticky = "ew")
            self.export_button.grid(row = 5, column = 0, sticky = "ew")
            self.delete_button.grid(row = 6, column = 0, sticky = "ew")


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


    class PropertyEditor:

        def __init__(self, gui):
            self.gui = gui

        def open(self, object):
            
            window = Toplevel()
            frame = Frame(window)
            textVars = []

            for i,(name, field) in enumerate(object.properties.items()):
                var = StringVar()
                Entry(frame, textvariable = var).grid(row = i, column = 1)
                Label(frame, text = name).grid(row = i, column = 0)
                textVars.append(var)

            frame.pack()

            def cleanup():
                window.destroy()
                for name, text in zip(object.properties.keys(), textVars):
                    object.properties[name] = float(text.get())

                self.gui.canvas.redraw()

            close_button = Button(window, text = "Done", command = cleanup)
            close_button.pack()


if __name__ == '__main__':

    app = QApplication(sys.argv)
    gui = CircuitGui()
    app.exec()