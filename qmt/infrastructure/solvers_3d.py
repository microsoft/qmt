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
class TransportData:
    conductance: float
    smatrix: kwant.solvers.common.SMatrix
    disorder: UArray
