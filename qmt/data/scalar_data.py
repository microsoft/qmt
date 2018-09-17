# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import fenics as fn

import qmt.physics_constants as qc
from qms.fem.fenics_expressions import make_u0_expression, make_3d_prefactor_expression
from qms.fem.fenics_utilities import get_accumulation_parts, get_raw_dit_term
from qmt.data.template import Data

import os
import codecs
import shutil


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


class FenicsPotentialData3D(ScalarData3D):
    def __init__(self, fenics_potential, solver_input, coords_units, data_units, inf_norm_inconsistency=None):
        mesh = solver_input.mesh
        coords = mesh.coordinates()
        data = fenics_potential.compute_vertex_values()

        super(FenicsPotentialData3D, self).__init__(coords, data, coords_units, data_units)
        self.inf_norm_inconsistency = inf_norm_inconsistency

        self._element_type = solver_input.element_type
        self._element_degree = solver_input.element_degree
        self._set_potential(fenics_potential, mesh)

        charge_density, self.parts_to_volume_charge_integrals = self._initialize_non_surface_charge_density(
            solver_input, fenics_potential)
        parts_to_boundary_densities, self.parts_to_boundary_charge_integrals = self._initialize_surface_densities(
            solver_input, fenics_potential)

        self._serial_volume_density_data = self.serialize_fenics_function(mesh, charge_density)

        self._serial_parts_to_boundary_densities = {part: self.serialize_fenics_function(mesh, density) for
                                                    part, density in
                                                    parts_to_boundary_densities.items()}

    def _initialize_non_surface_charge_density(self, solver_input, potential):
        raise NotImplementedError("Class is abstract. This method is delegated to subclasses.")

    def _initialize_surface_densities(self, solver_input, potential):
        raise NotImplementedError("Class is abstract. This method is delegated to subclasses.")

    # TODO refactor
    def _set_potential(self, fenics_potential, mesh):
        self._serial_potential_data = self.serialize_fenics_function(mesh, fenics_potential)

    def get_potential(self):
        return self.deserialize_fenics_function(self._serial_potential_data, self._element_type,
                                                self._element_degree)

    def get_parts_to_boundary_densities(self):
        results = {}
        for part, density in self._serial_parts_to_boundary_densities.items():
            # The density should be continuous on each part's boundary, so no need for discontinuous elements
            results[part] = self.deserialize_fenics_function(density, self._element_type, self._element_degree)

        return results

    def get_charge_density(self):
        return self.deserialize_fenics_function(self._serial_volume_density_data, "DG", self._element_degree)

    def deserialize_fenics_function(self, serial_function_data, element_type, element_degree):
        import uuid
        scratch_dir = 'tmp_' + str(uuid.uuid4())
        os.mkdir(scratch_dir)
        serial_mesh = serial_function_data.serial_mesh
        serial_fenics_function = serial_function_data.serial_function

        potential_path = os.path.join(scratch_dir, 'tmp_potential_' + str(hash(serial_fenics_function)) + '.xml')
        mesh_path = os.path.join(scratch_dir, 'tmp_potential_' + str(hash(serial_mesh)) + '.xml')

        decoded_potential = codecs.decode(serial_fenics_function.encode(), 'base64')
        decoded_mesh = codecs.decode(serial_mesh.encode(), 'base64')

        with open(potential_path, 'wb') as potential_file:
            potential_file.write(decoded_potential)

        with open(mesh_path, 'wb') as mesh_file:
            mesh_file.write(decoded_mesh)

        mesh = fn.Mesh(mesh_path)
        V = fn.FunctionSpace(mesh, element_type, element_degree)
        potential = fn.Function(V, potential_path)

        shutil.rmtree(scratch_dir)

        return potential

    # TODO implement from serialization above
    def serialize_fenics_function(self, mesh, fenics_function):
        import uuid
        scratch_dir = 'tmp_' + str(uuid.uuid4())

        function_path = os.path.join(scratch_dir, 'tmp_potential_' + str(hash(fenics_function)) + '.xml')
        mesh_path = os.path.join(scratch_dir, 'tmp_mesh_' + str(hash(mesh)) + '.xml')
        fn.File(function_path) << fenics_function
        fn.File(mesh_path) << mesh

        with open(function_path, 'rb') as potential_file:
            serial_function = codecs.encode(potential_file.read(), 'base64').decode()

        with open(mesh_path, 'rb') as mesh_file:
            serial_mesh = codecs.encode(mesh_file.read(), 'base64').decode()

        shutil.rmtree(scratch_dir)

        return SerialFenicsFunctionData(serial_mesh, serial_function)


