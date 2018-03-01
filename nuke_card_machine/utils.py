import nuke
from PySide import QtGui

def get_user_input(node):
    p = nuke.Panel("specify Psoition Pass")
    layer = ''.join(get_layer())
    output = ''.join(['Axis2', 'Card'])
    p.addEnumerationPulldown("Layer:", layer)
    p.addEnumerationPulldown("Create:", output)
    p.addButton("Cancel")
    p.addButton("Ok")
    result = p.show()
    if not result:
        return
    user_layer = p.value("Layer:")
    user_type = p.value("Create:")
    get_screenspace_coordionates(node, user_layer, user_type)


def get_layer():
    node = nuke.selectedNode()
    channels = node.channels()
    layer = list(set([c.split('.')[0] for c in channels]))
    return sorted(layer), node


def get_strokes(layer):
    strokes = []
    for element in layer:
        if isinstance(element, nuke.rotopaint.Layer):
            get_strokes(element)
        elif isinstance(element, nuke.rotopaint.Stroke) or isinstance(element, nuke.rotopaint.Shape):
            strokes.append(element)
    return strokes


def get_stroke_details(rotonode):
    strokes = get_strokes(rotonode.knob('curves').rootLayer)
    details = []
    for stroke in strokes:
        attributes = stroke.getAttributes()
        start_frame = int(attributes.getValue(0, 'ltn'))
        xpos = stroke.getTransform().getPivotPointAnimCurve(0).constantValue
        ypos = stroke.getTransform().getPivotPointAnimCurve(1).constantValue
        details.append((start_frame, xpos, ypos))
    return details


def sample_values_via_curvetool(curve, screen_coordinate, layer):
    curve['operation'].setValue(1)
    curve['channels'].setValue(layer)
    frame, x, y = screen_coordinate
    curve['ROI'].setValue([x, y, x + 1, y + 1])
    nuke.execute(curve, frame, frame)
    return curve['intensitydata'].valueAt(frame)


def import_data(node, layer, node_type, uniform_scale, render_engine):
    node['disable'].setValue(True)
    coordinates = get_stroke_details(node)
    temp_xpos = node.xpos()
    curve = nuke.nodes.CurveTool(inputs=[node])

    node_types = {'Axis': nuke.nodes.Axis2,
                  'Card': nuke.nodes.Card,
                  'Card3D': nuke.nodes.Card3D}

    for pick in coordinates:
        x, y, z, _ = sample_values_via_curvetool(curve, pick, layer)
        if render_engine == 'RAW':
            values = [x, y, z]
        elif render_engine == 'Max/Vray':
            values = [x, z, -y]
        elif render_engine == 'Maya/Vray':
            values = [x, y, -z]

        temp_xpos += 150
        temp_ypos = node.ypos() + 100

        new = node_types[node_type]()
        new.setXYpos(temp_xpos, temp_ypos + 50)

        if node_type == 'Card':
            card = new
            new = nuke.nodes.TransformGeo(xpos=temp_xpos, ypos=temp_ypos + 100)
            new.setInput(0, card)

        new['translate'].setValue(values)
        new['uniform_scale'].setValue(float(uniform_scale))

    nuke.delete(curve)
    node['disable'].setValue(False)


def check_nodetype():
    node = nuke.selectedNode()
    if node.Class() == 'RotoPaint':
        return node
    else:
        error_message()


def error_message():
    nuke.message('No RotoPaint Node selected.')
