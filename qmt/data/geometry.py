# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

"""Geometry data classes."""

import numpy as np
from shapely.ops import unary_union
from shapely.geometry import LinearRing, LineString, MultiLineString, Polygon
from itertools import chain, combinations
from typing import Optional, Sequence, Tuple
import FreeCAD
import Part
from FreeCAD import Base
import matplotlib._color_data as mcd
from qmt.materials import Materials
from .data_utils import load_serial, store_serial, write_deserialised
from matplotlib.axes import Axes


class Geo2DData(object):
    """
    Class for holding a 2D geometry specification. This class holds two main dicts:
        - parts is a dictionary of shapely Polygon objects
        - edges is a dictionary of shapely LineString objects

    Parts are intended to be 2D domains, while edges are used for setting boundary
    conditions and surface conditions.
    """

    def __init__(self, lunit="nm"):
        self.parts = {}
        self.edges = {}
        self.build_order = []
        self.lunit = lunit

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
                    "Attempted to remove the part "
                    + part_name
                    + ", which doesn't exist."
                )
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
                    "Attempted to remove the edge "
                    + edge_name
                    + ", which doesn't exist."
                )
            else:
                pass

    def compute_bb(self):
        """
        Computes the bounding box of all of the parts and edges in the geometry.

        :return bb_list: List of [min_x,max_x,min_y,max_y]
        """
        all_shapes = list(self.parts.values()) + list(self.edges.values())
        bbox_vertices = unary_union(all_shapes).envelope.exterior.coords.xy
        min_x = min(bbox_vertices[0])
        max_x = max(bbox_vertices[0])
        min_y = min(bbox_vertices[1])
        max_y = max(bbox_vertices[1])
        return [min_x, max_x, min_y, max_y]

    def part_build_order(self):
        """
        Returns the build order restricted to parts.

        :return build_order: build order restricted to parts.
        """
        priority = []
        for geo_item in self.build_order:
            if geo_item in self.parts:
                priority += [geo_item]
        return priority

    def part_coord_list(self, part_name):
        """
        Get the list of vertex coordinates for a part

        :param str part_name: Name of the part
        :return list coord_list: List of coordinates of the vertices of the part.
        """
        # Note that in shapely, the first coord is repeated at the end, which we trim off:
        coord_list = list(np.array(self.parts[part_name].exterior.coords.xy).T)[:-1]
        return coord_list

    def edge_coord_list(self, edge_name):
        """
        Get the list of vertex coordinates for an edge.

        :param str edge_name: Name of the edge.
        :return list coord_list: List of the coordinates of the edge.
        """
        coord_list = list(np.array(self.edges[edge_name].coords.xy).T)[:]
        return coord_list

    def plot(
        self,
        parts_to_exclude: Sequence[str] = [],
        line_width: float = 20.0,
        ax: Optional[Axes] = None,
        colors: Sequence = list(mcd.XKCD_COLORS.values()),
    ) -> Axes:
        """
        Plots the 2d geometry
        :param parts_to_exclude: Part/edge names that won't be plotted
        :param line_width: Thickness of lines (only for edge lines)
        :param ax: You can pass in a matplotlib axes to plot in. If it's None, a new
            figure with its corresponding axes will be created
        :param subplot_args: Tuple of args and kwargs to pass to add_subplot
        :param colors: Colors to use for plotting the parts and edges
        :return:
        """
        from matplotlib import pyplot as plt
        import descartes

        if not ax:
            ax = plt.figure().gca()
        pn = 0
        for part_name, part in self.edges.items():
            if part_name in parts_to_exclude:
                continue
            if len(part.coords) == 2:
                coords = np.asarray(part.coords)
                vec = np.asarray(coords[0]) - np.asarray(coords[1])
                vec /= np.linalg.norm(vec)
                perp_vec = np.array([-vec[1], vec[0]])
                half_width = line_width / 2
                part1 = LineString(
                    [
                        coords[0] + half_width * perp_vec,
                        coords[1] + half_width * perp_vec,
                        coords[1] - half_width * perp_vec,
                        coords[0] - half_width * perp_vec,
                    ]
                )
            else:
                part1 = part
            pgn = Polygon(LinearRing(part1))
            patch = descartes.PolygonPatch(pgn, fc=colors[pn].upper(), label=part_name)
            ax.add_patch(patch)

            plt.text(
                list(*part.representative_point().coords)[0],
                list(*part.representative_point().coords)[1],
                part_name,
                ha="center",
                va="center",
            )
            pn += 1

        for part_name, part in self.parts.items():
            if part_name in parts_to_exclude:
                continue
            patch = descartes.PolygonPatch(part, fc=colors[pn].upper(), label=part_name)
            ax.add_patch(patch)
            plt.text(
                list(*part.representative_point().coords)[0],
                list(*part.representative_point().coords)[1],
                part_name,
                ha="center",
                va="center",
                size=14,
            )
            pn += 1
        # Set axis to auto. The user can change this later if he wishes
        ax.axis("auto")
        return ax


