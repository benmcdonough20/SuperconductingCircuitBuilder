from tkinter import Tk, Frame, mainloop,  Button
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

        #self.add_ground(Ground(0,0, self.canvas))


    def setup_gui(self):
        self.window = Tk()
    
        self.window.columnconfigure(0, weight=0)
        self.window.columnconfigure(1, weight=1)
        self.window.rowconfigure(0, weight=1)

        self.buttons_pane = self.ElementMegawidget(self)
        self.buttons_pane.grid(row=0, column=0, sticky="n")

        self.canvas = SmartCanvas(self, width = DEFAULT_WIDTH, height=DEFAULT_HEIGHT, bg = BGCOLOR)
        self.canvas.grid(row=0, column = 1, columnspan=4, sticky="nsew")

    
    def add_branch_element(self, element):
        self.branch_elements.append(element)
        for node in element.nodes:
            self.nodes.append(node)


    def add_node(self, node):
        self.nodes.append(node)

    def add_ground(self, node):
        self.grounds.append(node)
    
    class ElementMegawidget(Frame):
    
        def __init__(self, gui):
            super().__init__(gui.window)

            self.gui = gui

            self.capacitor_button = Button(self, text = "Add Capacitor", command=lambda : self.gui.add_branch_element(Capacitor(0,0,self.gui.canvas)))
            self.inductor_button = Button(self, text = "Add Inductor", command=lambda : self.gui.add_branch_element(Inductor(0,0,self.gui.canvas)))
            self.jj_button = Button(self, text = "Add Josephson Junction", command=lambda : self.gui.add_branch_element(JosephsonJunction(0,0,self.gui.canvas)))
            self.ground_button = Button(self, text = "Add Ground", command=lambda : self.gui.add_ground(Ground(0,0,self.gui.canvas)))

            self.capacitor_button.grid(row = 0, column = 0)
            self.inductor_button.grid(row = 1, column = 0)
            self.jj_button.grid(row = 2, column = 0)
            self.ground_button.grid(row = 3, column = 0)
    
if __name__ == '__main__':

    gui = CircuitGui()
    mainloop()