"""Integrate commands in Nuke Nodes and Nuke menu."""

# import third-party modules
import nuke  # pylint: disable = import-error

# import local modules
from nuke_card_machine import controller


def start_card_machine():
    """Reload and run the actual module."""
    reload(controller)
    controller.start()


def integrate_into_menu():
    """Add commands to Menu items."""

    for menu in [nuke.menu('Nuke'), nuke.menu('Nodes')]:
        fhofmann = menu.findItem("fhofmann")
        fhofmann.addCommand("card machine", start_card_machine)


integrate_into_menu()