class Geo3DData(object):
    """
    Class for a 3D geometry specification. It holds:
        - parts is a dict of Part3D objects, keyed by the label of each Part3D object.
        - build_order is a list of strings indicating the construction order.
    """

    EXTERIOR_BC_NAME = "exterior"

    def __init__(self):
        self.build_order = []
        self.parts = {}  # dict of parts in this geometry
        self.xsecs = {}  # dict of cross-sections in this geometry
        self.serial_fcdoc = None  # serialized FreeCAD document for this geometry
        self.mesh_verts = None  # numpy array corresponding to the mesh vertices
        self.mesh_tets = (
            None
        )  # numpy array; each row contains the vertex indices in one tet
        self.mesh_regions = (
            None
        )  # 1D array; each entry is the region ID of the corresponding tet
        self.mesh_id_dict = None  # dictionary with part name keys mapping to region IDs
        self.virtual_mesh_regions = (
            None
        )  # Dict with 1D arrays; each entry specifies what tets belong to virtual region
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
                    "Attempted to remove the part "
                    + part_name
                    + ", which doesn't exist."
                )
            else:
                pass

    def add_xsec(self, xsec_name, polygons, axis=(1.0, 0.0, 0.0), distance=0.0):
        """
        Make a cross-section of the geometry perpendicular to the axis at a given distance from the origin.
        :param str xsec_name: a strong giving the name for the cross section.
        :param dict polygons: dict conrresponding to the cross-section polygons.
        :param tuple axis: Tuple defining the axis that defines the normal of the cross section.
        :param float distance: Distance along the axis used to set the cross section.
        """
        self.xsecs[xsec_name] = {
            "axis": axis,
            "distance": distance,
            "polygons": polygons,
        }

    def set_data(self, data_name, data, scratch_dir=None):
        """
        Set data to a serial format that is easily portable.

        :param str data_name:  "fcdoc" freeCAD document \
                               "mesh"  fenics mesh \
                               "rmf"   fenics region marker function
        :param data:           The corresponding data that we would like to set.
        :param scratch_dir:    Optional existing temporary (fast) storage location.
        """
        if data_name == "fcdoc":

            def _save_fct(doc, path):
                doc.saveAs(path)

            self.serial_fcdoc = store_serial(
                data, _save_fct, "fcstd", scratch_dir=scratch_dir
            )

        elif data_name == "mesh" or data_name == "rmf":
            import fenics as fn

            def _save_fct(data, path):
                fn.File(path) << data

            if data_name == "mesh":
                self.serial_mesh = store_serial(
                    data, _save_fct, "xml", scratch_dir=scratch_dir
                )
            if data_name == "rmf":
                self.serial_region_marker = store_serial(
                    data, _save_fct, "xml", scratch_dir=scratch_dir
                )

        else:
            raise ValueError(str(data_name) + " was not a valid data_name.")

    def get_data(self, data_name, mesh=None, scratch_dir=None):
        """
        Get data from stored serial format.

        :param str data_name:  "fcdoc" freeCAD document.
        :param scratch_dir:    Optional existing temporary (fast) storage location.
        :return data:          The freeCAD document or fenics object that was stored.
        """
        if data_name == "fcdoc":

            def _load_fct(path):
                doc = FreeCAD.newDocument("instance")
                FreeCAD.setActiveDocument("instance")
                doc.load(path)
                return doc

            return load_serial(self.serial_fcdoc, _load_fct, scratch_dir=scratch_dir)
        else:
            raise ValueError(str(data_name) + " was not a valid data_name.")

    def write_fcstd(self, file_path=None):
        """Write geometry to a fcstd file.

        Returns the fcstd file path.
        """
        if file_path is None:
            file_path = (
                "_".join([item[0:4].replace(" ", "_") for item in self.build_order])
                + ".fcstd"
            )
        write_deserialised(self.serial_fcdoc, file_path)
        return file_path

    def xsec_to_2d(self, xsec_name: str, lunit: Optional[str] = None) -> Geo2DData:
        """
        Generates a Geo2DData from a cross section
        :param xsec_name: Name of the cross section
        :return: Geo2DData object
        """
        # Get our new coordinates
        # This construction ensures that y_new (the first axis in our new 2d coodinate
        # system) is always aligned (by projection) to one of the old axes, prefering
        # x, then y, then z
        x_new = np.array(self.xsecs[xsec_name]["axis"])
        y_new = np.array([0.0, 0, 0])
        axis_ind = -1
        while not np.any(y_new):
            axis_ind += 1
            y_new[axis_ind] = 1
            y_new -= y_new.dot(x_new) * x_new
        y_new /= np.linalg.norm(y_new)
        z_new = np.cross(x_new, y_new)

        def _project(vec):
            """Projects a 3D vector into our 2D cross section plane"""
            vec = vec - x_new * self.xsecs[xsec_name]["distance"]
            return [vec.dot(y_new), vec.dot(z_new)]

        def _inverse_project(vec):
            """Inverse of _project"""
            return (
                x_new * self.xsecs[xsec_name]["distance"]
                + vec[0] * y_new
                + vec[1] * z_new
            )

        part_polygons = {}
        virtual_part_polygons = {}
        # part_polygons is a dictionary of part_name to polygons. virtual_part_polygons
        # is the same for virtual parts
        for part_name in self.build_order:
            polygons = []
            for name, points in self.xsecs[xsec_name]["polygons"].items():
                if name.startswith(f"{part_name}_"):
                    poly = Polygon(map(_project, points))
                    # we add a name to the polygon so we can reference it easier later
                    poly.name = name
                    polygons.append(poly)
            if polygons:
                if self.parts[part_name].domain_type == "virtual":
                    virtual_part_polygons[part_name] = polygons
                else:
                    part_polygons[part_name] = polygons

        def _build_containment_graph(poly_list):
            """
            Given a list of polygons, build a directed graph where edge A -> B means
            A contains B. This intentionally does not include nested containment. Which
            means if A contains B and B contains C, we will only get the edges A -> B
            and B -> C, not A -> C
            """
            poly_by_area = sorted(poly_list, key=lambda p: p.area)

            # graph["poly_name"] is a list of polygons that poly_name contains
            graph = {poly.name: [] for poly in poly_list}

            for i, poly in enumerate(poly_by_area):
                # Find the smallest polygon that contains poly (if any), and add it to
                # the graph
                for bigger_poly in poly_by_area[i + 1 :]:
                    if bigger_poly.contains(poly):
                        graph[bigger_poly.name].append(poly)
                        break
            return graph

        def _is_inside(poly, part):
            """
            Given a polygon, find a point inside of it, and then check if that point is
            in the (3D) part
            """
            # Find the midpoint in x, then find the intersections with the polygon on
            # that vertical line. Then find the midpoint in y along the first
            # intersection line (if there're multiple)
            min_x, min_y, max_x, max_y = poly.bounds
            x = (min_x + max_x) / 2
            x_line = LineString([(x, min_y), (x, max_y)])
            intersec = x_line.intersection(poly)
            if type(intersec) == MultiLineString:
                intersec = intersec[0]
            x_line_intercept_min, x_line_intercept_max = intersec.xy[1].tolist()
            y = (x_line_intercept_min + x_line_intercept_max) / 2

            # Get 3D coordinates and check if it's in the freecad shape
            x, y, z = _inverse_project([x, y])
            freecad_solid = Part.Solid(
                FreeCAD.ActiveDocument.getObject(part.built_fc_name).Shape
            )
            return freecad_solid.isInside(Base.Vector(x, y, z), 1e-5, True)

        # Let's deal with the physical domains first, which can have cavities
        geo_2d = Geo2DData()
        self.get_data("fcdoc")  # The document name is "instance"
        for name, poly_list in part_polygons.items():
            cont_graph = _build_containment_graph(poly_list)
            polys_to_add = []
            # For each polygon (in each part), we subtract from it all interior polygons
            # And then check if what remains is inside the part or not (it could be a
            # cavity). We add it if it's not a cavity
            for poly in poly_list:
                for interior_poly in cont_graph[poly.name]:
                    poly = poly.difference(interior_poly)
                if _is_inside(poly, self.parts[name]):
                    polys_to_add.append(poly)
            if not polys_to_add:
                continue
            if len(polys_to_add) == 1:
                geo_2d.add_part(name, polys_to_add[0])
                continue
            for i, poly in enumerate(polys_to_add):
                geo_2d.add_part(f"{name}_{i}", poly)

        # Now we deal with the virtual parts, which are just added as is
        for name, poly_list in virtual_part_polygons.items():
            if len(poly_list) == 1:
                geo_2d.add_part(name, poly_list[0])
                continue
            for i, poly in enumerate(poly_list):
                geo_2d.add_part(f"{name}_{i}", poly)

        geo_2d.lunit = lunit
        # Clean up freecad document
        FreeCAD.closeDocument("instance")
        return geo_2d


