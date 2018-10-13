# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

"""Geometry task classes for 1D, 2D and 3D."""

from shapely.geometry import Polygon, LineString

from qmt.data import Geo2DData, Geo3DData, serialised_file
from qmt.tasks import Task

class Geometry2D(Task):
    """Task for handling of 2D geometries with Shapely."""
    def __init__(self, options=None, name='geometry_2d_task'):
        """
        Builds a geometry in 2D.
        :param dict options: The dictionary holding parts and edges. It should be of the form:
        {
        'parts':{'part_name':list of 2d points},
        'edges':{'edge_name':list of 2d points},
        'lunit':length_unit (nm),
        'build_order':[list, of, all, parts]
        }
        , where these lists are turned into Polygon and
        LineString objects, which are instances of shapely.geometry.
        The build_order controls the order in which the objects are parsed, which matters for
        overlapping domains and overlapping boundary conditions. The highest priority items are
        listed first.
        :param str name: The name of this task.
        """
        super(Geometry2D, self).__init__([], options, name)

    @staticmethod
    def _solve_instance(input_result_list, current_options):
        """
        :param list input_result_list: This is an empty list.
        :param dict current_options: The dictionary specification from above.
        :return: geo_2d: A Geo2DData object.
        """
        geo_2d = Geo2DData()
        build_order = list(current_options.get('build_order',
                                               current_options['parts']))
        edges = current_options.get('edges',{})
        # Set up the complete build order:
        for part in current_options['parts']:
            if part not in build_order:
                build_order.append(part)
        for edge in edges:
            if edge not in build_order:
                build_order.append(edge)
        for object_name in build_order:
            if object_name in current_options['parts']:
                geo_2d.add_part(object_name, Polygon(current_options['parts'][object_name]))
            elif object_name in edges:
                geo_2d.add_edge(object_name, LineString(current_options['edges'][object_name]))
            else:
                raise ValueError("Object of name "+object_name+" was found neither in edges nor "
                                                               "parts.")
        geo_2d.lunit = current_options.get('lunit', 'nm')
        return geo_2d


class Geometry3D(Task):
    """Task for handling of 3D geometries with FreeCAD."""
    def __init__(self, options=None, name='geometry_3d_task'):
        """
        Builds a geometry in 3D.

        :param dict options: The dictionary specifying FreeCAD infromation.
        It should be of the form
        {
          'pyenv':       path or callable name of the Python 2 executable,
          'input_file':  path to FreeCAD template file,
          'input_parts': ordered list of input parts, leftmost items get built first
          'params':      dict{ 'param_name': SweepTag }
        }
        :param str name: The name of this task.
        """
        options['serial_fcdoc'] = serialised_file(options['input_file'])
        super(Geometry3D, self).__init__([], options, name)

    @staticmethod
    def _solve_instance(input_result_list, current_options):
        """
        :param list input_result_list: This is an empty list.
        :param dict current_options: The dictionary specifying parts from above.
        :return geo_3d: A Geo3DData object.
        """
        assert 'serial_fcdoc' in current_options  # make sure the fc doc is in options

        # Convert NumPy3 floats to something that Python2 can unpickle
        if 'params' in current_options:
            current_options['params'] = {
                k: float(v) for k, v in current_options['params'].items()
            }

        # Send off the instructions
        from qmt.geometry.freecad_wrapper import fcwrapper
        geo = fcwrapper(current_options['pyenv'],
                        'build3d',
                        {'current_options': current_options},
                        debug=False)

        return geo
