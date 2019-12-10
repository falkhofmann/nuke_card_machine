"""Define constant values to map user selection to node types."""

# Import third-party modules
import nuke

GEOMETRY = {'Axis': nuke.nodes.Axis2,
            'Card': nuke.nodes.Card,
            'Card3D': nuke.nodes.Card3D}
