# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

from qmt.task_framework import Data

class Density1D(Data):
    def __init__(self, densities, density_units, bands, band_units):
        """
        Constructs Data object stores density information for 1d.
         
        :param densities: list of numpy arrays, corresponding to the density in [conduction band, light holes, heavy holes]
        :param density_units: units of density
        :param bands: list of numpy arrays, corresponding to the band energy in [conduction band, light holes, heavy holes]
        :param band_units: units of band energy
        """
        super(Density1D, self).__init__()
        
        self.densities = densities
        self.density_units = density_units
        self.bands = bands
        self.band_units = band_units

    def _serialize(self):
        self.content['densities'] = self.densities
        self.content['density_units'] = self._serialize_unit(self.density_units)
        self.content['bands'] = self.bands
        self.band_units['band_units'] = self._serialize_unit(self.band_units)

    def _deserialize(self):
        self.densities = self.content['densities']
        self.denisty_units = self._deserialize_unit(self.content['density_units'])
        self.bands = self.content['bands']
        self.band_units = self._deserialize_unit(self.content['band_units'])
