"""Connect user interface with model."""

# Import local modules
from nuke_card_machine import view
from nuke_card_machine import model


class Controller(object):
    """Connect the user interface with model."""
    def __init__(self, view_):
        self.view = view_
        self.set_up_signals()

    def set_up_signals(self):
        """Connect interface signal with model functions."""
        self.view.create.connect(lambda x: self.create_geometry(x))  # pylint: disable=unnecessary-lambda

    @staticmethod
    def create_geometry(details):
        """Read out data from images.

        Args:
            details (tuple): RotoPaint node, channel to measure, geometry to
                create and scale to set on the geometry.

        """
        model.import_data(*details)


def start():
    """Start up function."""
    rotopaint = model.check_nodetype()
    if rotopaint:
        global VIEW  # pylint: disable=global-statement, global-variable-undefined
        VIEW = view.CardMachine(rotopaint, model.get_layer(rotopaint))
        VIEW.raise_()
        VIEW.show()

        Controller(VIEW)
