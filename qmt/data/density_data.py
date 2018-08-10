# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

from qmt.data import Data

class Density1DData(Data):
    def __init__(self, densities, density_units, bands, band_units, mesh, mesh_units):
        """
        Constructs Data object stores density information for 1d.
         
        :param densities: list of numpy arrays, corresponding to the density in [conduction band, light holes, heavy holes]
        :param density_units: units of density
        :param bands: list of numpy arrays, corresponding to the band energy in [conduction band, light holes, heavy holes]
        :param band_units: units of band energy
        :param mesh: numpy array with the 1d mesh
        :param mesh_units: units of mesh points
        """
        super(Density1D, self).__init__()
        
        self.densities = densities
        self.density_units = density_units
        self.bands = bands
        self.band_units = band_units
        self.mesh = mesh
        self.mesh_units = mesh_units

    def _serialize(self):
        self.content['densities'] = self.densities
        self.content['density_units'] = self._serialize_unit(self.density_units)
        self.content['bands'] = self.bands
        self.content['band_units'] = self._serialize_unit(self.band_units)
        self.content['mesh'] = self.mesh
        self.content['mesh_units'] = self._serialize_unit(self.mesh_units)

    def _deserialize(self):
        self.densities = self.content['densities']
        self.denisty_units = self._deserialize_unit(self.content['density_units'])
        self.bands = self.content['bands']
        self.band_units = self._deserialize_unit(self.content['band_units'])
        self.mesh = self.content['mesh']
        self.mesh_units = self._deserialize_unit(self.content['mesh_units'])
