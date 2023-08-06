from PySide6.QtWidgets import (
    QMainWindow, 
    QApplication, 
    QSpacerItem,
    QSizePolicy,
    QToolBar, 
    QDockWidget,
    QWidget,
    QVBoxLayout,
    QLabel,
    QFileDialog,
    QPushButton
)
import pickle
from PySide6.QtGui import QDrag, QIcon, QAction
from PySide6.QtCore import Qt, QMimeData, QPoint

from pathlib import Path

import sys
import os
from sccircuitbuilder.constants import *
from sccircuitbuilder.canvas import SmartCanvas, ObjectFactory
from sccircuitbuilder.circuit import Circuit
from sccircuitbuilder.caretaker import Caretaker 

class CircuitBuilder(QMainWindow):

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Circuit Builder")
        self.setMinimumSize(MINSIZE)

        self.canvas = SmartCanvas(self)

        self.init_toolbox()
        self.init_menu()
        self.init_toolbar()

        self.caretaker = Caretaker()
        self.take_snapshot()

        self.setCentralWidget(self.canvas)
        self.show()

    def init_toolbox(self):
        self.toolsdock = ToolDock(self.import_circuit, self.export)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.toolsdock) 

    def init_toolbar(self):
        self.toolbar = QToolBar(self)

        undo = QAction("", self)
        undo.setIcon(QIcon(os.path.join(os.path.dirname(__file__),"icons/undo")))
        self.toolbar.addAction(undo)
        undo.triggered.connect(self.undo)

        redo = QAction("", self)
        redo.setIcon(QIcon(os.path.join(os.path.dirname(__file__),"icons/redo")))
        self.toolbar.addAction(redo)
        redo.triggered.connect(self.redo)

        clear = QAction("", self)
        clear.setIcon(QIcon(os.path.join(os.path.dirname(__file__),"icons/clear")))
        self.toolbar.addAction(clear)
        clear.triggered.connect(self.canvas.clear)
        
        self.addToolBar(self.toolbar) 
    
    def init_menu(self):
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu('&File')
        save_file = QAction("Save", self)
        file_menu.addAction(save_file)
        save_file.triggered.connect(self.save_dialogue)

        open_file = QAction("Open", self)
        file_menu.addAction(open_file)
        open_file.triggered.connect(self.open_dialogue)

        export_circuit = QAction("Export to scQubits", self)
        file_menu.addAction(export_circuit)
        export_circuit.triggered.connect(self.export)

        import_circuit = QAction("Import circuit", self)
        file_menu.addAction(import_circuit)
        import_circuit.triggered.connect(self.import_dialogue)
        

        toolbar_menu = menu_bar.addMenu('&Tools')

        show_toolbox = QAction("Dock Toolbox", self)
        show_toolbox.triggered.connect(self.toolsdock.redock)

        toolbar_menu.addAction(show_toolbox)

    def save(self, fname):
        with open(fname, "wb") as savefile:
            save = Circuit.CircuitMemento(self.canvas.objects)
            pickle.dump(save, savefile)
    
    def open(self, fname):
        with open(fname, "rb") as openfile:
            saved = pickle.load(openfile)
            self.canvas.restore(saved)

    def take_snapshot(self):
        self.caretaker.add_snapshot(Circuit.CircuitMemento(self.canvas.objects))

    def redo(self):
        snapshot = self.caretaker.redo()
        self.canvas.restore(snapshot)
    
    def undo(self):
        snapshot = self.caretaker.undo()
        self.canvas.restore(snapshot)

    def save_dialogue(self):
        fname,_ = QFileDialog.getSaveFileName(
                self,
                "Save File",
                "./",
                "circuits (*.circuit)",
            )
        self.save(fname+".circuit")
    
    def open_dialogue(self):
        fname,_ = QFileDialog.getOpenFileName(
                self,
                "Open File",
                "./",
                "circuits (*.circuit)"
            )
        self.open(fname)
    
    def export(self):
        fname,_ = QFileDialog.getSaveFileName(
                self,
                "Save File",
                "./",
                "ScQubits circuit (*.yml)",
            )
        with open(fname+".yml", "w") as f:
            f.write(str(self.canvas.objects))

    def import_dialogue(self):
        fname,_ = QFileDialog.getOpenFileName(
                self,
                "Import File",
                "./",
                "circuits (*.circuit)"
            )
        self.import_circuit(fname)
     
    def import_circuit(self, fname):
        with open(fname, "rb") as openfile:
            saved = pickle.load(openfile)
            new_circuit = Circuit()
            new_circuit.load(saved)
            self.canvas.import_circuit(new_circuit)
            self.take_snapshot()

