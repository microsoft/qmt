# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

from qmt.task_framework import Data

class Potential3D(Data):
    def __init__(self, coords, coords_units, data, data_units):
        """
        Constructs Data object stores electrostatic potential information for 3d.
         
        :param coords: array of shape (n,3) where n is the number of mesh points.
        :param coords_units: units of mesh points
        :param data: array of shape (n,) where n is the number of mesh points
        :param data_units: units of potential data
        """
        super(Potential3D, self).__init__()
        
        self.coords = coords
        self.coords_units = coords_units
        self.data = data
        self.data_units = data_units

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
