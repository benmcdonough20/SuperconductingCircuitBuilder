class UndoRedoException(Exception):
    ...

class Caretaker:
    def __init__(self):
        self.history = []
        self.idx = -1

    def add_snapshot(self, snapshot):
        self.idx += 1
        if self.idx < len(self.history):
            self.history = self.history[:self.idx]
        self.history.append(snapshot)
    
    def undo(self):
        try:
            self.idx -= 1
            return self.restore(self.idx)
        except IndexError:
            raise UndoRedoException()

    def redo(self):
        try:
            self.idx += 1
            return self.restore(self.idx)

        except IndexError as e:
            raise UndoRedoException()
        
    def restore(self, index):
        if index == -1:
            raise IndexError
        return self.history[index]