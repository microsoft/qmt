"""
Contains the Geo3DData class, which is used to describe a 3D geometry
"""

from qmt.infrastructure import load_serial, store_serial, write_deserialised
from typing import Any, Dict, List, Optional, Tuple
from .part_3d import Geo3DPart
import numpy as np
import FreeCAD
import Part
from FreeCAD import Base
from shapely.geometry import LineString, MultiLineString, Polygon
from .geo_2d_data import Geo2DData
from .geo_data_base import GeoData


class Geo3DData(GeoData):
    """Class for a 3D geometry specification. It holds:
        - parts is a dict of Part3D objects, keyed by the label of each Part3D object
        - build_order is a list of strings indicating the construction order
    """

    def __init__(self, lunit: Optional[str] = None):
        super().__init__(lunit or "nm")
        # dict of cross sections in this geometry
        # A cross section is a dict with axis and distance fields
        # E.g. xsec_dict={"test_xsec": {"axis": (1, 0, 0), "distance": 0}}
        self.xsecs: Dict[str, Dict] = {}
        self.serial_fcdoc: str = None  # serialized FreeCAD document for this geometry

    def add_part(self, part_name: str, part: Geo3DPart, overwrite: bool = False):
        """Add a part to this geometry.
        
        Parameters
        ----------
        part_name : str
            Name of the part to add
        part : Geo3DPart
            Part to add
        overwrite : bool, optional
            Whether we allow this to overwrite existing part, by default False
        """
        # We use : as a special character when a part is cut into multiple parts when
        # taking a cross section
        if ":" in part_name:
            raise ValueError("Cannot use : in part name")

        super().add_part(
            part_name,
            part,
            overwrite,
            lambda p: self.build_order.append(p.label) if p is not None else None,
        )

    def remove_part(self, part_name: str, ignore_if_absent: bool = False):
        """Remove a part from this geometry.
        
        Parameters
        ----------
        part_name : str
            Name of the part to remove
        ignore_if_absent : bool, optional
            Whether we ignore an attempted removal if the part name is not present, by
            default False
        """
        super.remove_part(
            part_name,
            ignore_if_absent,
            lambda p: self.build_order.remove(p) if p is not None else None,
        )

    def add_xsec(
        self,
        xsec_name: str,
        polygons: Dict[str, List[List[float]]],
        axis: Tuple[float, float, float] = (1.0, 0.0, 0.0),
        distance: float = 0.0,
    ):
        """Make a cross-section of the geometry perpendicular to the axis at a given distance from the origin.

        Parameters
        ----------
        xsec_name : str
            a strong giving the name for the cross section.
        polygons : dict
            dict conrresponding to the cross-section polygons.
        axis : tuple
            Tuple defining the axis that defines the normal of the cross section.
            (Default value = (1.0, 0.0, 0.0))
        distance : float
            Distance along the axis used to set the cross section.
        Returns
        -------
        None

        """
        if not np.isclose(np.linalg.norm(axis), 1):
            raise ValueError("Given axis is not a unit vector")

        self.xsecs[xsec_name] = {
            "axis": axis,
            "distance": distance,
            "polygons": polygons,
        }

    def set_data(self, data: Any, scratch_dir: Optional[str] = None):
        """Set data to a serial format that is easily portable.

        Parameters
        ----------
        data :
            The corresponding data that we would like to set.
        scratch_dir : str
            Optional existing temporary (fast) storage location. (Default value = None)
        Returns
        -------
        None
        """

        def _save_fct(doc, path):
            doc.saveAs(path)

        self.serial_fcdoc = store_serial(
            data, _save_fct, "fcstd", scratch_dir=scratch_dir
        )

    def get_data(self, data_name: str, scratch_dir: Optional[str] = None):
        """Get data from stored serial format.

        Parameters
        ----------
        data_name : str
            "fcdoc" freeCAD document.
        scratch_dir : str
            Optional existing temporary (fast) storage location. (Default value = None)
        mesh :
            (Default value = None)
        Returns
        -------
        data
        """
        if data_name == "fcdoc":

            def _load_fct(path):
                doc = FreeCAD.newDocument("instance")
                FreeCAD.setActiveDocument("instance")
                doc.load(path)
                return doc

            return load_serial(self.serial_fcdoc, _load_fct, scratch_dir=scratch_dir)
        else:
            raise ValueError(f"{data_name} was not a valid data_name.")

    def write_fcstd(self, file_path: Optional[str] = None):
        """Write geometry to a fcstd file.

        Returns the fcstd file path.

        Parameters
        ----------
        file_path :
            (Default value = None)
        Returns
        -------
        file_path

        """
        if file_path is None:
            file_path = (
                "_".join([item[0:4].replace(" ", "_") for item in self.build_order])
                + ".fcstd"
            )
        write_deserialised(self.serial_fcdoc, file_path)
        return file_path

    def xsec_to_2d(self, xsec_name: str, lunit: Optional[str] = None) -> Geo2DData:
        """Generates a Geo2DData from a cross section

        Parameters
        ----------
        xsec_name : str
            Name of the cross section
        lunit : Optional[str] :
            (Default value = None)
        Returns
        -------
        None

        """

        # Get our new coordinates
        # This constructions tries to align the new coordinates to our old coordinates
        # In particular, the map from projection axis -> new axes is
        # [1,0,0] -> [0,1,0] [0,0,1]
        # [0,1,0] -> [1,0,0] [0,0,1]
        # [0,0,1] -> [1,0,0] [0,1,0]

        # Find out which axis the projection axis is most closely aligned to
        x_new = np.array(self.xsecs[xsec_name]["axis"])
        ind = np.argmax(np.abs(x_new))
        y_new = np.array([0, 1.0, 0]) if ind == 0 else np.array([1.0, 0, 0])
        y_new -= y_new.dot(x_new) * x_new
        z_new = np.cross(x_new, y_new)
        # Adjust our second axis so that the "height axis" is correctly aligned
        if z_new[2] < 0:
            z_new = -z_new

        def _project(vec):
            """Projects a 3D vector into our 2D cross section plane
            
            Parameters
            ----------
            vec :
            Returns
            -------
            List of projection.

            """
            vec = vec - x_new * self.xsecs[xsec_name]["distance"]
            return [vec.dot(y_new), vec.dot(z_new)]

        def _inverse_project(vec):
            """Inverse of _project
            
            Parameters
            ----------
            vec :
            Returns
            -------
            Float, inverse of _project.

            """
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
                if self.parts[part_name].virtual:
                    virtual_part_polygons[part_name] = polygons
                else:
                    part_polygons[part_name] = polygons

        def _build_containment_graph(poly_list):
            """Given a list of polygons, build a directed graph where edge A -> B means
            A contains B. This intentionally does not include nested containment. Which
            means if A contains B and B contains C, we will only get the edges A -> B
            and B -> C, not A -> C.

            Parameters
            ----------
            poly_list :
            Returns
            -------
            graph

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
            """Given a polygon, find a point inside of it, and then check if that point is
            in the (3D) part

            Parameters
            ----------
            poly :
            part :
            Returns
            -------
            Boolean

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
                geo_2d.add_part(f"{name}:{i}", poly)

        # Now we deal with the virtual parts, which are just added as is
        for name, poly_list in virtual_part_polygons.items():
            if len(poly_list) == 1:
                geo_2d.add_part(name, poly_list[0])
                continue
            for i, poly in enumerate(poly_list):
                geo_2d.add_part(f"{name}:{i}", poly)

        geo_2d.lunit = self.lunit if lunit is None else None
        # Clean up freecad document
        FreeCAD.closeDocument("instance")
        return geo_2d
