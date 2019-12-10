
# Import local modules
from nuke_card_machine import view
from nuke_card_machine import model

reload(view)
reload(model)


class Controller:

    def __init__(self, view):
        self.view = view
        self.set_up_signals()

    def set_up_signals(self):
        self.view.create.connect(lambda x: self.create_geometry(x))

    @staticmethod
    def create_geometry(details):
        model.import_data(*details)


def start():
    """Start up function."""
    """
    rotopaint = model.check_nodetype()
    if rotopaint:

        global VIEW  # pylint: disable=global-statement
        VIEW = view.CardMachine(rotopaint, model.get_layer(rotopaint))
        VIEW.raise_()
        VIEW.show()

        Controller(VIEW)
    """

