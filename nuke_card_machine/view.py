"""Interface class to provide ability for cards creation."""

# Import built-in modules
import os

# Import third-party modules
from PySide2 import QtWidgets, QtCore, QtGui

# Import local modules
from nuke_card_machine.constants import GEOMETRY, ENGINES


class Button(QtWidgets.QPushButton):
    """Custom Button to change color when mouse is enter and leave widget."""

    def __init__(self, name, parent=None):
        super(Button, self).__init__(parent)
        self.setMouseTracking(True)
        self.setText(name)
        self.setMinimumWidth(100)
        self.setMaximumWidth(100)
        self.set_style_sheet(self)

    @staticmethod
    def set_style_sheet(widget):

        styles_file = os.path.normpath(os.path.join(os.path.dirname(__file__),
                                                    "stylesheet.css"))

        with open(styles_file, "r") as file_:
            style = file_.read()
            widget.setStyleSheet(style)


class DropDown(QtWidgets.QWidget):
    """Pair of label and dropdown widget."""

    def __init__(self, label, content=None, scale=None):
        super(DropDown, self).__init__()

        layout = QtWidgets.QVBoxLayout()
        layout.setAlignment(QtCore.Qt.AlignTop)

        self.setLayout(layout)

        label = QtWidgets.QLabel('{}: '.format(label))
        layout.addWidget(label)

        if not scale:
            self.pulldown = QtWidgets.QComboBox()
            print content
            for item in content:
                self.pulldown.addItem(QtGui.QIcon(self.get_icon_path(item)), item)
            layout.addWidget(self.pulldown)

        else:
            self.scale_input = QtWidgets.QLineEdit()
            self.scale_input.setMinimumWidth(50)
            self.scale_input.setText('1')
            layout.addWidget(self.scale_input)

    @staticmethod
    def get_icon_path(item):
        return os.path.normpath(os.path.join(os.path.dirname(__file__),
                                             "icons",
                                             "{}.png".format(item)))


class CardMachine(QtWidgets.QWidget):
    """Interface class to interact with user."""

    create = QtCore.Signal(object)

    def __init__(self, node='', layer=''):
        super(CardMachine, self).__init__()

        self.node = node
        self.layer = layer

        self.build_widgets()
        self.build_layouts()
        self.set_up_window_properties()
        self.set_up_signals()

    def build_widgets(self):
        self.channel_drop = DropDown('Position Pass', self.layer)
        self.geometry_drop = DropDown('Geometry', ENGINES)
        self.engine_drop = DropDown('Render Engine', sorted(GEOMETRY.keys()))
        self.scale = DropDown('Uniform Scale', content=None, scale=True)

        self.cancel_button = Button('Cancel')
        self.ok_button = Button('Create Geometry')

    def build_layouts(self):
        main_layout = QtWidgets.QVBoxLayout()
        button_layout = QtWidgets.QHBoxLayout()
        button_layout.setAlignment(QtCore.Qt.AlignRight)
        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.ok_button)

        main_layout.addWidget(self.channel_drop)
        main_layout.addWidget(self.geometry_drop)
        main_layout.addWidget(self.engine_drop)
        main_layout.addWidget(self.scale)
        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)

    def set_up_window_properties(self):
        self.setWindowTitle('nuke_card_machine')
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        self.setFixedSize(300, 300)

    def set_up_signals(self):
        self.cancel_button.clicked.connect(self.close)
        self.ok_button.clicked.connect(self.create_geometry)

    def create_geometry(self):
        """Build Nuke geometry based on user selection."""

        self.create.emit((self.node,
                         self.channel_drop.pulldown.currentText(),
                         self.geometry_drop.pulldown.currentText(),
                         self.engine_drop.pulldown.currentText(),
                         float(self.scale.scale_input.text())))
        self.close()

    def keyPressEvent(self, event):  # pylint: disable=invalid-name
        """Catch user key interactions. Close on escape."""
        if event.key() == QtCore.Qt.Key_Escape:
            self.close()
