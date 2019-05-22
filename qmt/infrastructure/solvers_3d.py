# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

from dataclasses import dataclass
from qmt.physics_constants import UArray

# fenics cannot be imported before kwant due to conflicting MUMPS loading mechanisms
if "fenics" in dir():
    del fenics
    import kwant
    import fenics
else:
    import kwant


@dataclass
class TransportData:
    conductance: float
    smatrix: kwant.solvers.common.SMatrix
    disorder: UArray
