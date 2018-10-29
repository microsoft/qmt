# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

"""Geometry task classes for 1D, 2D and 3D."""

from shapely.geometry import Polygon, LineString

from qmt.data import Geo2DData, Geo3DData, serialize_file


def build_2d_geometry(parts, edges, lunit='nm', build_order=None):
    """
    Build a geometry in 2D.
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
            raise ValueError("Object of name " + object_name + " was found neither in edges nor "
                                                               "parts.")
    geo_2d.lunit = lunit
    return geo_2d


def build_3d_geometry(pyenv, input_parts, input_file = None,
                      serialized_input_file = None,params=None):
    """
    Build a geometry in 3D.
    :param str pyenv: path or callable name of the Python 2 executable.
    :param list input_parts: ordered list of input parts, leftmost items get built first
    :param str input_file: path to FreeCAD template file. Either this or serialized_input_file
    must be set (but not both).
    :param bytes input_file: FreeCAD template file that has been serialized using
    qmt.data.serialize_file. This is useful for passing a file into a docker container or other
    environment that doesn't have access to a shared drive. Either this or serialized_input_file
    must be set (but not both).
    :param dict params: dictionary of parameters to use in the freeCAD
    :return Geo3DData:
    """
    if input_file is None and serialized_input_file is None:
        raise ValueError("One of input_file or serialized_input_file must be non-none.")
    elif input_file is not None and serialized_input_file is not None:
        raise ValueError("Both input_file and serialized_input_file were non-none.")
    elif input_file is not None:
        serial_fcdoc = serialize_file(input_file)
    else:
        serial_fcdoc = serialized_input_file
    options_dict = {}
    options_dict['serial_fcdoc'] = serial_fcdoc
    options_dict['input_parts'] = input_parts
    options_dict['params'] = params
    # Convert NumPy3 floats to something that Python2 can unpickle
    if 'params' in options_dict:
        options_dict['params'] = {
            k: float(v) for k, v in options_dict['params'].items()
            }
    # Send off the instructions
    from qmt.geometry.freecad_wrapper import fcwrapper
    geo = fcwrapper(pyenv,
                    'build3d',
                    {'current_options': options_dict}
                    )
    return geo
