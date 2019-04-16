from ..geometry.geo_data_base import GeoData
from qmt.materials import Materials
from qmt.geometry import Geo3DData, Geo2DData
from typing import Dict


class MatData(GeoData):
    """
    Base class for a geometry that has materials
    """

    def __init__(
        self, materials_database: Materials, materials_mapping: Dict[str, str]
    ):
        self.materials_database = materials_database
        self.materials_mapping = materials_mapping

    def get_material(self, part_name: str):
        return self.materials_database[self.parts[part_name].material]

    def get_material_mapping(self):
        """
        Get mapping of part names to materials.
        """
        return {name: self.get_material(name) for name in self.parts.keys()}

    def from_geo_data(self, geo_data: GeoData):
        """
        Copies fields of geo_data to this class
        """
        self.parts = geo_data.parts
        self.lunit = geo_data.lunit
        self.build_order = geo_data.build_order


class Mat3DData(MatData, Geo3DData):
    """
    A 3D geometry that has materials
    """

    def __init__(
        self,
        materials_database: Materials,
        materials_mapping: Dict[str, str],
        lunit: str = "nm",
    ):
        MatData.__init__(self, materials_database, materials_mapping)
        Geo3DData.__init__(self, lunit)

    def from_geo_data(self, geo_data: Geo3DData):
        MatData.from_geo_data(self, geo_data)
        self.xsecs = geo_data.xsecs
        self.serial_fcdoc = geo_data.serial_fcdoc


class Mat2DData(MatData, Geo2DData):
    """
    A 2D geometry that has materials
    """

    def __init__(
        self,
        materials_database: Materials,
        materials_mapping: Dict[str, str],
        lunit: str = "nm",
    ):
        MatData.__init__(self, materials_database, materials_mapping)
        Geo2DData.__init__(self, lunit)

    def from_geo_data(self, geo_data: Geo2DData):
        MatData.from_geo_data(self, geo_data)
        self.edges = geo_data.edges
