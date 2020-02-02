"""Integrate commands in Nuke menu."""

# import third-party modules
import nuke  # pylint: disable = import-error

# import local modules
from nuke_card_machine import controller

nuke.menu('Nuke').findItem("fhofmann").addCommand("nuke card machine", controller.start)
