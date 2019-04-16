from qmt.geometry import Geo3DData, Geo2DData
from qmt.materials import Materials
from typing import Dict, Union
from .mat_part import Mat2DData, Mat3DData
import warnings


def build_materials(
    materials: Materials,
    geo_data: Union[Geo2DData, Geo3DData],
    materials_mapping: Dict[str, str],
) -> Union[Mat2DData, Mat3DData]:
    """
    :param materials: A Materials class, representing a materails library. If you want
        to override values, use make_materials
    :param geo_data: A 2D or 3D geometry class
    :param materials_mapping: A mapping of parts to materials
    """

    # We keep a copy of materials_mapping around, but also set the material property
    # on all the parts
    for name, part in geo_data.parts.values():
        try:
            part.material = materials_mapping[name]
        except KeyError:
            raise ValueError(
                f"materials_mapping does not contain material for part {name}"
            )
    extra_materials = set(materials_mapping.keys()) - set(geo_data.parts.keys())
    if extra_materials:
        warnings.warn(
            f"{extra_materials} are provided in materials_mapping but not found in "
            "geometry parts"
        )

    if isinstance(geo_data, Geo2DData):
        mat_data = Mat2DData(materials, materials_mapping)
    elif isinstance(geo_data, Geo3DData):
        mat_data = Mat3DData(materials, materials_mapping)
    else:
        raise ValueError(f"geo_data must be either Geo2DData or Geo3DData")
    mat_data.from_geo_data(geo_data)
    return mat_data


def make_materials_library(material_properties: Dict[str, Dict]) -> Materials:
    """
    Make a Materials class instance with physical constants overridden by an input dictionary.
    :param dict material_properties: Override specific material properties by specifying
    {'material':{'material_attribute':override_value}
    :return Materials mat_lib: The materials library
    """
    mat_lib = Materials()
    if material_properties:
        for material in material_properties:
            mat_obj = mat_lib[material]
            for attribute in material_properties[material]:
                mat_obj[attribute] = material_properties[material][attribute]
            mat_lib[material] = mat_obj
    return mat_lib
