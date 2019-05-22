# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import kwant
from dataclasses import dataclass
from qmt.physics_constants import UArray


@dataclass
class TransportData:
    conductance: float
    smatrix: kwant.solvers.common.SMatrix
    disorder: UArray