class Part3DData(object):
    """
    Create a 3D geometric part.

    :param str label: The descriptive name of this new part.
    :param str fc_name: The name of the 2D/3D freeCAD object that this is built from. Note that if the label used for
        the 3D part is the same as the freeCAD label, and that label is unique, None may be used here as a shortcut.
    :param str directive: The freeCAD directive is used to construct this part.
        Valid options for this are:

        - extrude -- simple extrusion
        - wire -- hexagonal nanowire about a polyline
        - wire_shell -- shell coating a specified nanowire
        - sag -- SAG structure
        - lithography -- masked layer deposited on top
        - 3d_shape -- just take the 3D shape directly
    :param str domain_type: The type of domain this part represents. Valid options are:

        - semiconductor -- region permitted to self-consistently accumulate
        - metal_gate -- an electrode
        - virtual -- a part just used for selection (ignores material)
        - dielectric -- no charge accumulation allowed
    :param str material: The material of the resulting part.
    :param float z0: The starting z coordinate. Required for extrude, wire,
        SAG, and lithography directives.
    :param float thickness: The total thickness. Required for all directives.
        On wireShell, this is interpreted as the layer thickness.
    :param Part3DData target_wire: Target wire directive for a coating directive.
    :param list shell_verts: Vertices to use when rendering the coating. Required
        for the shell directive.
    :param str depo_mode: 'depo' or 'etch' defines the positive or negative mask for the
        deposition of a wire coating.
    :param float z_middle: The location for the "flare out" of the SAG directive.
    :param float t_in: The lateral distance from the 2D profile to the edge of the top bevel
        for the SAG directive.
    :param float t_out: The lateral distance from the 2D profile to the furthest "flare out"
        location for the SAG directive.
    :param int layer_num: The layer number used by the lithography directive. Lower numbers
        go down first, with higher numbers deposited last.
    :param list litho_base: The base partNames to use for the lithography directive.
        For multi-step lithography, the bases are just all merged,
        so there is no need to list this more than once.
    :param float mesh_max_size: The maximum allowable mesh size for this part, in microns.
    :param float mesh_min_size: The minimum allowable mesh size for this part, in microns.
    :param float mesh_growth_rate: The maximum allowable mesh growth rate for this part.
    :param tuple mesh_scale_vector: 3D list with scaling factors for the mesh in
        x, y, z direction.
    :param dict boundary_condition: One or more boundary conditions, if applicable, of
        the form of a type -> value mapping. For example, this could be {'voltage':1.0} or,
        more explicitly, {'voltage': {'type': 'dirichlet', 'value': 1.0,'unit': 'V'}}.
        Assumed by FEniCS solvers to be in the form {"voltage":1.0},
        and the value given is taken to be in meV.
    :param list subtract_list: A list of partNames that should be subtracted from the current
        part when forming the final 3D objects. This subtraction is
        carried out when boundary
        conditions are set.
    :param float ns: Volume charge density of a part, applicable to semiconductor and
        dielectric parts. The units for this are 1/cm^3.
    :param float phi_nl: The neutral level for interface traps, measured in units of eV above
        the valence band maximum (semiconductor only).
    :param float ds: Density of interface traps; units are 1/(cm^2*eV).
    """

    def __init__(
        self,
        label,
        fc_name,
        directive,
        domain_type=None,
        material=None,
        z0=0,
        thickness=None,
        target_wire=None,
        shell_verts=None,
        depo_mode=None,
        z_middle=None,
        t_in=None,
        t_out=None,
        layer_num=None,
        litho_base=None,
        mesh_max_size=None,
        mesh_min_size=None,
        mesh_growth_rate=None,
        mesh_scale_vector=None,
        boundary_condition=None,
        ns=None,
        phi_nl=None,
        ds=None,
    ):

        # Input validation
        if directive not in [
            "extrude",
            "wire",
            "wire_shell",
            "SAG",
            "lithography",
            "3d_shape",
        ]:
            raise NameError(
                "Error - directive " + directive + " is not a valid directive!"
            )
        if domain_type not in ["semiconductor", "metal_gate", "virtual", "dielectric"]:
            raise NameError("Error - domainType " + domain_type + " not valid!")
        if domain_type not in ["semiconductor", "dielectric"] and ns is not None:
            raise ValueError(
                "Cannot set a volume charge density on a gate or virtual part."
            )

        # Input storage
        self.label = label
        self.fc_name = fc_name
        self.directive = directive
        self.domain_type = domain_type
        self.material = material
        self.z0 = z0
        self.thickness = thickness
        self.target_wire = target_wire
        self.shell_verts = shell_verts
        self.depo_mode = depo_mode
        self.z_middle = z_middle
        self.t_in = t_in
        self.t_out = t_out
        self.layer_num = layer_num
        self.litho_base = [] if litho_base is None else litho_base
        self.mesh_max_size = mesh_max_size
        self.mesh_min_size = mesh_min_size
        self.mesh_growth_rate = mesh_growth_rate
        self.mesh_scale_vector = mesh_scale_vector
        self.boundary_condition = boundary_condition
        self.ns = ns
        self.phi_nl = phi_nl
        self.ds = ds
        self.serial_stp = None  # This gets set on geometry build
        self.serial_stl = None  # This gets set on geometry build
        self.built_fc_name = None  # This gets set on geometry build

    def write_stp(self, file_path=None):
        """Write part geometry to a STEP file.

        Returns the STEP file path.
        """
        if file_path is None:
            file_path = self.label + ".stp"
        write_deserialised(self.serial_stp, file_path)
        return file_path

    def write_stl(self, file_path=None):
        """Write part geometry to a STEP file.

        Returns the STEP file path.
        """
        if file_path is None:
            file_path = self.label + ".stl"
        write_deserialised(self.serial_stl, file_path)
        return file_path
