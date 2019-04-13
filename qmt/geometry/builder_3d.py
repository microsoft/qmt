from enum import Enum
from dataclasses import dataclass, field
from typing import List, Optional
from qmt.data.data_utils import write_deserialised


class DomainType(Enum):
    """
    - semiconductor -- region permitted to self-consistently accumulate
    - metal_gate -- an electrode
    - virtual -- a part just used for selection (ignores material)
    - dielectric -- no charge accumulation allowed
    """

    semiconductor = 1
    metal_gate = 2
    virtual = 3
    dielectric = 4


@dataclass
class Part3DData:
    """
    Base class for a 3D geometric part.
    :param domain_type: The type of domain this part represents
    :param fc_name: The name of the 2D/3D freeCAD object that this is built from. Note
        that if the label used for the 3D part is the same as the freeCAD label, and that
        label is unique, None may be used here as a shortcut
    :param label: The descriptive name of this new part
    :param material: The material of the resulting part.
    """

    built_fc_name: Optional[str] = field(init=False)  # This gets set on geometry build
    domain_type: DomainType
    fc_name: str
    label: str
    material: Optional[str]
    serial_stp: Optional[str] = field(init=False)  # This gets set on geometry build

    def __post_init__(self):
        if not self.material and self.domain_type == DomainType.virtual:
            raise ValueError(
                f"Material must be provided for non virtual ({self.domain_type.name}) "
                f"part {self.label}"
            )
        elif self.material and self.domain_type == DomainType.virtual:
            raise ValueError(f"Material provided for virtual part {self.label}")

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


class Geom3DBuilder:
    def extrusion(
        self,
        label: str,
        fc_name: Optional[str],
        domain_type: str,
        material: Optional[str],
        thickness: float,
        z0: float,
    ) -> ExtrudeData:
        domain_type = Geom3DBuilder.convert_domain_type(domain_type)
        fc_name = label if not fc_name else fc_name
        return ExtrudeData(domain_type, fc_name, label, material, thickness, z0)

    def wire(
        self,
        label: str,
        fc_name: Optional[str],
        domain_type: str,
        material: Optional[str],
        thickness: float,
        z0: float,
    ) -> WireData:
        domain_type = Geom3DBuilder.convert_domain_type(domain_type)
        fc_name = label if not fc_name else fc_name
        return WireData(domain_type, fc_name, label, material, thickness, z0)

    def wire_shell(
        self,
        label: str,
        fc_name: Optional[str],
        domain_type: str,
        material: Optional[str],
        thickness: float,
        target_wire: WireData,
        shell_verts: List[int],
        depo_mode: str,
    ) -> WireShellData:
        domain_type = Geom3DBuilder.convert_domain_type(domain_type)
        fc_name = label if not fc_name else fc_name
        try:
            depo_mode = DepoMode[depo_mode]
        except KeyError:
            raise ValueError(
                f"{depo_mode} is not a valid depo mode. Options are "
                f"{[d.name for d in DepoMode]}"
            )
        return WireShellData(
            domain_type,
            fc_name,
            label,
            material,
            thickness,
            target_wire,
            shell_verts,
            depo_mode,
        )

    def SAG(
        self,
        label: str,
        fc_name: Optional[str],
        domain_type: str,
        material: Optional[str],
        thickness: float,
        z0: float,
        z_middle: float,
        t_in: float,
        t_out: float,
    ) -> SAGData:
        domain_type = Geom3DBuilder.convert_domain_type(domain_type)
        fc_name = label if not fc_name else fc_name
        return SAGData(
            domain_type, fc_name, label, material, thickness, z0, z_middle, t_in, t_out
        )

    def lithography(
        self,
        label: str,
        fc_name: Optional[str],
        domain_type: str,
        material: Optional[str],
        thickness: float,
        z0: float,
        layer_num: int,
        litho_base: List[str],
    ) -> LithographyData:
        domain_type = Geom3DBuilder.convert_domain_type(domain_type)
        fc_name = label if not fc_name else fc_name
        return LithographyData(
            domain_type, fc_name, label, material, thickness, z0, layer_num, litho_base
        )

    def shape3d(
        self,
        label: str,
        fc_name: Optional[str],
        domain_type: str,
        material: Optional[str],
    ) -> Part3DData:
        domain_type = Geom3DBuilder.convert_domain_type(domain_type)
        fc_name = label if not fc_name else fc_name
        return Part3DData(domain_type, fc_name, label, material)

    @staticmethod
    def convert_domain_type(domain_str: str) -> DomainType:
        try:
            return DomainType[domain_str]
        except KeyError:
            raise ValueError(
                f"{domain_str} is not a valid domain type. Options are "
                f"{[d.name for d in DomainType]}"
            )
