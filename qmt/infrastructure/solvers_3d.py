# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

from dataclasses import dataclass
from qmt.physics_constants import UArray
from kwant.solvers.common import SMatrix


@dataclass
class TransportData:
    conductance: float
    smatrix: SMatrix
    disorder: UArray