class ToolDock(QDockWidget):
    
    def __init__(self, import_circuit, export_circuit):
        super().__init__()
        toolbox = QWidget()
        self._layout = QVBoxLayout()
        toolbox.setLayout(self._layout)
        self.setWidget(toolbox)

        self._elements()
        self._nodes()
        self._circuits(import_circuit)
        self._gui_options(export_circuit)

        self._layout.addSpacerItem(QSpacerItem(
            0,
            0,
            QSizePolicy.Policy.Ignored, QSizePolicy.Policy.MinimumExpanding
        ))
    
    def _elements(self):
        section_label = QLabel("Branch Elements")
        add_capacitor = DragLabel(
            "Add Capacitor", 
            ObjectFactory.capacitor, 
            os.path.join(os.path.dirname(__file__),"elements/capacitor.svg"), 
            ICON_SIZE, 
            .5*ICON_SIZE
        )
        add_inductor = DragLabel(
            "Add Inductor", 
            ObjectFactory.inductor, 
            os.path.join(os.path.dirname(__file__),"elements/Inductor.svg"),
            ICON_SIZE, 
            .5*ICON_SIZE
        )
        add_junction = DragLabel(
            "Add Josephson Junction", 
            ObjectFactory.junction, 
            os.path.join(os.path.dirname(__file__),"elements/JJ.svg"), 
            ICON_SIZE, 
            .5*ICON_SIZE
        )
        self._layout.addWidget(section_label)
        self._layout.addWidget(add_capacitor)
        self._layout.addWidget(add_inductor)
        self._layout.addWidget(add_junction)

    def _nodes(self):
        section_label = QLabel("Nodes")
        add_ground = DragLabel(
            "Add Ground", 
            ObjectFactory.ground, 
            os.path.join(os.path.dirname(__file__),"elements/ground.svg"), 
            .4*ICON_SIZE, 
            .4*ICON_SIZE
        )
        self._layout.addWidget(section_label)
        self._layout.addWidget(add_ground)

    def _circuits(self, import_circuit):
        section_label = QLabel("Circuits")
        self._layout.addWidget(section_label)
        circuits_dir = Path(__file__).parent / "circuits"
        for entry in circuits_dir.iterdir():
            add_circuit = QPushButton(entry.stem)
            add_circuit.clicked.connect(CircuitImport(entry.name, import_circuit))
            self._layout.addWidget(add_circuit)
    
    def _gui_options(self, export):
        section_label = QLabel("Gui Options")
        self._layout.addWidget(section_label)
        show_toolbox = QPushButton("Dock Toolbox", self)
        show_toolbox.clicked.connect(self.redock)
        self._layout.addWidget(show_toolbox)
        export_button = QPushButton("Export to scQubits", self)
        export_button.clicked.connect(export)
        self._layout.addWidget(export_button)
    
    def redock(self):
        self.setFloating(False)
        self.show()

class CircuitImport:
    def __init__(self, name, update):
        self.name = name
        self.update = update
    
    def __call__(self):
        self.update(os.path.join(os.path.dirname(__file__),"circuits/")+self.name)

class DragLabel(QLabel):

    def __init__(self, text, element, icon_path, icon_width, icon_height):
        super().__init__(text)
        self.element = element
        self.icon = QIcon(icon_path).pixmap(icon_width, icon_height)
        self.setPixmap(self.icon)
        self.setMaximumWidth(icon_width)
        self.center = QPoint(icon_width/2, icon_width/4)
    
    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton:
            mime_data = QMimeData()
            mime_data.setText(self.element)
            drag = QDrag(self)
            drag.setMimeData(mime_data)
            drag.setPixmap(self.icon)
            drag.setHotSpot(self.center)
            drag.exec(Qt.DropAction.MoveAction)
            event.accept()

def GUI():
    app = QApplication(sys.argv)
    gui = CircuitBuilder()
    app.exec()

if __name__ == '__main__':
    GUI()    