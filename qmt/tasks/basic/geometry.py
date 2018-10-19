# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

"""Geometry task classes for 1D, 2D and 3D."""

from shapely.geometry import Polygon, LineString

from qmt.data import Geo2DData, Geo3DData, serialised_file

def geometry_2d(parts,edges,lunit='nm',build_order=None):
    """
    Builds a geometry in 2D.
    :param dict parts: Dictionary for holding the 2D parts, of the form
    {'part_name':list of 2d points}.
    :param dict edges: Dictionary of 2D edges, of the form:
    {'edge_name':list of 2d points}.
    :param str lunit: length_unit (nm).
    :param list build_order: None or a list of all parts, determining the build order. Items on
    the left are highest priority and items on the right are lowest. If None is given (default),
    then build order is determined just taken to be the order of the parts and edges.
    """
    geo_2d = Geo2DData()
    if build_order is None:
        build_order = list(parts)
    # Set up the complete build order:
    for part in parts:
        if part not in build_order:
            build_order.append(part)
    for edge in edges:
        if edge not in build_order:
            build_order.append(edge)
    for object_name in build_order:
        if object_name in parts:
            geo_2d.add_part(object_name, Polygon(parts[object_name]))
        elif object_name in edges:
            geo_2d.add_edge(object_name, LineString(edges[object_name]))
        else:
            raise ValueError("Object of name "+object_name+" was found neither in edges nor "
                                                           "parts.")
    geo_2d.lunit = lunit
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
