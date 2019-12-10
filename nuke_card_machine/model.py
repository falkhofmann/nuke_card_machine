""""Provide utility functions to measure values and build nodes."""

# import built-in modules
from collections import defaultdict

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
    """Get all Strokes inside RotoPaint curve knob.

    Args:
        curve_layer (list): Available layer on Node.

    Returns:
        List: RotoPaint Strokes.

    """
    strokes = []
    for element in curve_layer:
        if isinstance(element, nuke.rotopaint.Layer):
            get_strokes(element)
        elif isinstance(element, nuke.rotopaint.Stroke):
            strokes.append(element)
    return strokes


def get_stroke_details(rotopaint_node):
    """Get Screen position and frame of strokes.

    Args:
        rotopaint_node (nuke.node): Rotopaint node to extract details from.

    Returns:
        List: Tuples (int, float, float)

    """
    strokes = get_strokes(rotopaint_node.knob('curves').rootLayer)
    ordered_details = defaultdict(list)
    for stroke in strokes:
        attributes = stroke.getAttributes()
        start_frame = int(attributes.getValue(0, 'ltn'))
        xpos = stroke.getTransform().getPivotPointAnimCurve(0).constantValue
        ypos = stroke.getTransform().getPivotPointAnimCurve(1).constantValue
        ordered_details[start_frame].append((xpos, ypos))
    return ordered_details


def build_curve_tool(paint_node, channel):
    """Measure value from sub-channel on given point and layer.

    Args:
        paint_node (nuke.Node): Node to check values on.
        channel (str): Channel to measure values from.

    """
    curve_tool = nuke.nodes.CurveTool(xpos=paint_node.xpos(),
                                      ypos=paint_node.ypos() + 100,
                                      channels=channel)
    curve_tool['operation'].setValue(1)
    curve_tool.setInput(0, paint_node)
    return curve_tool


def sample_values(curve_tool, stroke, frame):
    """Measure values from given point.

    Args:
        frame (int): Frame on which color sampling is going to happen.
        curve_tool (nuke.Node): Node to measure values.
        stroke (tuple): Frame of stroke creation as well as  and y position of
            stroke in screen_space.

    Returns:
        Tuple (float, float, float): X, Y and Z Position.

    """
    xpos, ypos = stroke
    curve_tool['ROI'].setValue([xpos, ypos, xpos+1, ypos+1])
    nuke.execute(curve_tool, frame, frame)
    return curve_tool['intensitydata'].value()


def import_data(roto_paint, layer, node_type, uniform_scale):  # pylint: disable=too-many-locals
    """Build nuke geometry.

    Args:
        roto_paint (nuke.node): Nuke Rotopaint node.
        layer (str): Name of layer holding position information.
        node_type (str): Type of nuke geometry to create.
        uniform_scale: Overall scale to created Nodes.

    """
    frames = get_stroke_details(roto_paint)
    roto_paint['disable'].setValue(True)
    temp_xpos = roto_paint.xpos()

    curve_tool = build_curve_tool(roto_paint, layer)

    for frame in frames:

        for stroke in frames[frame]:

            position = sample_values(curve_tool, stroke, frame)

            temp_xpos += 150
            temp_ypos = roto_paint.ypos() + 100

            geometry = nuke.createNode(node_type)
            geometry.setXYpos(temp_xpos, temp_ypos + 50)
            geometry.setInput(0, None)

            if node_type == 'Card':
                card = geometry
                geometry = nuke.nodes.TransformGeo(xpos=temp_xpos, ypos=temp_ypos + 100)
                geometry.setInput(0, card)

            geometry['translate'].setValue(position[:3])
            geometry['uniform_scale'].setValue(float(uniform_scale))

    nuke.delete(curve_tool)
    roto_paint['disable'].setValue(False)


def check_nodetype():
    """Validate that selected Node is RotoPaint.

    Returns:
        Nuke.node: Selected RotoPaint node if valid.

    """
    node = nuke.selectedNode()
    if node.Class() == 'RotoPaint':
        return node
    else:
        error_message()
        return


def error_message():
    """Pop up error message, showing that no Rotopaint node is selected."""
    nuke.message('No RotoPaint Node selected.')
