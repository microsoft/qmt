"""
Contains classes used to describe 3d geometry parts
"""

from typing import List, Optional
from qmt.data import write_deserialised
from enum import Enum


class Part3DData:
    """
    Base class for a 3D geometric part.
    :param fc_name: The name of the 2D/3D freeCAD object that this is built from. Note
        that if the label used for the 3D part is the same as the freeCAD label, and that
        label is unique, None may be used here as a shortcut
    :param label: The descriptive name of this new part
    :param virtual: Whether the part is virtual or not
    """

    def __init__(self, label: str, fc_name: Optional[str], virtual: bool = False):

        self.built_fc_name: Optional[str] = None  # This gets set on geometry build
        self.fc_name = label if fc_name is None else fc_name
        self.label = label
        self.serial_stl: Optional[str] = None  # This gets set on geometry build
        self.serial_stp: Optional[str] = None  # This gets set on geometry build
        self.virtual = virtual

    def write_stp(self, file_path=None):
        """Write part geometry to a STEP file.

        Returns the STEP file path.
        """
        if file_path is None:
            file_path = f"{self.label}.stp"
        write_deserialised(self.serial_stp, file_path)
        return file_path

    def write_stl(self, file_path=None):
        """Write part geometry to a STEP file.

        Returns the STEP file path.
        """
        if file_path is None:
            file_path = f"{self.label}.stl"
        write_deserialised(self.serial_stl, file_path)
        return file_path


class ExtrudeData(Part3DData):
    def __init__(
        self,
        label: str,
        fc_name: str,
        thickness: float,
        z0: float = 0.0,
        virtual: bool = False,
    ):
        """
        :param label: The descriptive name of this new part
        :param fc_name: The name of the 2D/3D freeCAD object that this is built from. Note
            that if the label used for the 3D part is the same as the freeCAD label, and that
            label is unique, None may be used here as a shortcut
        :param thickness: The extrusion thickness
        :param z0: The starting z coordinate
        :param virtual: Whether the part is virtual or not
        """
        self.thickness = thickness
        self.z0 = z0
        super().__init__(label, fc_name, virtual=virtual)


class WireData(Part3DData):
    def __init__(
        self,
        label: str,
        fc_name: str,
        thickness: float,
        z0: float = 0.0,
        virtual: bool = False,
    ):
        """
        :param label: The descriptive name of this new part
        :param fc_name: The name of the 2D/3D freeCAD object that this is built from. Note
            that if the label used for the 3D part is the same as the freeCAD label, and that
            label is unique, None may be used here as a shortcut
        :param thickness: The extrusion thickness
        :param z0: The starting z coordinate
        :param virtual: Whether the part is virtual or not
        """
        self.thickness = thickness
        self.z0 = z0
        super().__init__(label, fc_name, virtual=virtual)


class DepoMode(Enum):
    """
    'depo' or 'etch' defines the positive or negative mask for the deposition of a wire
    coating
    """

    depo = 1
    etch = 2


class WireShellData(Part3DData):
    def __init__(
        self,
        label: str,
        fc_name: str,
        thickness: float,
        target_wire: WireData,
        shell_verts: List[int],
        depo_mode: str,
        virtual: bool = False,
    ):
        """
        :param label: The descriptive name of this new part
        :param fc_name: The name of the 2D/3D freeCAD object that this is built from. Note
            that if the label used for the 3D part is the same as the freeCAD label, and that
            label is unique, None may be used here as a shortcut
        :param thickness: The extrusion thickness
        :param target_wire: Target wire for coating
        :param shell_verts: Vertices to use when rendering the coating
        :param depo_mode: 'depo' or 'etch' defines the positive or negative mask
        :param virtual: Whether the part is virtual or not
        """
        self.thickness = thickness
        self.target_wire = target_wire
        self.shell_verts = shell_verts
        try:
            self.depo_mode = DepoMode[depo_mode]
        except KeyError:
            raise ValueError(
                f"{depo_mode} is not a valid depo mode. Options are "
                f"{[d.name for d in DepoMode]}"
            )
        super().__init__(label, fc_name, virtual=virtual)


class SAGData(Part3DData):
    def __init__(
        self,
        label: str,
        fc_name: str,
        thickness: float,
        z_middle: float,
        t_in: float,
        t_out: float,
        z0: float = 0.0,
        virtual: bool = False,
    ):
        """
        :param label: The descriptive name of this new part
        :param fc_name: The name of the 2D/3D freeCAD object that this is built from. Note
            that if the label used for the 3D part is the same as the freeCAD label, and that
            label is unique, None may be used here as a shortcut
        :param thickness: The total SAG thickness
        :param z_middle: The location for the "flare out"
        :param t_in: The lateral distance from the 2D profile to the edge of the top bevel
        :param t_out: The lateral distance from the 2D profile to the furthest "flare out"
            location
        :param z0: The starting z coordinate
        :param virtual: Whether the part is virtual or not
        """
        self.thickness = thickness
        self.z0 = z0
        self.z_middle = z_middle
        self.t_in = t_in
        self.t_out = t_out
        super().__init__(label, fc_name, virtual=virtual)


class LithographyData(Part3DData):
    def __init__(
        self,
        label: str,
        fc_name: str,
        thickness: float,
        layer_num: int,
        z0: float = 0.0,
        litho_base: List[str] = [],
        virtual: bool = False,
    ):
        """
        :param label: The descriptive name of this new part
        :param fc_name: The name of the 2D/3D freeCAD object that this is built from. Note
            that if the label used for the 3D part is the same as the freeCAD label, and that
            label is unique, None may be used here as a shortcut
        :param thickness: The lithography thickness
        :param layer_num: The layer number. Lower numbers go down first, with higher numbers
            deposited last
        :param z0: The starting z coordinate
        :param litho_base: The base partNames to use. For multi-step lithography, the bases
            are just all merged, so there is no need to list this more than once
        :param virtual: Whether the part is virtual or not
        """
        self.thickness = thickness
        self.z0 = z0
        self.layer_num = layer_num
        self.litho_base = litho_base
        super().__init__(label, fc_name, virtual=virtual)
