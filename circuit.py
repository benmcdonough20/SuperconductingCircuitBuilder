from canvas_element import CanvasElement
from node import Ground

class Circuit(CanvasElement):
    
    def __init__(self):
        
        self.elements = []
        self.nodes = []