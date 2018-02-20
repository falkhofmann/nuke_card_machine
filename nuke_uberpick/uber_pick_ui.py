import nuke  # pylint: disable=import-error

try:
    # < Nuke 11
    import PySide.QtCore as QtCore
    import PySide.QtGui as QtGuiWidgets
except ImportError:
    # >= Nuke 11
    import PySide2.QtCore as QtCore
    import PySide2.QtWidgets as QtGuiWidgets

import nuke_uberpick.utils as utils

reload(utils)


UBER_PICK = None


class CustomButton(QtGuiWidgets.QPushButton):
    def __init__(self, name, parent=None):
        super(CustomButton, self).__init__(parent)
        self.setMouseTracking(True)
        self.setText(name)
        self.setMinimumWidth(100)
        self.setMaximumWidth(100)
        self.setStyleSheet("background-color:#282828")

    def enterEvent(self, event):
        self.setStyleSheet("background-color:#C26828")

    def leaveEvent(self, event):
        self.setStyleSheet("background-color:#282828")


class DropDown(QtGuiWidgets.QWidget):
    def __init__(self, label, content=None, scale=None):
        super(DropDown, self).__init__()

        layout = QtGuiWidgets.QVBoxLayout()
        layout.setAlignment(QtCore.Qt.AlignTop)

        self.setLayout(layout)

        label = QtGuiWidgets.QLabel('{}: '.format(label))
        layout.addWidget(label)

        if not scale:
            self.pulldown = QtGuiWidgets.QComboBox()
            self.pulldown.addItems(content)
            layout.addWidget(self.pulldown)

        else:
            self.scale_input = QtGuiWidgets.QLineEdit()
            self.scale_input.setMinimumWidth(50)
            self.scale_input.setText('1')
            layout.addWidget(self.scale_input)


class UberPick(QtGuiWidgets.QWidget):
    def __init__(self, node):
        super(UberPick, self).__init__()

        self.node = node

        self.setWindowTitle('nuke_uberpick')
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        self.setFixedSize(400, 300)
        main_layout = QtGuiWidgets.QVBoxLayout()
        layer, node = utils.get_layer()

        self.channel_drop = DropDown('Position Pass', layer)
        self.geometry_drop = DropDown('Geometry', ['Axis', 'Card', 'Card3d'])
        self.engine_drop = DropDown('Render Engine', ['VRay', 'Mantra/Nuke'])
        self.scale = DropDown('Uniform Scale', content=None, scale=True)

        cancel_button = CustomButton('Cancel')
        ok_button = CustomButton('do the magic')

        button_layout = QtGuiWidgets.QHBoxLayout()
        button_layout.setAlignment(QtCore.Qt.AlignRight)
        button_layout.addWidget(cancel_button)
        button_layout.addWidget(ok_button)

        main_layout.addWidget(self.channel_drop)
        main_layout.addWidget(self.geometry_drop)
        main_layout.addWidget(self.engine_drop)
        main_layout.addWidget(self.scale)
        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)

        cancel_button.clicked.connect(self.cancel)
        ok_button.clicked.connect(self.create_geometry)

    def create_geometry(self):
        channel = self.channel_drop.pulldown.currentText()
        geometry = self.geometry_drop.pulldown.currentText()
        renderer = self.engine_drop.pulldown.currentText()
        scale = self.scale.scale_input.text()
        utils.import_data(self.node, channel, geometry, scale, renderer)
        self.cancel()

    def cancel(self):
        self.close()

    # noinspection PyPep8Naming
    def keyPressEvent(self, e):
        if e.key() == QtCore.Qt.Key_Escape:
            self.cancel()


def start():
    rotopaint = utils.check_nodetype()
    if rotopaint:
        global dialog
        dialog = UberPick(rotopaint)
        dialog.show()
