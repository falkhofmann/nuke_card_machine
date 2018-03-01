"""Interface class to provide ability for cards creation."""


try:
    # < Nuke 11
    import PySide.QtCore as QtCore
    import PySide.QtGui as QtGuiWidgets
except ImportError:
    # >= Nuke 11
    import PySide2.QtCore as QtCore
    import PySide2.QtWidgets as QtGuiWidgets

from nuke_card_machine.constants import AXIS, CARD, CARD3D, RAW, MAX, MAYA
import nuke_card_machine.utils as utils

reload(utils)


class Button(QtGuiWidgets.QPushButton):
    """Custom Button to change color when mouse is enter and leave widget."""

    def __init__(self, name, parent=None):
        super(Button, self).__init__(parent)
        self.setMouseTracking(True)
        self.setText(name)
        self.setMinimumWidth(100)
        self.setMaximumWidth(100)
        self.setStyleSheet("background-color:#282828")

    def enterEvent(self, event):  # pylint: disable=invalid-name,unused-argument
        """Change stylesheet to ornage style when mouse enters widget.

        Args:
            event: unused but necessary.

        """
        self.setStyleSheet("background-color:#C26828")

    def leaveEvent(self, event):  # pylint: disable=invalid-name,unused-argument
        """Change stylesheet back to basic when mouse leaves widget.

        Args:
            event: unused but necessary.

        """
        self.setStyleSheet("background-color:#282828")


class DropDown(QtGuiWidgets.QWidget):
    """Pair of label and dropdown widget."""

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


class CardMachine(QtGuiWidgets.QWidget):
    """Interface class to interact with user."""

    def __init__(self, node):
        super(CardMachine, self).__init__()

        self.node = node

        self.setWindowTitle('nuke_card_machine')
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        self.setFixedSize(400, 300)
        main_layout = QtGuiWidgets.QVBoxLayout()
        layer, node = utils.get_layer()

        self.channel_drop = DropDown('Position Pass', layer)
        self.geometry_drop = DropDown('Geometry', [AXIS, CARD, CARD3D])
        self.engine_drop = DropDown('Render Engine', [RAW, MAX, MAYA])
        self.scale = DropDown('Uniform Scale', content=None, scale=True)

        cancel_button = Button('Cancel')
        ok_button = Button('Create Geometry')

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
        """Build Nuke geometry based on user selection."""
        utils.import_data(self.node,
                          self.channel_drop.pulldown.currentText(),
                          self.geometry_drop.pulldown.currentText(),
                          self.engine_drop.pulldown.currentText(),
                          self.scale.scale_input.text())
        self.cancel()

    def cancel(self):
        """Close widget."""
        self.close()

    def keyPressEvent(self, event):  # pylint: disable=invalid-name
        """Catch user key interactions. Close on escape."""
        if event.key() == QtCore.Qt.Key_Escape:
            self.cancel()


def start():
    """Start up function to show widget."""
    rotopaint = utils.check_nodetype()
    if rotopaint:
        card_machine = None
        global card_machine  # pylint: disable=global-statement
        card_machine = CardMachine(rotopaint)
        card_machine.show()
