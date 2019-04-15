"""
Contains classes used to describe 3d geometry parts
"""

from dataclasses import dataclass, field
from typing import List, Optional
from qmt.data import write_deserialised
from enum import Enum


@dataclass
class Part3DData:
    """
    Base class for a 3D geometric part.
    :param fc_name: The name of the 2D/3D freeCAD object that this is built from. Note
        that if the label used for the 3D part is the same as the freeCAD label, and that
        label is unique, None may be used here as a shortcut
    :param label: The descriptive name of this new part
    :param virtual: Whether the part is virtual or not
    """

    built_fc_name: Optional[str] = field(init=False)  # This gets set on geometry build
    fc_name: str
    label: str
    serial_stp: Optional[str] = field(init=False)  # This gets set on geometry build
    virtual: bool

    def write_stp(self, file_path=None):
        """Write part geometry to a STEP file.

        Returns the STEP file path.
        """
        if file_path is None:
            file_path = f"{self.label}.stp"
        write_deserialised(self.serial_stp, file_path)
        return file_path


@dataclass
class ExtrudeData(Part3DData):
    """
    :param thickness: The extrusion thickness
    :param z0: The starting z coordinate
    """

    thickness: float
    z0: float


@dataclass
class WireData(Part3DData):
    """
    :param thickness: The total wire thickness
    :param z0: The starting z coordinate
    """

    thickness: float
    z0: float


class DepoMode(Enum):
    """
    'depo' or 'etch' defines the positive or negative mask for the deposition of a wire
    coating
    """

    depo = 1
    etch = 2


@dataclass
class WireShellData(Part3DData):
    """
    :param thickness: The wire shell thickness
    :param target_wire: Target wire for coating
    :param shell_verts: Vertices to use when rendering the coating
    :param depo_mode: 'depo' or 'etch' defines the positive or negative mask
    """

    thickness: float
    target_wire: WireData
    shell_verts: List[int]
    depo_mode: DepoMode


@dataclass
class SAGData(Part3DData):
    """
    :param thickness: The total SAG thickness
    :param z0: The starting z coordinate
    :param z_middle: The location for the "flare out"
    :param t_in: The lateral distance from the 2D profile to the edge of the top bevel
    :param t_out: The lateral distance from the 2D profile to the furthest "flare out"
        location
    """

    thickness: float
    z0: float
    z_middle: float
    t_in: float
    t_out: float


@dataclass
class LithographyData(Part3DData):
    """
    :param thickness: The lithography thickness
    :param z0: The starting z coordinate
    :param layer_num: The layer number. Lower numbers go down first, with higher numbers
        deposited last
    :param litho_base: The base partNames to use. For multi-step lithography, the bases
        are just all merged, so there is no need to list this more than once
    """

    thickness: float
    z0: float
    layer_num: int
    litho_base: List[str]
