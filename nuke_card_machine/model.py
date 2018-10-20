""""Provide utility functions to measure values and build nodes."""

# Import third-party modules
import nuke  # pylint: disable=import-error

# Import local modules
from nuke_card_machine.constants import ENGINES, CHANNEL_MAP


def get_layer(node):
    """Get available layer at selected node.

    Returns:
        List: Sorted layer at selectedNode.
        Node: Currently selected Node.

    """
    layer = list(set([c.split('.')[0] for c in node.channels()]))
    return sorted(layer)


def get_strokes(curve_layer):
    """Get all Strokes inside Rotopaint curve knob.

    Args:
        curve_layer (list): Available layer on Node.

    Returns:
        List: Rotopaint Strokes.

    """
    strokes = []
    for element in curve_layer:
        if isinstance(element, nuke.rotopaint.Layer):
            get_strokes(element)
        elif isinstance(element, nuke.rotopaint.Stroke):
            strokes.append(element)
    return strokes


def get_stroke_details(rotonode):
    """Get Screen position and frame of strokes.

    Args:
        rotonode (nuke.node): Rotopaint node to extract details from.

    Returns:
        List: Tuples (int, float, float)

    """
    strokes = get_strokes(rotonode.knob('curves').rootLayer)
    details = []
    for stroke in strokes:
        attributes = stroke.getAttributes()
        start_frame = int(attributes.getValue(0, 'ltn'))
        xpos = stroke.getTransform().getPivotPointAnimCurve(0).constantValue
        ypos = stroke.getTransform().getPivotPointAnimCurve(1).constantValue
        details.append((start_frame, xpos, ypos))
    return details


def sample_values(rotonode, pick, layer, render_engine):
    """Measure values from given point.

    Args:
        rotonode (nuke.Node): Node to check values on.
        pick (tuple): Frame of stroke creation as well as  and y position of
            stroke in screenspace.
        layer (str): Layer holding hte position data to measure.
        render_engine (str): Engine from which data has been rendered.

    Returns:
        Tuple (float, float, float): X, Y and Z Position.

    """
    frame, xpos, ypos = pick
    coordinates = []
    for channel in ('red', 'green', 'blue'):
        coordinates.append(
            sample_point(rotonode, layer, channel, render_engine, xpos, ypos))
    return coordinates


def sample_point(node, layer, channel, render_engine, xpos, ypos):
    """Measure value from sub-channel on given point and layer.

    Args:
        node (nuke.Node): Node to check values on.
        layer (str): Layer holding hte position data to measure. :
        channel (str): Subchannel like red, green or blue.
        render_engine (str): Engine from which data has been rendered.
        xpos (int): Horizontal screenspace position to measure.
        ypos (int): Vertical screenspace position to measure.

    Returns:
        Float: Measured Position in Sub channel.

    """
    return float(node.sample(r'{}.{}'.format(layer, CHANNEL_MAP[render_engine][channel]), xpos, ypos))


def import_data(node, layer, render_engine, node_type, uniform_scale):  # pylint: disable=too-many-locals
    """Build nuke geometry.

    Args:
        node (nuke.node): Nuke Rotopaint node.
        layer (str): Name of layer holding position information.
        render_engine (str): From which engine the data were created.
        node_type (str): Type of nuke geometry to create.
        uniform_scale: Overall scale to created Nodes.

    """
    coordinates = get_stroke_details(node)
    temp_xpos = node.xpos()

    values = []
    for pick in coordinates:

        xpos, ypos, zpos = sample_values(node, pick, layer, render_engine)

        if render_engine in ENGINES[0:1]:
            values = [xpos, ypos, zpos]
        elif render_engine == ENGINES[2]:
            values = [xpos, zpos, -ypos]
        elif render_engine == ENGINES[3]:
            values = [xpos, ypos, -zpos]

        temp_xpos += 150
        temp_ypos = node.ypos() + 100

        geoemtry = nuke.createNode(node_type)
        geoemtry.setXYpos(temp_xpos, temp_ypos + 50)
        geoemtry.setInput(0, None)

        if node_type == 'Card':
            card = geoemtry
            geoemtry = nuke.nodes.TransformGeo(xpos=temp_xpos, ypos=temp_ypos + 100)
            geoemtry.setInput(0, card)

        geoemtry['translate'].setValue(values)
        geoemtry['uniform_scale'].setValue(float(uniform_scale))


def check_nodetype():
    """Validate that selected Node is Rotopaint.

    Returns:
        Nuke.node: Selected Rotopaint node if valid.

    """
    node = nuke.selectedNode()
    if node.Class() == 'RotoPaint':
        return node
    else:
        error_message()


def error_message():
    """Pop up error message, showing that no Rotopaint node is selected."""
    nuke.message('No RotoPaint Node selected.')
