from itertools import chain
from sccircuitbuilder.node import Node, Ground
from sccircuitbuilder.branch_element import BranchElement
from sccircuitbuilder.connection import Connection, Anchor, Wire
from sccircuitbuilder.constants import Point, SPACING

class Circuit:
    
    def __init__(self):
        
        self.elements = []
        self.nodes = []
        self.grounds = []
        self.connections = []
        self.anchors = []

    def add_element(self, element):
        self.elements.append(element)

    def remove_element(self, element):
        self.elements.remove(element)
        for node in element.nodes:
            if len(node.elements) == 1:
                node.delete()
            else:
                node.elements.remove(element)
        for connection in element.connections:
            self.remove_connection(connection)
    
    def add_ground(self, ground):
        self.grounds.append(ground)
    
    def remove_ground(self, ground):
        self.grounds.remove(ground)
    
    def remove_node(self, node):
        self.nodes.remove(node)
        for i,node in enumerate(self.nodes):
            node.idx = i+1 

    def add_connection(self, connection):
        self.connections.append(connection)
    
    def remove_connection(self, connection):
        self.connections.remove(connection)
        for anchor in connection.anchors:
            self.remove_anchor(anchor)
    
    def add_node(self, node):
        node.idx = len(self.nodes)+1
        self.nodes.append(node)
    
    def add_circuit(self, circuit):
        for elt in circuit:
            elt.circuit = self
        self.nodes += circuit.nodes
        self.elements += circuit.elements
        self.grounds += circuit.grounds
        self.connections += circuit.connections
        self.anchors += circuit.anchors
        for i,node in enumerate(self.nodes):
            node.idx = i+1
    
    def add_anchor(self, anchor):
        self.anchors.append(anchor)

    def remove_anchor(self, anchor):
        self.anchors.remove(anchor)

    def __iter__(self):
        return chain(self.elements, self.nodes, self.grounds, self.anchors, self.connections)

    def clear(self):
        self.elements.clear()
        self.nodes.clear()
        self.anchors.clear()
        self.connections.clear()
        self.grounds.clear()
    
    def restore(self, memento):
        self.clear()
        self.load(memento)

    def load(self, memento):
        self.node_idxs = [node.idx for node in memento.node_mementos]
        self.ground_idxs = [ground.idx for ground in memento.ground_mementos]

        self._load_nodes(memento)
        self._load_grounds(memento)
        self._load_elements(memento)
        
    def _load_nodes(self, memento):
        for node_mem in memento.node_mementos:
            newnode = Node(node_mem.loc, self)
            newnode.idx = node_mem.idx 
    
    def _load_grounds(self, memento):
        for ground_mem in memento.ground_mementos:
            newground = Ground(ground_mem.loc, self)
            for i in range(ground_mem.rot):
                newground.rotate()

    def _load_elements(self, memento):
        for element_mem in memento.element_mementos:
            self._load_element(element_mem)

    def _load_element(self, element_mem):
        new_element = BranchElement(element_mem.loc , self)
        new_element.icon = element_mem.icon
        new_element.setIcon(new_element.icon, SPACING, SPACING)
        new_element.name = element_mem.name
        for i in range(element_mem.rot):
            new_element.rotate_icon()
        new_element.properties = element_mem.properties

        for node in new_element.nodes:
            self.remove_node(node)
        new_element.nodes.clear()

        for connection in new_element.connections:
            self.remove_connection(connection)
        new_element.connections.clear()

        self._setup_nodes(new_element, element_mem) 
        for conn_memo in element_mem.conn_memos:
            self._setup_connection(new_element, conn_memo)
            
    
    def _setup_nodes(self, new_element, element_mem):
        for node_idx in element_mem.nodes:
            new_element.nodes.append(self.nodes[self.node_idxs.index(node_idx)])
            self.nodes[self.node_idxs.index(node_idx)].elements.append(new_element)
        for gnd_idx in element_mem.grounds:
            new_element.nodes.append(self.grounds[self.ground_idxs.index(gnd_idx)])
            self.grounds[self.ground_idxs.index(gnd_idx)].elements.append(new_element)
    
    def _setup_connection(self, new_element, conn_memo):
        try:
            node = self.nodes[self.node_idxs.index(conn_memo.dest)]
            new_conn = Connection(new_element, node, conn_memo.d, self)
            node.connections.append(new_conn)
        except:
            ground = self.grounds[self.ground_idxs.index(conn_memo.dest)]
            new_conn = Connection(new_element, ground, conn_memo.d, self)
            ground.connections.append(new_conn)
        if conn_memo.anchors:
            for anchor_pt in conn_memo.anchors:
                new_conn.anchors.append(Anchor(anchor_pt, self, new_conn))
            new_conn.wires[0].dest = new_conn.anchors[0]
            for i in range(len(new_conn.anchors)-1):
                new_conn.wires.append(Wire(new_conn.anchors[i], new_conn.anchors[i+1], Point(0,0)))
            new_conn.wires.append(Wire(new_conn.anchors[-1], new_conn.dest, Point(0,0)))
            new_conn.rewire()
        new_element.connections.append(new_conn)
        

    def __str__(self):
        strs = []
        strs.append("branches:\n")
        for element in self.elements:
            strs.append(str(element)+"\n")
        return "".join(strs)

    class CircuitMemento:
        def __init__(self, circuit):
            for i,gnd in enumerate(circuit.grounds):
                gnd.idx = len(circuit.nodes)+i+5
            self.cutoff = len(circuit.nodes)
            self.ground_mementos = [Node.NodeMemento(ground) for ground in circuit.grounds]
            self.node_mementos = [Node.NodeMemento(node) for node in circuit.nodes]
            self.element_mementos = [BranchElement.ElementMomento(element) for element in circuit.elements]
            self.connection_mementos = [Connection.ConnectionMomento(conn) for conn in circuit.connections]
            for gnd in circuit.grounds:
                gnd.idx = 0