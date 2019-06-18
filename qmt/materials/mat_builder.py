from qmt.geometry import Geo3DData, Geo2DData
from qmt.materials import Materials
from typing import Dict, Optional, Union
from .mat_data import MatData
import warnings
from shapely.geometry import LineString


def build_materials(
    geo_data: Union[Geo2DData, Geo3DData],
    materials_mapping: Dict[str, str],
    materials: Optional[Materials] = None,
) -> MatData:
    """Build a MatData object.

    Parameters
    ----------
    geo_data : Union[Geo2DData, Geo3DData]
        A 2D or 3D geometry class.
    materials_mapping : dict
        A mapping of parts to materials.
    materials : Materials
        A Materials class, representing a materials library. If you want to override
        properties, use make_materials.
    Returns
    -------
    MatData
       Built object with materials information.
    Raises
    ------
    ValueError
        If materials_mapping does not contain a key for a part in geo_data.
    """
    if materials is None:
        materials = Materials()

    # We keep a copy of materials_mapping around, but also set the material property
    # on all the parts
    new_mapping = {}
    for name, part in geo_data.parts.items():
        if ":" in name:
            old_name, _ = name.split(":")
            new_mapping[name] = materials_mapping[old_name]
            continue

        if (
            name not in materials_mapping
            and not part.virtual
            and not isinstance(part, LineString)
        ):
            raise ValueError(
                f"materials_mapping does not contain material for part {name}"
            )
        mat = materials_mapping.get(name)
        if mat is not None:
            new_mapping[name] = mat
    extra_materials = set(new_mapping.keys()) - set(geo_data.parts.keys())
    if extra_materials:
        warnings.warn(
            f"{extra_materials} are provided in materials_mapping but not found in "
            "geometry parts"
        )
    return MatData(materials, new_mapping)


def make_materials_library(material_properties: Dict[str, Dict]) -> Materials:
    """Make a Materials class instance with physical constants overridden by an input dictionary.

    Parameters
    ----------
    material_properties: dict
        Override specific material properties by specifying
        {'material':{'material_attribute':override_value}.
    Returns
    -------
    The materials library with overriden properties.
    """
    mat_lib = Materials()
    if material_properties:
        for material in material_properties:
            mat_obj = mat_lib[material]
            for attribute in material_properties[material]:
                mat_obj[attribute] = material_properties[material][attribute]
            mat_lib[material] = mat_obj
    return mat_lib
