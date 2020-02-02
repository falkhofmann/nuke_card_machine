"""Define constant values to map user selection to node types."""

# Import third-party modules
import nuke  # pylint: disable=import-error

GEOMETRY = {'Axis': nuke.nodes.Axis2,
            'Card': nuke.nodes.Card2,
            'Card3D': nuke.nodes.Card3D}
