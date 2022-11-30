from tkinter import Tk, Frame, mainloop,  Button, Toplevel, Entry, Label, StringVar
from constants import *
from node import Ground
from smart_canvas import SmartCanvas
from branch_element import Capacitor, JosephsonJunction, Inductor

class CircuitGui:
    def __init__(self):
        self.setup_gui()

        self.branch_elements = []
        self.nodes = []
        self.grounds = []

        self.add_ground(Ground(0,0, self.canvas))

    def setup_gui(self):
        self.window = Tk()
    
        self.window.columnconfigure(0, weight=0)
        self.window.columnconfigure(1, weight=1)
        self.window.rowconfigure(0, weight=1)

        self.buttons_pane = self.ElementMegawidget(self)
        self.buttons_pane.grid(row=0, column=0, sticky="n")

        self.canvas = SmartCanvas(self, width = DEFAULT_WIDTH, height=DEFAULT_HEIGHT, bg = BGCOLOR)
        self.canvas.grid(row=0, column = 1, columnspan=4, sticky="nsew")

    def export(self):
        for element in self.branch_elements:
            node1 = self.nodes.index(element.nodes[0])
            node2 = self.nodes.index(element.nodes[1])
            print(f"[{element} , {node1}, {node2}, {element.properties}")

    def edit_mode(self):
        self.canvas.state.edit()

    def delete_mode(self):
        self.canvas.state.delete()

    def edit(self, object):
        self.buttons_pane.editor.open(object)

    def add_branch_element(self, element):
        self.branch_elements.append(element)
        for node in element.nodes:
            self.nodes.append(node)

    def delete(self, element):
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

    def add_node(self, node):
        self.nodes.append(node)

    def add_ground(self, node):
        self.grounds.append(node)
    
    class ElementMegawidget(Frame):
    
        def __init__(self, gui):
            super().__init__(gui.window)

            self.gui = gui
            self.editor = gui.PropertyEditor()

            self.capacitor_button = Button(self, text = "Add Capacitor", command=lambda : self.gui.add_branch_element(Capacitor(0,0,self.gui.canvas)))
            self.inductor_button = Button(self, text = "Add Inductor", command=lambda : self.gui.add_branch_element(Inductor(0,0,self.gui.canvas)))
            self.jj_button = Button(self, text = "Add Josephson Junction", command=lambda : self.gui.add_branch_element(JosephsonJunction(0,0,self.gui.canvas)))
            self.ground_button = Button(self, text = "Add Ground", command=lambda : self.gui.add_ground(Ground(0,0,self.gui.canvas)))
            self.editor_button = Button(self, text = "Edit Properties", command = lambda: self.gui.edit_mode())
            self.export_button = Button(self, text = "Export to scQubits", command = lambda:self.gui.export())
            self.delete_button = Button(self, text = "Delete", command = lambda:self.gui.delete_mode())

            self.capacitor_button.grid(row = 0, column = 0)
            self.inductor_button.grid(row = 1, column = 0)
            self.jj_button.grid(row = 2, column = 0)
            self.ground_button.grid(row = 3, column = 0)
            self.editor_button.grid(row = 4, column = 0)
            self.export_button.grid(row = 5, column = 0)
            self.delete_button.grid(row = 6, column = 0)

    class PropertyEditor:

        def __init_(self, gui):
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
                    object.properties[name] = text.get()

            close_button = Button(window, text = "Done", command = cleanup)
            close_button.pack()


if __name__ == '__main__':

    gui = CircuitGui()
    mainloop()