# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

from collections import namedtuple

Potential2dData = namedtuple(
    "Potential2dData",
    ["coordinates", "coordinate_units", "potential", "potential_units"],
)
ThomasFermi2dData = namedtuple(
    "ThomasFermi2dData",
    [
        "coordinates",
        "potential",
        "density",
        "conduction_band",
        "valence_band",
        "reference_level",
        "temperature",
        "coordinate_units",
        "potential_units",
        "energy_units",
    ],
)

Bdg2dData = namedtuple(
    "Bdg2dData",
    [
        "coordinates",
        "energies",
        "wave_functions",
        "coordinate_units",
        "energy_units",
        "hamiltonian",
    ],
)


Phase2dData = namedtuple(
    "Phase2dData", ["coordinates", "superconducting_phase", "coordinate_units"]
)

# TODO: this needs to be pruned
class SchrodingerPoissonDatas:
    def __init__(
        self,
        poisson_obj,
        density,
        density_per_subband,
        density_units,
        rho,
        rho_units,
        psis,
        energies,
        potential,
        potential_units,
        mesh,
        mesh_units,
        bands,
        temperature,
        band_charges,
        Dit,
        neutral_level,
        fixed_charge_sites,
        fixed_charge_site_perimeters,
    ):
        """
        Constructs Data object stores outputs of Thomas-Fermi Task.

        :param poisson_obj: A qms.physics.Poisson object containing relevant boundary conditions,
        etc.
        :param densities: list of numpy arrays, corresponding to the density in [conduction band,
        light holes, heavy holes]
        :param density_units: units of density
        :param mesh: numpy array with the 1d mesh
        :param mesh_units: units of mesh points
        """
        self.content = {}
        self.poisson = poisson_obj
        self.density = density
        self.density_per_subband = density_per_subband
        self.density_units = density_units
        self.rho = rho
        self.rho_units = rho_units
        self.psis = psis
        self.energies = energies
        self.potential = potential
        self.potential_units = potential_units
        self.mesh = mesh
        self.mesh_units = mesh_units
        self.bands = bands
        self.temperature = temperature
        self.band_charges = band_charges
        self.Dit = Dit
        self.neutral_level = neutral_level
        self.fixed_charge_sites = fixed_charge_sites
        self.fixed_charge_site_perimeters = fixed_charge_site_perimeters

    def _serialize(self):
        self.content["poisson"] = self.poisson
        self.content["density"] = self.density
        self.content["density_per_subband"] = self.density_per_subband
        self.content["density_units"] = self._serialize_unit(self.density_units)
        self.content["rho"] = self.rho
        self.content["rho_units"] = self._serialize_unit(self.rho_units)
        self.content["psis"] = self.psis
        self.content["energies"] = self.energies
        self.content["potential"] = self.potential
        self.content["potential_units"] = self._serialize_unit(self.potential_units)
        self.content["mesh"] = self.mesh
        self.content["mesh_units"] = self._serialize_unit(self.mesh_units)
        self.content["bands"] = self.bands
        self.content["temperature"] = self.temperature
        self.content["band_charges"] = self.band_charges
        self.content["Dit"] = self.Dit
        self.content["neutral_level"] = self.neutral_level
        self.content["fixed_charge_sites"] = self.fixed_charge_sites
        self.content["fixed_charge_site_perimeters"] = self.fixed_charge_site_perimeters

    def _deserialize(self):
        self.poisson = self.content["poisson"]
        self.density = self.content["density"]
        self.density_per_subband = self.content["density_per_subband"]
        self.denisty_units = self._deserialize_unit(self.content["density_units"])
        self.rho = self.content["rho"]
        self.rho_units = self._deserialize_unit(self.content["rho_units"])
        self.psis = self.content["psis"]
        self.energies = self.content["energies"]
        self.potential = self.content["potential"]
        self.potential_units = self._deserialize_unit(self.content["potential_units"])
        self.mesh = self.content["mesh"]
        self.mesh_units = self._deserialize_unit(self.content["mesh_units"])
        self.bands = self.content["bands"]
        self.temperature = self.content["temperature"]
        self.band_charges = self.content["band_charges"]
        self.Dit = self.content["Dit"]
        self.neutral_level = self.content["neutral_level"]
        self.fixed_charge_sites = self.content["fixed_charge_sites"]
        self.fixed_charge_site_perimeters = self.content["fixed_charge_site_perimeters"]
