# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

from qmt.data import Data

class ThomasFermiData(Data):
    def __init__(self, poisson_obj, density, density_units, rho, rho_units, mesh, mesh_units, masses, bands, temperature, band_charges, eunit, fixed_charge_sites, fixed_charge_site_perimeters):
        """
        Constructs Data object stores outputs of Thomas-Fermi Task.
         
        :param poisson_obj: A qms.physics.Poisson object containing relevant boundary conditions, etc.
        :param densities: list of numpy arrays, corresponding to the density in [conduction band, light holes, heavy holes]
        :param density_units: units of density
        :param mesh: numpy array with the 1d mesh
        :param mesh_units: units of mesh points
        """
        super(ThomasFermiData, self).__init__()

        self.poisson = poisson_obj
        self.density = density
        self.density_units = density_units
        self.rho = rho
        self.rho_units = rho_units
        self.mesh = mesh
        self.mesh_units = mesh_units
        self.masses = masses
        self.bands = bands
        self.temperature = temperature
        self.band_charges = band_charges
        self.eunit = eunit
        self.fixed_charge_sites = fixed_charge_sites
        self.fixed_charge_site_perimeters = fixed_charge_site_perimeters

    def _serialize(self):
        self.content['poisson'] = self.poisson
        self.content['density'] = self.density
        self.content['density_units'] = self._serialize_unit(self.density_units)
        self.content['rho'] = self.rho
        self.content['rho_units'] = self._serialize_unit(self.rho_units)
        self.content['mesh'] = self.mesh
        self.content['mesh_units'] = self._serialize_unit(self.mesh_units)
        self.content['masses'] = self.masses
        self.content['bands'] = self.bands
        self.content['temperature'] = self.temperature
        self.content['band_charges'] = self.band_charges
        self.content['eunit'] = self._serialize_unit(self.eunit)
        self.content['fixed_charge_sites'] = self.fixed_charge_sites
        self.content['fixed_charge_site_perimeters'] = self.fixed_charge_site_perimeters

    def _deserialize(self):
        self.poisson = self.content['poisson']
        self.density = self.content['density']
        self.denisty_units = self._deserialize_unit(self.content['density_units'])
        self.rho = self.content['rho']
        self.rho_units = self._deserialize_unit(self.content['rho_units'])
        self.mesh = self.content['mesh']
        self.mesh_units = self._deserialize_unit(self.content['mesh_units'])
        self.masses = self.content['masses']
        self.bands = self.content['bands']
        self.temperature = self.content['temperature']
        self.band_charges = self.content['band_charges']
        self.eunit = self._deserialize_unit(self.content['eunit'])
        self.fixed_charge_sites = self.content['fixed_charge_sites']
        self.fixed_charge_site_perimeters = self.content['fixed_charge_site_perimeters']
