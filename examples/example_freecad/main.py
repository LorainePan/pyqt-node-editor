import os, sys
from qtpy.QtWidgets import QDockWidget
from qtpy.QtCore import Qt

# Path to pyqt-node-editor
NODE_EDITOR_DIR = os.path.join(App.getUserAppDataDir(), "Macro", "pyqt-node-editor")

# Append NODE_EDITOR_DIR to python path
if NODE_EDITOR_DIR not in sys.path:
	sys.path.insert(0, NODE_EDITOR_DIR)

# Load pyqt-node-editor module
from examples.example_freecad.calc_sub_window import CalculatorSubWindow

if __name__ == '__main__':
    fcMainWindow = FreeCADGui.getMainWindow() # Get FreeCAD main window
    myWidget = QDockWidget() # Create dock widget
    myWidget.setWidget(CalculatorSubWindow()) # Add node editor to widget
    fcMainWindow.addDockWidget(Qt.RightDockWidgetArea, myWidget) # Add widget to right dock