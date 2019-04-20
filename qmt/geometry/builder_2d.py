from typing import Dict, List, Optional, Union
from .geo_2d_data import Geo2DData
from shapely.geometry import LineString, Polygon


def build_2d_geometry(
    parts: Dict[str, List[float]],
    edges: Dict[str, List[float]],
    lunit: str = "nm",
    build_order: Optional[List[str]] = None,
) -> Geo2DData:
    """Build a geometry in 2D.

    Parameters
    ----------
    parts : dict
        Dictionary for holding the 2D parts, of the form
        {'part_name':list of 2d points}.
    edges : dict
        Dictionary of 2D edges, of the form:
        {'edge_name':list of 2d points}.
    lunit : str
        length_unit (nm).
        (Default value = "nm")
    build_order : list
        None or a list of all parts, determining the build order. Items on
        the left are highest priority and items on the right are lowest.
        If None is given (default), then build order is determined just
        taken to be the order of the parts and edges.
        (Default value = None)
    Returns
    -------
    Geo2DData instance
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
            geo_2d.add_part(object_name, LineString(edges[object_name]))
        else:
            raise ValueError(
                f"Object of name {object_name} was found neither in edges nor parts."
            )
    geo_2d.lunit = lunit
    return geo_2d
