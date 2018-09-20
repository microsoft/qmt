# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

from qmt.data import Data

class ThomasFermiData(Data):
    def __init__(self,*,poisson_obj=None, density=None, density_units=None, rho=None,
                 rho_units=None, mesh=None, mesh_units=None, masses=None, bands=None,
                 temperature=None, band_charges=None, eunit=None, fixed_charge_sites=None,
                 fixed_charge_site_perimeters=None):
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
