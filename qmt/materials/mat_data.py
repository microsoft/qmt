from ..geometry.geo_data_base import GeoData
from qmt.materials import Materials
from qmt.geometry import Geo3DData, Geo2DData
from typing import Dict


class MatPart:
    def __init__(self, material: str):
        """Object containing material information for a part.
        Currently only contains one string. Might contain more things in the future.

        Parameters
        ----------
        material : str
            The material for the part
        """
        self.material = material


class MatData:
    def __init__(
        self, materials_database: Materials, materials_mapping: Dict[str, str] = {}
    ):
        """Class that contains materials information.

        Parameters
        ----------
        materials_database : Materials
            The materials database to use.
        materials_mapping : dict
            Mapping of parts to materials.
            (Default = {})
        """
        self.materials_database = materials_database
        self.parts = {name: MatPart(mat) for name, mat in materials_mapping.values()}

    def add_part(self, part_name: str, part: MatPart, overwrite: bool = False):
        """Add a part to this materials information.

        Parameters
        ----------
        part_name : str
            Name of the part to create
        part : MatPart
            MatPart containing material properties for the part.
        overwrite : bool
            Should we allow this to overwrite? (Default value = False)
        Returns
        -------
        None
        """
        if (part_name in self.parts) and (not overwrite):
            raise ValueError(f"Attempted to overwrite the part {part_name}.")
        else:
            self.parts[part_name] = part

    def remove_part(self, part_name: str, ignore_if_absent: bool = False):
        """Remove a part from this materials information.

        Parameters
        ----------
        part_name : str
            Name of part to remove.
        ignore_if_absent : bool
            Should we ignore an attempted removal if the part name
            is not found? (Default value = False)
        Returns
        -------
        None
        """
        if part_name in self.parts:
            del self.parts[part_name]
        elif not ignore_if_absent:
            raise ValueError(
                f"Attempted to remove the part {part_name}, which doesn't exist."
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
