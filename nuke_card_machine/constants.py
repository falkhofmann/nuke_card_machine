# Import third-party modules
import nuke

ENGINES = ['Houdini', 'Nuke', 'Max', 'Maya']

GEOMETRY = {'Axis': nuke.nodes.Axis2,
            'Card': nuke.nodes.Card,
            'Card3D': nuke.nodes.Card3D}

CHANNEL_MAP = {'Houdini': {'red': 'x', 'green': 'x', 'blue': 'z'},
               'Nuke': {'red': 'red', 'green': 'green', 'blue': 'z'},
               'Max': {'red': 'red', 'green': 'green', 'blue': 'z'},
               'Maya': {'red': 'red', 'green': 'green', 'blue': 'z'}
               }
