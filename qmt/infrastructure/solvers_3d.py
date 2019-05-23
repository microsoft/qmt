# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

from dataclasses import dataclass
from qmt.physics_constants import UArray
import kwant


@dataclass
class TransportData:
    conductance: float
    smatrix: kwant.solvers.common.SMatrix
    disorder: UArray
