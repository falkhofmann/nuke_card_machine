import string
import nuke


def get_user_input(node):
    p = nuke.Panel("specify Psoition Pass")
    layer = string.join(get_layer())
    output = string.join(['Axis2', 'Card'])
    p.addEnumerationPulldown("Layer:", layer)
    p.addEnumerationPulldown("Create:", output)
    p.addButton("Cancel")
    p.addButton("Ok")
    result = p.show()
    if result:
        user_layer = p.value("Layer:")
        user_type = p.value("Create:")
        get_screenspace_coordionates(node, user_layer, user_type)


def get_layer():
    node = nuke.selectedNode()
    channels = node.channels()
    layer = list(set([c.split('.')[0].lower() for c in channels]))
    return sorted(layer), node


def get_screenspace_coordionates(rotonode, layer, renderer):

    knob = rotonode.knob('curves')
    root = knob.rootLayer
    coordinates = []

    length = len(root)

    if length >= 1:
        for lay in range(length):
            xpos = root[lay].getTransform().getPivotPointAnimCurve(0).constantValue
            ypos = root[lay].getTransform().getPivotPointAnimCurve(1).constantValue
            coordinates.append((xpos, ypos))
    return coordinates

def sample_values_on_coordinate(rotonode, screen_coordinate,):

    colors =[]
    for axis in ['red', 'green', 'blue']:
        colors.append(rotonode.sample(r'rgb.{}'.format(axis), screen_coordinate[0], screen_coordinate[1]))

    return colors


def import_data(node, layer, node_type, uniform_scale, render_engine):
    coordinates = get_screenspace_coordionates(node, layer)


    temp_xpos = node.xpos()

    for pick in coordinates:
        values = sample_values_on_coordinate(node, pick)

        if render_engine == 'Mantra/Nuke':
            values = [x, y, z]
        elif render_engine == 'VRay':
            values = [values[0], values[2], -values[1]]

        temp_xpos += 150
        temp_ypos = node.ypos() + 100

        if node_type == 'Axis':
            new = nuke.nodes.Axis2(xpos=temp_xpos, ypos=temp_ypos + 50)

        elif node_type == 'Card':
            card = nuke.nodes.Card(xpos=temp_xpos, ypos=temp_ypos + 50)
            new = nuke.nodes.TransformGeo(xpos=temp_xpos, ypos=temp_ypos + 100)
            new.setInput(0, card)

        new['translate'].setValue([values])
        new['uniform_scale'].setValue(float(uniform_scale))


def check_nodetype():
    node = nuke.selectedNode()
    if node.Class() == 'RotoPaint':
        return node
    else:
        error_message()


def error_message():
    nuke.message('No RotoPaint Node selected.')
