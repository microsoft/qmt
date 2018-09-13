# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

from qmt.data.template import Data

class MobilityData(Data):
    def __init__(self, conductance, conductance_units, mobility, mobility_units):
        """
        Constructs Data object stores density information for 1d.
         
        :param densities: list of numpy arrays, corresponding to the density in [conduction band, light holes, heavy holes]
        :param density_units: units of density
        :param bands: list of numpy arrays, corresponding to the band energy in [conduction band, light holes, heavy holes]
        :param band_units: units of band energy
        :param mesh: numpy array with the 1d mesh
        :param mesh_units: units of mesh points
        """
        super(MobilityData, self).__init__()
        
        self.conductance = conductance
        self.conductance_units = conductance_units
        self.mobility = mobility
        self.mobility_units = mobility_units

    def _serialize(self):
        self.content['conductance'] = self.conductance
        self.content['conductance_units'] = self.conductance_units
        self.content['mobility'] = self.mobility
        self.content['mobility_units'] = self.mobility_units

