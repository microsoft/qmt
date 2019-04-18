"""
Contains classes used to describe 3d geometry parts
"""

from typing import List, Optional
from qmt.data import write_deserialised
from enum import Enum


class Part3DData:
    def __init__(self, label: str, fc_name: Optional[str], virtual: bool = False):
        """Base class for a 3D geometric part.

        Parameters
        ----------
        label : str
            The descriptive name of this new part.
        fc_name : str
            The name of the 2D/3D freeCAD object that this is built from. Note that if the
            label used for the 3D part is the same as the freeCAD label, and that label is
            unique, None may be used here as a shortcut.
        virtual : bool
            Whether the part is virtual or not
            (Default value = False)
        """
        self.built_fc_name: Optional[str] = None  # This gets set on geometry build
        self.fc_name = label if fc_name is None else fc_name
        self.label = label
        self.serial_stl: Optional[str] = None  # This gets set on geometry build
        self.serial_stp: Optional[str] = None  # This gets set on geometry build
        self.virtual = virtual

    def write_stp(self, file_path=None):
        """Write part geometry to a STEP file.

        Returns the STEP file path.

        Parameters
        ----------
        file_path : str
            (Default value = None)
        Returns
        -------
        file_path

        """
        if file_path is None:
            file_path = f"{self.label}.stp"
        write_deserialised(self.serial_stp, file_path)
        return file_path

    def write_stl(self, file_path=None):
        """Write part geometry to a STEP file.

        Returns the STEP file path.

        Parameters
        ----------
        file_path : str
            (Default value = None)
        Returns
        -------
        file_path

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
        """Class for geometric extrusions.

        Parameters
        ----------
        label : str
            The descriptive name of this new part.
        fc_name : str
            The name of the 2D/3D freeCAD object that this is built from. Note that if the
            label used for the 3D part is the same as the freeCAD label, and that label is
            unique, None may be used here as a shortcut.
        thickness : float
            The extrusion thickness.
        z0 : float
            The starting z coordinate.
            (Default value = 0.0)
        virtual : bool
            Whether the part is virtual or not.
            (Default value = False)
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
        """Class for hexagonal wire.

        Parameters
        ----------
        label : str
            The descriptive name of this new part.
        fc_name : str
            The name of the 2D/3D freeCAD object that this is built from. Note that if the
            label used for the 3D part is the same as the freeCAD label, and that label is
            unique, None may be used here as a shortcut.
        thickness : float
            The wire thickness.
        z0 : float
            The starting z coordinate.
            (Default value = 0.0)
        virtual : bool
            Whether the part is virtual or not.
            (Default value = False)
        """
        self.thickness = thickness
        self.z0 = z0
        super().__init__(label, fc_name, virtual=virtual)


class DepoMode(Enum):
    """
    'depo' or 'etch' defines the positive or negative mask for the deposition of a wire
    coating.
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
        """Class for the geometry of a wire shell.

        Parameters
        ----------
        label : str
            The descriptive name of this new part.
        fc_name : str
            The name of the 2D/3D freeCAD object that this is built from. Note that if the
            label used for the 3D part is the same as the freeCAD label, and that label is
            unique, None may be used here as a shortcut.
        thickness : float
            The shell thickness.
        target_wire : WireData
            Target wire for coating.
        shell_verts : List[int]
            Vertices to use when rendering the coating.
        depo_mode : str
            'depo' or 'etch' defines the positive or negative mask.
        virtual : bool
            Whether the part is virtual or not.
            (Default value = False)
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
        """Class for selective area growth

        Parameters
        ----------
        label : str
            The descriptive name of this new part.
        fc_name : str
            The name of the 2D/3D freeCAD object that this is built from. Note that if the
            label used for the 3D part is the same as the freeCAD label, and that label is
            unique, None may be used here as a shortcut.
        thickness : float
            The total SAG thickness.
        z_middle : float
            The location for the "flare out".
        t_in : float
            The lateral distance from the 2D profile to the edge of the top bevel.
        t_out : float
            The lateral distance from the 2D profile to the furthest "flare out"
            location.
        z0 : float
            The starting z coordinate.
            (Default value = 0.0)
        virtual : bool
            Whether the part is virtual or not.
            (Default value = False)
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
        """Class for lithography.

        Parameters
        ----------
        label : str
            The descriptive name of this new part.
        fc_name : str
            The name of the 2D/3D freeCAD object that this is built from. Note that if the
            label used for the 3D part is the same as the freeCAD label, and that label is
            unique, None may be used here as a shortcut.
        thickness : float
            The lithography thickness.
        layer_num : int
            The layer number. Lower numbers go down first, with higher numbers deposited
            last.
        z0 : float
            The starting z coordinate.
            (Default value = 0.0)
        litho_base : List[str]
            The base partNames to use. For multi-step lithography, the bases are just all
            merged, so there is no need to list this more than once.
            (Default value = [])
        virtual : bool
            Whether the part is virtual or not.
            (Default value = False)
        """
        self.thickness = thickness
        self.z0 = z0
        self.layer_num = layer_num
        self.litho_base = litho_base
        super().__init__(label, fc_name, virtual=virtual)
