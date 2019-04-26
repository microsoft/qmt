from ..geometry.geo_data_base import GeoData
from qmt.materials import Materials
from qmt.geometry import Geo3DData, Geo2DData
from typing import Dict
from qmt.infrastructure import WithParts
from dataclasses import dataclass


@dataclass
class MatPart:
    """Object containing material information for a part.
    Currently only contains one string. Might contain more things in the future.

    Parameters
    ----------
    material : str
        The material for the part
    """

    material: str


class MatData(WithParts):
    def __init__(
        self, materials_database: Materials, materials_mapping: Dict[str, str] = None
    ):
        """Class that contains materials information.

        Parameters
        ----------
        materials_database : Materials
            The materials database to use.
        materials_mapping : dict
            Mapping of parts to materials.
            (Default = None)
        """
        self.materials_database = materials_database
        if materials_mapping is not None:
            super().__init__(
                {name: MatPart(mat) for name, mat in materials_mapping.items()}
            )

    def get_material(self, part_name: str):
        """Get the material for a particular part.
        
        Parameters
        ----------
        part_name : str
            Name of the part to get material for.
        Returns
        -------
        Material for that part.
        """
        return self.materials_database[self.parts[part_name].material]

    def get_material_mapping(self):
        """Get mapping of part names to materials.
        Returns
        -------
        Dictionary parts to materials.
        """
        return {name: self.get_material(name) for name in self.parts.keys()}
