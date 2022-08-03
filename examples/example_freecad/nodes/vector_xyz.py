import os
from qtpy.QtCore import Qt, QRectF
from qtpy.QtGui import QImage
from qtpy.QtWidgets import QLineEdit, QLabel
from nodeeditor.node_node import Node
from nodeeditor.node_socket import LEFT_CENTER, RIGHT_CENTER
from nodeeditor.node_graphics_node import QDMGraphicsNode
from nodeeditor.node_content_widget import QDMNodeContentWidget
from examples.example_freecad.calc_conf import register_node, OP_NODE_VEC_XYZ
from nodeeditor.utils import dumpException
import FreeCAD as App


class VecXYZGraphicsNode(QDMGraphicsNode):
    def initSizes(self):
        super().initSizes()
        self.width = 160
        self.height = 95
        self.edge_roundness = 6
        self.edge_padding = 0
        self.title_horizontal_padding = 8
        self.title_vertical_padding = 10

    def initAssets(self):
        super().initAssets()
        status_icon = os.path.join(App.getUserAppDataDir(), "Macro", "pyqt-node-editor", "examples",
                            "example_freecad", "icons", "status_icons.png")
        self.icons = QImage(status_icon)

    def paint(self, painter, QStyleOptionGraphicsItem, widget=None):
        super().paint(painter, QStyleOptionGraphicsItem, widget)

        offset = 24.0
        if self.node.isDirty(): offset = 0.0
        if self.node.isInvalid(): offset = 48.0

        painter.drawImage(
            QRectF(-10, -10, 24.0, 24.0),
            self.icons,
            QRectF(offset, 0, 24.0, 24.0)
        )


@register_node(OP_NODE_VEC_XYZ)
class VecXYZNode(Node):
    icon = os.path.join(App.getUserAppDataDir(), "Macro", "pyqt-node-editor", "examples",
                        "example_freecad", "icons", "freecad_default_icon.png")
    op_code = OP_NODE_VEC_XYZ
    op_title = "Vector XYZ"

    GraphicsNode_class = VecXYZGraphicsNode
    NodeContent_class = None

    def __init__(self, scene):
        super().__init__(scene, self.__class__.op_title, inputs=[(0, "X"), (0, "Y"), (0, "Z")], outputs=[(1, "Vec")])
        self.value = None
        self.input_multi_edged = True
        self.output_multi_edged = True
        self.initSockets([(0, "X"), (0, "Y"), (0, "Z")], [(1, "Vec")], True)
        self.markDirty()
        #self.eval()

    def initSettings(self):
        super().initSettings()
        self.input_socket_position = LEFT_CENTER
        self.output_socket_position = RIGHT_CENTER

    def eval(self):
        if not self.isDirty() and not self.isInvalid():
            print(" _> returning cached %s value:" % self.__class__.__name__, self.value)
            return self.value
        try:
            val = self.evalImplementation()
            return val
        except ValueError as e:
            self.markInvalid()
            self.grNode.setToolTip(str(e))
            self.markDescendantsDirty()
        except Exception as e:
            self.markInvalid()
            self.grNode.setToolTip(str(e))
            dumpException(e)

    def evalImplementation(self):
        x = self.getInputs(0)
        y = self.getInputs(1)
        z = self.getInputs(2)

        if len(x)==0 or len(y)==0 or len(z)==0:
            self.markInvalid()
            self.markDescendantsDirty()
            self.grNode.setToolTip("Connect all inputs")
            return None

        else:
            x_values = []
            for x_value in x:
                x_values.append(x_value.eval())

            y_values = []
            for y_value in y:
                y_values.append(y_value.eval())

            z_values = []
            for z_value in z:
                z_values.append(z_value.eval())

            val = self.evalOperation(x_values[0], y_values[0], z_values[0])
            self.value = val
            self.markDirty(False)
            self.markInvalid(False)
            self.grNode.setToolTip("")
            self.markDescendantsDirty()
            self.evalChildren()
            return self.value

    def evalOperation(self, x, y, z):
        vector = App.Vector(x, y, z)
        if vector:
            return vector
        else:
            raise ValueError('Wrong input values')

    def onInputChanged(self, socket=None):
        print("%s::__onInputChanged" % self.__class__.__name__)
        self.markDirty()
        self.eval()

    def serialize(self):
        res = super().serialize()
        res['op_code'] = self.__class__.op_code
        return res

    def deserialize(self, data, hashmap={}, restore_id=True):
        res = super().deserialize(data, hashmap, restore_id)
        #print("Deserialized Node '%s'" % self.__class__.__name__, "res:", res)
        return res