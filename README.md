# CircuitBuilder
This is a GUI for designing superconducting circuits intended to accompany the python package scQubits.

## Usage
Start wih `python gui.py`. The elements used to build a circuit are
1) Capacitor
2) Inductor
3) Josephson Junction

Drag the icons from the toolbox onto the canvas to place down an element. Drag nodes together to connect them. Left-click on wires to add anchor points and drag 
the anchor points to guide the wires.

### Keyboard
* `Shift + Right Click` - add to selection
* `Shift + Right Drag` - add box to selection
* `Enter` on property entry box - change property

### Mouse
* `Left Button Drag` on whitespace - pan
* `Left Button Drag` on element/selected group - move selection
* `Right Button Drag` - box selection
* `Left Button Click` on element - rotate
* `Right Button Click` on element - select and show properties

![Screenshot indicating usage](./screenshot.png "screenshot")

## Features
* Split nodes
* Delete elements
* Wire anchor points
* Undo / Redo
* Save / Open
* Export to scQubits circuit format
* Import circuits representing scQubits objects

## Dependencies
* Python 3.10.8
* PyQt 6.4.0

## Know issues
There are still many bugs!
* Right click has no activation distance, so using a mouse will result in some dropped right clicks
* Sometime import/undo/redo crashes, but it usually seems to work 

