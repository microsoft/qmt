# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

"""Geometry data classes."""

from qmt.materials import Materials
from qmt.data.template import Data
from .data_utils import load_serial, store_serial, write_deserialised
from shapely.ops import cascaded_union



class Geo2DData(Data):
    """Class holding 2D geometry data."""
    def __init__(self):
        """
        Class for holding a 2D geometry specification. This class holds two main dicts:
            - parts is a dictionary of shapely Polygon objects
            - edges is a dictionary of shapely LineString objects
        Parts are intended to be 2D domains, while edges are used for setting boundary conditions
        and surface conditions.
        """
        super(Geo2DData, self).__init__()
        self.parts = {}
        self.edges = {}
        self.build_order = []

    def add_part(self, part_name, part, overwrite=False):
        """
        Add a part to this geometry.
        :param str part_name: Name of the part to create
        :param Polygon part: Polygon object from shapely.geometry. This must be a valid Polygon.
        :param bool overwrite: Should we allow this to overwrite?
        """
        if not part.is_valid:
            raise ValueError("Part " + part_name + " is not a valid polygon.")
        if (part_name in self.parts) and (not overwrite):
            raise ValueError("Attempted to overwrite the part " + part_name + ".")
        else:
            self.parts[part_name] = part
            self.build_order += [part_name]

    def remove_part(self, part_name, ignore_if_absent=False):
        """
        Remove a part from this geometry.
        :param str part_name: Name of part to remove
        :param bool ignore_if_absent: Should we ignore an attempted removal if the part name
        is not found?
        """
        if part_name in self.parts:
            del self.parts[part_name]
            self.build_order.remove(part_name)
        else:
            if not ignore_if_absent:
                raise ValueError(
                    "Attempted to remove the part " + part_name + ", which doesn't exist.")
            else:
                pass

    def add_edge(self, edge_name, edge, overwrite=False):
        """
        Add an edge to this geometry.
        :param str edge_name: Name of the edge to create
        :param LineString edge: LineString object from shapely.geometry.
        :param bool overwrite: Should we allow this to overwrite?
        """
        if (edge_name in self.edges) and (not overwrite):
            raise ValueError("Attempted to overwrite the edge " + edge_name + ".")
        else:
            self.edges[edge_name] = edge
            self.build_order += [edge_name]

    def remove_edge(self, edge_name, ignore_if_absent=False):
        """
        Remove an edge from this geometry.
        :param str edge_name: Name of part to remove
        :param bool ignore_if_absent: Should we ignore an attempted removal if the part name
        is not found?
        """
        if edge_name in self.edges:
            del self.edges[edge_name]
            self.build_order.remove(edge_name)
        else:
            if not ignore_if_absent:
                raise ValueError(
                    "Attempted to remove the edge " + edge_name + ", which doesn't exist.")
            else:
                pass

    def compute_bb(self):
        """
        Computes the bounding box of all of the parts and edges in the geometry.
        :return bb_list: List of [min_x,max_x,min_y,max_y]
        """
        all_shapes = list(self.parts.values()) + list(self.edges.values())
        bbox_vertices = cascaded_union(all_shapes).envelope.exterior.coords.xy
        min_x = min(bbox_vertices[0])
        max_x = max(bbox_vertices[0])
        min_y = min(bbox_vertices[1])
        max_y = max(bbox_vertices[1])
        return [min_x, max_x,min_y, max_y]

