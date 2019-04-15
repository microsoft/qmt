# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

"""Geometry task classes for 1D, 2D and 3D."""

from shapely.geometry import Polygon, LineString
from qmt.data import Geo2DData, serialize_file
import FreeCAD


def build_2d_geometry(parts, edges, lunit="nm", build_order=None):
    """
    Build a geometry in 2D.

    :param dict parts: Dictionary for holding the 2D parts, of the form
                       {'part_name':list of 2d points}.
    :param dict edges: Dictionary of 2D edges, of the form:
                       {'edge_name':list of 2d points}.
    :param str lunit: length_unit (nm).
    :param list build_order: None or a list of all parts, determining the build order. Items on
                             the left are highest priority and items on the right are lowest.
                             If None is given (default), then build order is determined just
                             taken to be the order of the parts and edges.
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
            raise ValueError(
                "Object of name " + object_name + " was found neither in edges nor "
                "parts."
            )
    geo_2d.lunit = lunit
    return geo_2d
