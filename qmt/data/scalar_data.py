# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import qmt.physics_constants as qc
from qmt.data import Data

# Abstract class
class ScalarData(Data):
    def __init__(self):
        super(ScalarData, self).__init__()

    def _serialize(self):
        self.content['coords'] = self.coords
        self.content['coords_units'] = self._serialize_unit(self.coords_units)
        self.content['data'] = self.data
        self.content['data_units'] = self._serialize_unit(self.data_units)

    def _deserialize(self):
        self.coords = self.content['coords']
        self.coords_units = self._deserialize_unit(self.content['coords_units'])
        self.data = self.content['data']
        self.data_units = self._deserialize_unit(self.content['data_units'])

class ScalarData3D(ScalarData):
    def __init__(self, coords, data, coords_units, data_units):
        super(ScalarData3D, self).__init__()
        self.coords = coords
        self.coords_units = coords_units
        self.data = data
        self.data_units = data_units

class InterpolatableScalarData3D(ScalarData3D):
    def __init__(self, coords, data, coords_units, data_units, evaluate_point_function):
        super(InterpolatableScalarData3D, self).__init__(coords, data, coords_units, data_units)
        self.evaluate_point_function = evaluate_point_function

    def evaluate(self, point):
        return self.evaluate_point_function(point)

class FenicsPotentialData3D(InterpolatableScalarData3D):
    def __init__(self, fenics_potential, fenics_mesh, coords_units=qc.units.nm, data_units=qc.units.meV):
        coords = fenics_mesh.coordinates()
        data = fenics_potential.compute_vertex_values()
        super(FenicsPotentialData3D, self).__init__(coords, data, coords_units, data_units, fenics_potential)