""""Provide utility functions to measure values and build nodes."""

# Import third-party modules
import nuke  # pylint: disable=import-error


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


def sample_values(rotonode, pick, layer):
    """Measure values from given point.

    Args:
        rotonode (nuke.Node): Node to check values on.
        pick (tuple): Frame of stroke creation as well as  and y position of
            stroke in screenspace.
        layer (str): Layer holding hte position data to measure.

    Returns:
        Tuple (float, float, float): X, Y and Z Position.

    """
    frame, xpos, ypos = pick
    coordinates = []
    channels = [sub for sub in rotonode.channels() if layer in sub.split('.')[0]][:3]

    for channel in channels:
        coordinates.append(sample_point(rotonode, channel, xpos, ypos))
    return coordinates


def sample_point(node, channel, xpos, ypos):
    """Measure value from sub-channel on given point and layer.

    Args:
        node (nuke.Node): Node to check values on.
        channel (str): Subchannel like red, green or blue.
        xpos (int): Horizontal screenspace position to measure.
        ypos (int): Vertical screenspace position to measure.

    Returns:
        Float: Measured Position in Sub channel.

    """
    return float(node.sample(channel, xpos, ypos))


def import_data(node, layer, node_type, uniform_scale):  # pylint: disable=too-many-locals
    """Build nuke geometry.

    Args:
        node (nuke.node): Nuke Rotopaint node.
        layer (str): Name of layer holding position information.
        node_type (str): Type of nuke geometry to create.
        uniform_scale: Overall scale to created Nodes.

    """
    coordinates = get_stroke_details(node)
    temp_xpos = node.xpos()

    for pick in coordinates:

        nuke.tprint(pick)
        position = sample_values(node, pick, layer)

        temp_xpos += 150
        temp_ypos = node.ypos() + 100

        geometry = nuke.createNode(node_type)
        geometry.setXYpos(temp_xpos, temp_ypos + 50)
        geometry.setInput(0, None)

        if node_type == 'Card':
            card = geometry
            geometry = nuke.nodes.TransformGeo(xpos=temp_xpos, ypos=temp_ypos + 100)
            geometry.setInput(0, card)

        geometry['translate'].setValue(position)
        geometry['uniform_scale'].setValue(float(uniform_scale))


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
