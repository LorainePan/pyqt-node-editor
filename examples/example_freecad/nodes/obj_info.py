import os
from qtpy.QtCore import Qt, QRectF
from qtpy.QtGui import QImage
from qtpy.QtWidgets import QLineEdit, QLabel
from nodeeditor.node_node import Node
from nodeeditor.node_socket import LEFT_CENTER, RIGHT_CENTER
from nodeeditor.node_graphics_node import QDMGraphicsNode
from nodeeditor.node_content_widget import QDMNodeContentWidget
from examples.example_freecad.calc_conf import register_node, OP_NODE_OBJ_INFO
from nodeeditor.utils import dumpException
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
        self.edit = QLineEdit("Obj label", self)
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


@register_node(OP_NODE_OBJ_INFO)
class ObjInfoNode(Node):
    icon = os.path.join(App.getUserAppDataDir(), "Macro", "pyqt-node-editor", "examples",
                        "example_freecad", "icons", "in.png")
    op_code = OP_NODE_OBJ_INFO
    op_title = "Object Info"
    content_label_objname = "calc_node_input"

    GraphicsNode_class = ObjInfoGraphicsNode
    NodeContent_class = TextInputContent

    def __init__(self, scene):
        super().__init__(scene, self.__class__.op_title, inputs=[], outputs=[(0, "Out")])
        self.value = None
        self.input_multi_edged = False
        self.output_multi_edged = True
        self.initSockets([], [(0, "")], True)

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

    def eval(self):
        if not self.isDirty() and not self.isInvalid():
            print(" _> returning cached %s value:" % self.__class__.__name__, self.value)
            return self.value
        try:
            val = self.evalImplementation()
            print(val)
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
        text = str(self.content.edit.text())
        self.value = self.evalOperation(text)
        self.markDirty(False)
        self.markInvalid(False)
        self.markDescendantsInvalid(False)
        self.markDescendantsDirty()
        self.grNode.setToolTip("Enter object label")
        self.evalChildren()
        return self.value

    def evalOperation(self, obj_label):
        obj_list = App.ActiveDocument.getObjectsByLabel(obj_label)
        if len(obj_list) == 1:
            return obj_list[0].Name
        else:
            raise ValueError('Unknown object label')

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