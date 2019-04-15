from qmt.geometry import Geo3DData
from qmt.materials import Materials


class Mat3DData(Geo3DData):
    def __init__(self):
        super().__init__()
        self.materials_database = Materials()

    def get_material(self, part_name):
        return self.materials_database[self.parts[part_name].material]

    def get_material_mapping(self):
        """
        Get mapping of part names to materials.

        :return:
        """
        return {name: self.get_material(name) for name in self.parts.keys()}
