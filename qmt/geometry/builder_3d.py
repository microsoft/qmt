"""
The Geo3DBuilder class, which is used to build 3D geometries
"""

from typing import List, Optional
from qmt.data import serialize_file, write_deserialised
import FreeCAD
from .part_3d import (
    DepoMode,
    ExtrudeData,
    LithographyData,
    Part3DData,
    SAGData,
    WireData,
    WireShellData,
)
from qmt.geometry import Geo3DData


class Geo3DBuilder:
    def extrusion(
        self,
        label: str,
        fc_name: Optional[str],
        thickness: float,
        z0: float,
        virtual: bool = False,
    ) -> ExtrudeData:
        fc_name = label if not fc_name else fc_name
        return ExtrudeData(fc_name, label, virtual, thickness, z0)

    def wire(
        self,
        label: str,
        fc_name: Optional[str],
        thickness: float,
        z0: float,
        virtual: bool = False,
    ) -> WireData:
        fc_name = label if not fc_name else fc_name
        return WireData(fc_name, label, virtual, thickness, z0)

    def wire_shell(
        self,
        label: str,
        fc_name: Optional[str],
        thickness: float,
        target_wire: WireData,
        shell_verts: List[int],
        depo_mode: str,
        virtual: bool = False,
    ) -> WireShellData:
        fc_name = label if not fc_name else fc_name
        try:
            depo_mode = DepoMode[depo_mode]
        except KeyError:
            raise ValueError(
                f"{depo_mode} is not a valid depo mode. Options are "
                f"{[d.name for d in DepoMode]}"
            )
        return WireShellData(
            fc_name, label, virtual, thickness, target_wire, shell_verts, depo_mode
        )

    def SAG(
        self,
        label: str,
        fc_name: Optional[str],
        thickness: float,
        z0: float,
        z_middle: float,
        t_in: float,
        t_out: float,
        virtual: bool = False,
    ) -> SAGData:
        fc_name = label if not fc_name else fc_name
        return SAGData(fc_name, label, virtual, thickness, z0, z_middle, t_in, t_out)

    def lithography(
        self,
        label: str,
        fc_name: Optional[str],
        thickness: float,
        z0: float,
        layer_num: int,
        litho_base: List[str],
        virtual: bool = False,
    ) -> LithographyData:
        fc_name = label if not fc_name else fc_name
        return LithographyData(
            fc_name, label, virtual, thickness, z0, layer_num, litho_base
        )

    def shape3d(
        self, label: str, fc_name: Optional[str], virtual: bool = False
    ) -> Part3DData:
        fc_name = label if not fc_name else fc_name
        return Part3DData(fc_name, label, virtual)

    def build_3d_geometry(
        self,
        input_parts,
        input_file=None,
        xsec_dict=None,
        serialized_input_file=None,
        params=None,
    ):
        """
        Build a geometry in 3D.

        :param list input_parts: Ordered list of input parts, leftmost items get built first
        :param str input_file: Path to FreeCAD template file. Either this or serialized_input_file
            must be set (but not both).
        :param dict xsec_dict: Dictionary of cross-section specifications. It should be of the
            form {'xsec_name':{'axis':(1,0,0),'distance':0.}}, where the axis parameter is a tuple
            defining the axis that defines the normal of the cross section, and distance is
            the length along the axis used to set the cross section.
        :param bytes serialized_input_file: FreeCAD template file that has been serialized using
            qmt.data.serialize_file. This is useful for passing a
            file into a docker container or other environment that
            doesn't have access to a shared drive. Either this or
            serialized_input_file must be set (but not both).
        :param dict params: Dictionary of parameters to use in FreeCAD.
        :return Geo3DData: A built geometry.
        """
        if input_file is None and serialized_input_file is None:
            raise ValueError(
                "One of input_file or serialized_input_file must be non-none."
            )
        elif input_file is not None and serialized_input_file is not None:
            raise ValueError("Both input_file and serialized_input_file were non-none.")
        elif input_file is not None:
            serial_fcdoc = serialize_file(input_file)
        else:
            serial_fcdoc = serialized_input_file
        if params is None:
            params = {}
        if xsec_dict is None:
            xsec_dict = {}
        options_dict = {}
        options_dict["serial_fcdoc"] = serial_fcdoc
        options_dict["input_parts"] = input_parts
        options_dict["params"] = params
        options_dict["xsec_dict"] = xsec_dict

        data = Geo3DData()
        data.serial_fcdoc = serial_fcdoc
        data.get_data("fcdoc")
        from qmt.geometry.freecad.objectConstruction import build

        built = build(options_dict)
        FreeCAD.closeDocument("instance")
        return built
