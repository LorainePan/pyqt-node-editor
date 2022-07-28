import os
from qtpy.QtWidgets import QLineEdit
from qtpy.QtCore import Qt
from examples.example_freecad.calc_conf import register_node, OP_NODE_INPUT, OP_NODE_TXT_INPUT
from examples.example_freecad.calc_node_base import CalcNode, CalcGraphicsNode
from nodeeditor.node_content_widget import QDMNodeContentWidget
from nodeeditor.utils import dumpException

from qtpy.QtGui import QImage
from qtpy.QtCore import QRectF
from qtpy.QtWidgets import QLabel

from nodeeditor.node_node import Node
from nodeeditor.node_graphics_node import QDMGraphicsNode
from nodeeditor.node_socket import LEFT_CENTER, RIGHT_CENTER

import FreeCAD as App


class ObjInfoGraphicsNode(QDMGraphicsNode):
    def initSizes(self):
        super().initSizes()
        self.width = 160
        self.height = 74
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


class TextInputContent(QDMNodeContentWidget):
    def initUI(self):
        self.edit = QLineEdit("Text", self)
        self.edit.setAlignment(Qt.AlignRight)
        self.edit.setObjectName(self.node.content_label_objname)

    def serialize(self):
        res = super().serialize()
        res['text'] = self.edit.text()
        return res

    def deserialize(self, data, hashmap={}):
        res = super().deserialize(data, hashmap)
        try:
            value = data['text']
            self.edit.setText(value)
            return True & res
        except Exception as e:
            dumpException(e)
        return res


@register_node(OP_NODE_TXT_INPUT)
class ObjInfoNode(Node):
    icon = os.path.join(App.getUserAppDataDir(), "Macro", "pyqt-node-editor", "examples",
                        "example_freecad", "icons", "in.png")
    op_code = OP_NODE_TXT_INPUT
    op_title = "Text"
    content_label_objname = "calc_node_input"

    GraphicsNode_class = CalcGraphicsNode
    NodeContent_class = CalcContent

    def __init__(self, scene):
        super().__init__(scene, scene, self.__class__.op_title, inputs=[], outputs=[0])
        self.value = None
        self.input_multi_edged = True
        self.initSockets(inputs, outputs, True)

        # it's really important to mark all nodes Dirty by default
        self.markDirty()

        self.eval()

    def initInnerClasses(self):
        self.content = TextInputContent(self)
        self.grNode = ObjInfoGraphicsNode(self)
        self.content.edit.textChanged.connect(self.onInputChanged)

    def initSettings(self):
        super().initSettings()
        self.input_socket_position = LEFT_CENTER
        self.output_socket_position = RIGHT_CENTER

    def evalImplementation(self):
        u_value = self.content.edit.text()
        s_value = str(u_value)
        self.value = s_value
        self.markDirty(False)
        self.markInvalid(False)

        self.markDescendantsInvalid(False)
        self.markDescendantsDirty()

        self.grNode.setToolTip("Text input")

        self.evalChildren()

        return self.value




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

    def onInputChanged(self, socket=None):
        #print("%s::__onInputChanged" % self.__class__.__name__)
        self.markDirty()
        self.eval()

    def serialize(self):
        res = super().serialize()
        res['op_code'] = self.__class__.op_code
        return res

    def deserialize(self, data, hashmap={}, restore_id=True):
        res = super().deserialize(data, hashmap, restore_id)
        #print("Deserialized CalcNode '%s'" % self.__class__.__name__, "res:", res)
        return res


class FCOneOneNode(Node):

    def evalOperation(self, input1, input2):
        return 123

    def evalImplementation(self):
        input = self.getInputs(0)

        if input is None:
            self.markInvalid()
            self.markDescendantsDirty()
            self.grNode.setToolTip("Connect all inputs")
            return None

        else:
            val = []
            for i in input:
                val.append(self.evalOperation(i.eval()))
            self.value = val
            self.markDirty(False)
            self.markInvalid(False)
            self.grNode.setToolTip("")

            self.markDescendantsDirty()
            self.evalChildren()
            print(val)
            return val




