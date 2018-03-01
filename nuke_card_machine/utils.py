""""provides utility functoins to measuring values and build nodes."""

import nuke  # pylint: disable=import-error

from nuke_card_machine.constants import AXIS, CARD, CARD3D, RAW, MAX, MAYA


def get_layer():
    """Get available layer at selected node.

    Returns:
        List: Sorted layer at selectedNode.
        Node: Currently selected Node.

    """
    node = nuke.selectedNode()
    channels = node.channels()
    layer = list(set([c.split('.')[0] for c in channels]))
    return sorted(layer), node


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
    """Get Screenpoistion and frame of strokes.

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


def sample_values_via_curvetool(curve, screen_coordinate):
    """Measure values on specific position in screenspace.

    Args:
        curve (nuke.node): CurveTool.
        screen_coordinate (list): X and Y position to measure.
        layer (str): Layer to measure colors from.

    Returns:
        list: RGBA values.

    """
    frame, xpos, ypos = screen_coordinate
    curve['ROI'].setValue([xpos, ypos, xpos + 1, ypos + 1])
    curve['label'].setValue(str(frame))
    nuke.execute(curve, frame, frame)
    return curve['intensitydata'].valueAt(frame)


def import_data(node, layer, node_type, render_engine, uniform_scale):  # pylint: disable=too-many-locals
    """Build nuke geometry.

    Args:
        node (nuke.node): Nuke Rotopaint node.
        layer (list): Available layer on node.
        node_type (str): Type of nuke geometry to create.
        uniform_scale: Overall scale to created Nodes.
        render_engine (str): From which engine the data were created.

    """
    node['disable'].setValue(True)
    coordinates = get_stroke_details(node)
    temp_xpos = node.xpos()

    node_types = {AXIS: nuke.nodes.Axis2,
                  CARD: nuke.nodes.Card,
                  CARD3D: nuke.nodes.Card3D}

    curve = nuke.nodes.CurveTool(inputs=[node])
    curve['operation'].setValue(1)
    curve['channels'].setValue(layer)

    values = []
    for pick in coordinates:
        xpos, ypos, zpos, _ = sample_values_via_curvetool(curve, pick)


        if render_engine == RAW:
            values = [xpos, ypos, zpos]
        elif render_engine == MAX:
            values = [xpos, zpos, -ypos]
        elif render_engine == MAYA:
            values = [xpos, ypos, -zpos]

        temp_xpos += 150
        temp_ypos = node.ypos() + 100

        new = nuke.createNode(node_type)
        new.setXYpos(temp_xpos, temp_ypos + 50)
        new.setInput(0, None)

        if node_type == CARD:
            card = new
            new = nuke.nodes.TransformGeo(xpos=temp_xpos, ypos=temp_ypos + 100)
            new.setInput(0, card)

        new['translate'].setValue(values)
        new['uniform_scale'].setValue(float(uniform_scale))

    nuke.delete(curve)
    node['disable'].setValue(False)


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
    """Pop up error message, shwoing that no Rotopaint node was selected."""
    nuke.message('No RotoPaint Node selected.')
