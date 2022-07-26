import os, sys
from qtpy.QtWidgets import QMainWindow
from qtpy.QtCore import Qt

# Path to pyqt-node-editor
NODE_EDITOR_DIR = os.path.join(App.getUserAppDataDir(), "Macro", "pyqt-node-editor")

# Append NODE_EDITOR_DIR to python path
if NODE_EDITOR_DIR not in sys.path:
	sys.path.insert(0, NODE_EDITOR_DIR)

# Load pyqt-node-editor modules
from examples.example_freecad.calc_window import CalculatorWindow

if __name__ == '__main__':
    # Setup node editor window
    fc_main_window = FreeCADGui.getMainWindow()
    clc_wnd = CalculatorWindow()
    mw = QMainWindow(parent=fc_main_window)
    mw.setCentralWidget(clc_wnd)
    mw.show()