# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

from collections import namedtuple
import sympy.physics.units as spu
import kwant  # kwant import to stop fenics from segfaulting
from qmt.infrastructure import store_serial, load_serial
import fenics as fn
from dataclasses import dataclass
from typing import Dict, Optional
from qmt.physics_constants import UArray
from sympy.core.mul import Mul


@dataclass
class Fem3DData:
    coordinates: UArray
    potential: UArray
    reference_level: Mul
    charge: Optional[UArray] = None
    surface_charge_integrals: Optional[Dict[str, Mul]] = None
    volume_charge_integrals: Optional[Dict[str, Mul]] = None
    uniform_export: Optional[Dict[str, UArray]] = None
    fenics_3d_data: Optional[Dict[str, bytes]] = None

    def get_data(self, data):
        if data == "function":
            return deserialize_fenics_function(self.fenics_3d_data)
        else:
            print(f"Unknown datatype {data} for get_data function")


class SerialFenicsFunctionData:
    def __init__(self, serial_mesh, serial_function):
        self.serial_mesh = serial_mesh
        self.serial_function = serial_function


def serialize_fenics_function(mesh, fenics_function):
    def _write_fenics_file(data, path):
        fn.File(path) << data

    serial_mesh = store_serial(mesh, _write_fenics_file, "xml")
    serial_function = store_serial(fenics_function, _write_fenics_file, "xml")

    return SerialFenicsFunctionData(serial_mesh, serial_function)


def deserialize_fenics_function(
    serial_function_data, element_type="P", element_degree=2
):
    serial_mesh = serial_function_data.serial_mesh
    serial_fenics_function = serial_function_data.serial_function

    mesh = load_serial(serial_mesh, fn.Mesh, ext_format="xml")

    def _load_fenics_function(path):
        V = fn.FunctionSpace(mesh, element_type, element_degree)
        return fn.Function(V, path)

    potential = load_serial(
        serial_fenics_function, _load_fenics_function, ext_format="xml"
    )
    return potential


@dataclass
class TransportData:
    conductance: float
    smatrix: kwant.solvers.common.SMatrix
    disorder: UArray
