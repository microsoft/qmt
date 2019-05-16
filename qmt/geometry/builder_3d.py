"""
The Geo3DBuilder class, which is used to build 3D geometries
"""

from typing import Dict, List, Optional
from qmt.infrastructure import serialize_file
import FreeCAD
from .part_3d import Geo3DPart
from .geo_3d_data import Geo3DData


def build_3d_geometry(
    input_parts: List[Geo3DPart],
    input_file: Optional[str] = None,
    xsec_dict: Dict[str, Dict] = None,
    serialized_input_file: Optional[bytes] = None,
    params: Optional[Dict] = None,
) -> Geo3DData:
    """Build a geometry in 3D.

    Parameters
    ----------
    input_parts : list
        Ordered list of input parts, leftmost items get built first
    input_file : str
        Path to FreeCAD template file. Either this or serialized_input_file
        must be set (but not both).
        (Default value = None)
    xsec_dict : dict
        Dictionary of cross-section specifications. It should be of the
        form {'xsec_name':{'axis':(1,0,0),'distance':0.}}, where the axis parameter is a tuple
        defining the axis that defines the normal of the cross section, and distance is
        the length along the axis used to set the cross section.
        (Default value = None)
    serialized_input_file : bytes
        FreeCAD template file that has been serialized using
        qmt.infrastructure.serialize_file. This is useful for passing a
        file into a docker container or other environment that
        doesn't have access to a shared drive. Either this or
        input_file must be set (but not both).
        (Default value = None)
    params : dict
        Dictionary of parameters to use in FreeCAD.
        (Default value = None)
    Returns
    -------
    Geo3DData instance

    """
    from qmt.geometry.freecad.objectConstruction import build

    if input_file is None and serialized_input_file is None:
        raise ValueError("One of input_file or serialized_input_file must be non-none.")
    elif input_file is not None and serialized_input_file is not None:
        raise ValueError("Both input_file and serialized_input_file were non-none.")
    elif input_file is not None:
        serial_fcdoc = serialize_file(input_file)
    else:
        serial_fcdoc = serialized_input_file
    if params is None:
        params = {}
    if xsec_dict is None:
        xsec_dict = {}
    options_dict = {}
    options_dict["serial_fcdoc"] = serial_fcdoc
    options_dict["input_parts"] = input_parts
    options_dict["params"] = params
    options_dict["xsec_dict"] = xsec_dict

    data = Geo3DData()
    data.serial_fcdoc = serial_fcdoc
    data.get_data("fcdoc")

    try:
        built = build(options_dict)
    except Exception:
        FreeCAD.closeDocument("instance")
        raise
    FreeCAD.closeDocument("instance")
    return built