class SerialFenicsFunctionData(object):

    def __init__(self, serial_mesh, serial_function):
        self.serial_mesh = serial_mesh
        self.serial_function = serial_function


class FenicsThomasFermiData3D(FenicsPotentialData3D):
    def __init__(self, fenics_potential, solver_input, coords_units, data_units, solver_options,
                 inf_norm_inconsistency=None):
        self.solver_options = solver_options
        super(FenicsThomasFermiData3D, self).__init__(fenics_potential, solver_input, coords_units, data_units,
                                                      inf_norm_inconsistency=inf_norm_inconsistency)

    def _initialize_non_surface_charge_density(self, solver_input, potential):
        names_to_ids = solver_input.geo_3d_data.get_names_to_region_ids()
        measure = solver_input.region_mapping.measure

        volume_charge_integrals = {}

        all_parts_density = fn.Constant(0.0)
        for part in solver_input.volume_charge_parts():
            region_id = names_to_ids[part]
            density = fn.Constant(0.0)
            inclusion_function = solver_input.region_mapping.inclusion_function(part)

            if part in solver_input.parts_to_volume_charges:
                ns = solver_input.parts_to_volume_charges[part]
                density += fn.Constant(ns) * inclusion_function

            if part in solver_input.accumulation_parts():
                known_potential = potential
                region_id = names_to_ids[part]
                density += make_accumulation_term(solver_input, known_potential) * inclusion_function

            volume_charge_integrals[part] = fn.assemble(density * measure(region_id))
            all_parts_density += density

            # Need to interpolate all_parts_density onto a suitable function space
            # Maybe DG
            density_V = fn.FunctionSpace(solver_input.mesh, "DG", self._element_degree)
            density_function = fn.project(all_parts_density, density_V)

        return density_function, volume_charge_integrals

    def _initialize_surface_densities(self, solver_input, potential):
        names_to_ids = solver_input.geo_3d_data.get_names_to_region_ids()
        measure = solver_input.boundary_conditions.names_to_measures

        surface_charge_integrals = {}
        surface_densities = {}

        for part in solver_input.surface_charge_parts():
            part_surface_density = fn.Constant(0.0)

            if part in solver_input.parts_to_neumann_bcs:
                charge_density = solver_input.parts_to_neumann_bcs[part]
                part_surface_density += fn.Constant(charge_density)

            if part in solver_input.parts_to_phi_nl_and_ds:
                known_potential = potential
                part_surface_density += get_raw_dit_term(part, solver_input.parts_to_phi_nl_and_ds[part], solver_input,
                                                         self.solver_options, known_potential)

            surface_charge_integrals[part] = fn.assemble(part_surface_density * measure[part])

            # Make boundary function space
            # region_id = names_to_ids[part]
            # sm = fn.SubMesh(solver_input.mesh, solver_input.region_mapping.region_mapping_function, region_id)
            # bm = fn.BoundaryMesh(sm, "exterior")
            # boundary_V = fn.FunctionSpace(bm, self._element_type, self._element_degree)
            # surface_density_function = fn.project(part_surface_density, boundary_V)
            #
            # surface_densities[part] = surface_density_function

        return {}, surface_charge_integrals

class FenicsPoissonData3D(FenicsPotentialData3D):
    def __init__(self, fenics_potential, solver_input, coords_units, data_units, inf_norm_inconsistency=None):
        # self.source_charge_options = source_charge_options
        super(FenicsPoissonData3D, self).__init__(fenics_potential, solver_input, coords_units, data_units)

    # TODO implement
    def _initialize_surface_densities(self, solver_input, potential):
        return None, None
        # Could be encoded as double-valued FacetFunctions?
        # Can use code from utilities to get source terms?

    # TODO implement
    def _initialize_non_surface_charge_density(self, solver_input, potential):
        return None, None
