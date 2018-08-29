# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import fenics as fn
from qms.fem import fenics_expressions

import qmt.physics_constants as qc
from qmt.data.template import Data


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

    # def as_fenics_expression(self):


class FenicsPotentialData3D(InterpolatableScalarData3D):
    def __init__(self, fenics_potential, solver_input, coords_units,
                 data_units):
        mesh = solver_input.mesh
        # region_mapping = solver_input.region_mapping
        coords = mesh.coordinates()
        data = fenics_potential.compute_vertex_values()
        super(FenicsPotentialData3D, self).__init__(coords, data, coords_units, data_units, fenics_potential)
        self.phi = self.evaluate_point_function
        # TODO initialize surface and volume integrals
        # self.charge_density, self.parts_to_volume_charge_integrals = self._initialize_non_surface_charge_density(solver_input)
        # self.parts_to_boundary_densities, self.parts_to_boundary_charge_integrals = self._initialize_surface_densities(solver_input)

        # self.charge_density = self._initialize_charge_density(solver_input)
        # self.parts_to_volume_charge_integrals = self._initialize_volume_integrals(solver_input)
        # self.parts_to_boundary_charge_integrals = self._initialize_boundary_integrals(solver_input)


    # def _initialize_non_surface_charge_density(self, solver_input):
    #     raise NotImplementedError("Class is abstract. This method is delegated to subclasses.")
    #
    # def _initialize_surface_densities(self, solver_input):
    #     raise NotImplementedError("Class is abstract. This method is delegated to subclasses.")

    # # Figure out how to do this
    # def _initialize_charge_density(self, solver_input):
    #     # solve linear problem
    #     # Is this just an inverse Poisson solve?
    #
    #     # charge = PermittivityExpression()
    #     # result = fn.assemble()
    #     # todo project onto different space?
    #     # I think I have to project this. How do I get the right function space?
    #     # I want a piecewise constant vector-valued function space
    #     # or maybe, something derived from the vector space of phi?
    #     # How about one lower degree?
    #     # Waiit, I don't want to project the laplacian onto this space!!
    #     V = self.phi.function_space()
    #     # mesh = V.mesh()
    #     # degree = V.ufl_element().degree() - 1
    #     # element_type = 'DG' if degree == 0 else 'P'
    #     # gradient_vector_space = fn.VectorFunctionSpace(mesh, element_type, degree)
    #     # phi_laplacian = fn.div(fn.grad(self.phi))
    #     # TODO try doing this manually!
    #     rho = fn.TrialFunction(V)
    #     v = fn.TestFunction(V)
    #     L = fn.dot(fn.grad(self.phi), fn.grad(v)) * fn.dx
    #     a = rho * v * fn.dx
    #     rho = fn.Function(V)
    #     fn.solve(a == L, rho)
    #     return rho
    #     # return fn.project(phi_laplacian, V)
    #
    # def _initialize_volume_integrals(self, solver_input):
    #     # integrate solution of linear problem?
    #     # TODO include contained boundary?
    #     names_to_ids = solver_input.geo_3d_data.get_names_to_region_ids()
    #     measure = fn.Measure("dx", domain=solver_input.mesh,
    #                          subdomain_data=solver_input.region_mapping.region_mapping_function)
    #     volume_integrals = {}
    #     for name, region_id in names_to_ids.items():
    #         volume_integrals[name] = fn.assemble(self.charge_density * measure(region_id))
    #     return volume_integrals
    #
    # def _initialize_boundary_integrals(self, solver_input):
    #     # integrate up normal derivative :P
    #     names_to_ids = solver_input.geo_3d_data.get_names_to_region_ids()
    #     normal_derivative = fn.grad(self.phi)
    #
    #     boundary_integrals = {}
    #     for name, id in names_to_ids.items():
    #         part_measure = fn.Measure("dS", domain=solver_input.mesh,
    #                                   subdomain_data=solver_input.boundary_conditions.get_boundary(name))
    #         n = fn.FacetNormal(solver_input.mesh)
    #         boundary_integrals[name] = fn.assemble(
    #             (fn.dot(normal_derivative('-'), n('-')) + fn.dot(normal_derivative('+'), n('+'))) * part_measure)
    #
    #     return boundary_integrals


# TODO override integral initializers

class FenicsThomasFermiData3D(FenicsPotentialData3D):
    def __init__(self, fenics_potential, charge_density_function, solver_input, coords_units=qc.units.nm,
                 data_units=qc.units.meV):
        self.charge_density_function = charge_density_function
        super(FenicsThomasFermiData3D, self).__init__(fenics_potential, solver_input, coords_units, data_units)

    def _initialize_non_surface_charge_density(self, solver_input):
        names_to_ids = solver_input.geo_3d_data.get_names_to_region_ids()
        measure = fn.Measure("dx", domain=solver_input.mesh,
                                 subdomain_data=solver_input.region_mapping.region_mapping_function)
        # Straightforward
        # TODO

    def _initialize_surface_densities(self, solver_input):
        pass


class FenicsPoissonData3D(FenicsPotentialData3D):
    def __init__(self, fenics_potential, source_charge_options, solver_input, coords_units=qc.units.nm,
                 data_units=qc.units.meV):
        self.source_charge_options = source_charge_options
        super(FenicsPoissonData3D, self).__init__(fenics_potential, solver_input, coords_units, data_units)


    def _initialize_surface_densities(self, solver_input):
        pass
        # Could be encoded as double-valued FacetFunctions?
        # Can use code from utilities to get source terms?

    def _initialize_non_surface_charge_density(self, solver_input):
        # get terms from utilities, w/o measures
        pass