class Geo3DData(Data):
    """Class holding 3D geometry data."""
    EXTERIOR_BC_NAME = "exterior"

    def __init__(self):
        """
        Class for a 3D geometry specification. It holds:
            - parts is a dict of Part3D objects, keyed by the label of each Part3D object.
            - build_order is a list of strings indicating the construction order.
        """
        super(Geo3DData, self).__init__()

        self.build_order = []
        self.parts = {}  # dict of parts in this geometry
        self.serial_fcdoc = None  # serialized FreeCAD document for this geometry
        self.serial_mesh = None  # Holding container for the serialized xml of the meshed geometry
        self.serial_region_marker = None  # Holding container for the serialized xml of the region
        # marker function
        self.fenics_ids = None  # dictionary with part name keys mapping to fenics ids.
        self.materials_database = Materials()

    def get_material(self, part_name):
        return self.materials_database[self.parts[part_name].material]

    def get_material_mapping(self):
        """
        Get mapping of part names to materials.
        :return:
        """
        return {name: self.get_material(name) for name in self.parts.keys()}

    def add_part(self, part_name, part, overwrite=False):
        """
        Add a part to this geometry.
        :param str part_name: Name of the part to create
        :param Part3D part: Part3D object.
        :param bool overwrite: Should we allow this to overwrite?
        """
        if (part_name in self.parts) and (not overwrite):
            raise ValueError("Attempted to overwrite the part " + part_name + ".")
        else:
            self.build_order.append(part.label)
            self.parts[part_name] = part

    def remove_part(self, part_name, ignore_if_absent=False):
        """
        Remove a part from this geometry.
        :param str part_name: Name of part to remove
        :param bool ignore_if_absent: Should we ignore an attempted removal if the part name
        is not found?
        """
        if part_name in self.parts:
            del self.parts[part_name]
        else:
            if not ignore_if_absent:
                raise ValueError(
                    "Attempted to remove the part " + part_name + ", which doesn't exist.")
            else:
                pass

    def set_data(self, data_name, data, scratch_dir=None):
        """
        Set data to a serial format that is easily portable.
        :param str data_name:  "fcdoc" freeCAD document \
                               "mesh"  fenics mesh \
                               "rmf"   fenics region marker function
        :param data:           The corresponding data that we would like to set.
        :param scratch_dir:    Optional existing temporary (fast) storage location.
        """
        if data_name == 'fcdoc':
            def _save_fct(doc, path):
                doc.saveAs(path)
            self.serial_fcdoc = store_serial(data, _save_fct, 'fcstd', scratch_dir=scratch_dir)

        elif data_name == 'mesh' or data_name == 'rmf':
            import fenics as fn

            def _save_fct(data, path):
                fn.File(path) << data
            if data_name == 'mesh':
                self.serial_mesh = store_serial(data, _save_fct, 'xml', scratch_dir=scratch_dir)
            if data_name == 'rmf':
                self.serial_region_marker = store_serial(data, _save_fct, 'xml',
                                                         scratch_dir=scratch_dir)

        else:
            raise ValueError(str(data_name) + ' was not a valid data_name.')

    def get_data(self, data_name, mesh=None, scratch_dir=None):
        """
        Get data from stored serial format.
        :param str data_name:  "fcdoc" freeCAD document \
                               "mesh"  fenics mesh \
                               "rmf"   fenics region marker function
        :param mesh:
        :param scratch_dir:    Optional existing temporary (fast) storage location.
        :return data:          The freeCAD document or fenics object that was stored.
        """
        if data_name == 'fcdoc':
            import FreeCAD

            def _load_fct(path):
                doc = FreeCAD.newDocument('instance')
                FreeCAD.setActiveDocument('instance')
                doc.load(path)
                return doc
            return load_serial(self.serial_fcdoc, _load_fct, scratch_dir=scratch_dir)

        elif data_name == 'mesh':
            import fenics as fn

            def _load_fct(path):
                return fn.Mesh(path)
            return load_serial(self.serial_mesh, _load_fct, ext_format='xml',
                               scratch_dir=scratch_dir)

        elif data_name == 'rmf':
            import fenics as fn

            def _load_fct(path):
                assert mesh, 'Need to specify a mesh on which to generate the region marker function'
                data = fn.MeshFunction('size_t', mesh, mesh.topology().dim())
                fn.File(path) >> data
                return data
            return load_serial(self.serial_region_marker, _load_fct, ext_format='xml',
                               scratch_dir=scratch_dir)

        else:
            raise ValueError(str(data_name) + ' was not a valid data_name.')

    def write_fcstd(self, file_path=None):
        """Write geometry to a fcstd file.

        Returns the fcstd file path.
        """
        if file_path is None:
            file_path = '_'.join([item[0:4].replace(' ', '_') for item in self.build_order]) + '.fcstd'
        write_deserialised(self.serial_fcdoc, file_path)
        return file_path

    # TODO: Redundant? self.fenics_ids appears to be identical to the mapping returned here
    def get_names_to_region_ids(self):
        mapping = {name: i + 2 for i, name in enumerate(self.build_order)}
        mapping[Geo3DData.EXTERIOR_BC_NAME] = 1
        return mapping

    def get_region_ids(self):
        return self.get_region_ids_to_names().keys()

    def get_region_ids_to_names(self):
        return {id: name for name, id in self.get_names_to_region_ids().items()}

    def get_names_to_default_ns(self):
        return {name: part.ns for name, part in self.parts.items() if part.ns is not None}

    def get_names_to_default_phi_nl(self):
        return {name: part.ds for name, part in self.parts.items() if part.ds is not None}

    def get_names_to_default_phi_nl_and_ds(self):
        result = {}
        for name in self.parts:
            if self.parts[name].phi_nl is not None:
                result[name] = {}
                result[name]["phi_nl"] = self.parts[name].phi_nl

            if self.parts[name].ds is not None:
                if name not in result:
                    raise ValueError("both phi_nl and ds must be specified together")
                result[name]["ds"] = self.parts[name].ds
            else:
                if name in result:
                    raise ValueError("both phi_nl and ds must be specified together")

        return result

    def get_names_to_default_ds(self):
        return {name: part.phi_nl for name, part in self.parts.items() if part.phi_nl is not None}

    def get_names_to_default_bcs(self):
        return {name: part.boundary_condition for name, part in self.parts.items() if
                part.boundary_condition is not None}

    def get_names_to_default_dirichlet_bcs(self):
        return {name: part.boundary_condition["voltage"] for name, part in self.parts.items() if
                part.boundary_condition is not None and "dirichlet" in part.boundary_condition}

    def get_names_to_default_neumann_bcs(self):
        return {name: part.boundary_condition["neumann"] for name, part in self.parts.items() if
                part.boundary_condition is not None and "neumann" in part.boundary_condition}

    # def add_exterior_boundary_condition(self, value):
    #     self.exterior_boundary_condition_value = value
    #
    # def add_exterior_neumann_boundary_condition(self, value):
    #     self.exterior_neumann_boundary_condition_value = value

    # def get_names_to_neumann_bc_values(self):
    #     results = {}
    #     for part, data in self.parts.items():
    #         if data.boundary_condition and "neumann" in data.boundary_condition:
    #             results[part] = data.boundary_condition["neumann"]
    #
    #     if self.exterior_neumann_boundary_condition_value is not None:
    #         results[Geo3DData.EXTERIOR_BC_NAME] = self.exterior_neumann_boundary_condition_value
    #
    #         # try:
    #         #     results[part] = data.boundary_condition["voltage"]
    #         # except (KeyError, TypeError) as e:
    #         #     pass
    #     return results
    #
    #
    # def get_names_to_dirichlet_bc_values(self):
    #     results = {}
    #     for part, data in self.parts.items():
    #         if data.boundary_condition and "voltage" in data.boundary_condition:
    #             results[part] = data.boundary_condition["voltage"]
    #
    #     if self.exterior_boundary_condition_value is not None:
    #         results[Geo3DData.EXTERIOR_BC_NAME] = self.exterior_boundary_condition_value
    #
    #         # try:
    #         #     results[part] = data.boundary_condition["voltage"]
    #         # except (KeyError, TypeError) as e:
    #         #     pass
    #     return results
