from shapely.geometry import LinearRing, LineString, MultiLineString, Polygon
from shapely.ops import unary_union
from typing import List, Optional, Sequence
import numpy as np
from matplotlib.axes import Axes
import matplotlib._color_data as mcd
from .geo_data_base import GeoData


class Geo2DData(GeoData):
    """Class for holding a 2D geometry specification. This class holds two main dicts:
        - parts is a dictionary of shapely Polygon objects
        - edges is a dictionary of shapely LineString objects

    Parts are intended to be 2D domains, while edges are used for setting boundary
    conditions and surface conditions.

    Parameters
    ----------
    lunit : str
        Length unit (Default value = 'nm')

    """

    def __init__(self, lunit="nm"):
        super().__init__(lunit)
        self.edges = {}

    def add_part(self, part_name: str, part: Polygon, overwrite: bool = False):
        """Add a part to this geometry.

        Parameters
        ----------
        part_name : str
            Name of the part to create
        part : Polygon
            Polygon object from shapely.geometry. This must be a valid Polygon.
        overwrite : bool
            Should we allow this to overwrite? (Default value = False)
        Returns
        -------
        None
        """
        if not part.is_valid:
            raise ValueError(f"Part {part_name} is not a valid polygon.")
        if (part_name in self.parts) and (not overwrite):
            raise ValueError(f"Attempted to overwrite the part {part_name}.")
        else:
            self.parts[part_name] = part
            self.build_order += [part_name]

    def remove_part(self, part_name: str, ignore_if_absent: bool = False):
        """Remove a part from this geometry.

        Parameters
        ----------
        part_name : str
            Name of part to remove.
        ignore_if_absent : bool
            Should we ignore an attempted removal if the part name
            is not found? (Default value = False)
        Returns
        -------
        None
        """
        if part_name in self.parts:
            del self.parts[part_name]
            self.build_order.remove(part_name)
        elif not ignore_if_absent:
            raise ValueError(
                f"Attempted to remove the part {part_name}, which doesn't exist."
            )

    def add_edge(self, edge_name: str, edge: LineString, overwrite: bool = False):
        """Add an edge to this geometry.

        Parameters
        ----------
        edge_name : str
            : Name of the edge to create
        edge : LineString
            LineString object from shapely.geometry.
        overwrite : bool
            Should we allow this to overwrite? (Default value = False)
        Returns
        -------
        None
        """
        if (edge_name in self.edges) and (not overwrite):
            raise ValueError(f"Attempted to overwrite the edge {edge_name}.")
        else:
            self.edges[edge_name] = edge
            self.build_order += [edge_name]

    def remove_edge(self, edge_name: str, ignore_if_absent: bool = False):
        """Remove an edge from this geometry.

        Parameters
        ----------
        edge_name : str
            Name of part to remove.
        ignore_if_absent : bool
            Should we ignore an attempted removal if the part name
            is not found? (Default value = False)
        Returns
        -------
        None
        """
        if edge_name in self.edges:
            del self.edges[edge_name]
            self.build_order.remove(edge_name)
        elif not ignore_if_absent:
            raise ValueError(
                f"Attempted to remove the edge {edge_name}, which doesn't exist."
            )

    def compute_bb(self) -> List[float]:
        """Computes the bounding box of all of the parts and edges in the geometry.

        Returns
        -------
        List of [min_x, max_x, min_y, max_y].
        """
        all_shapes = list(self.parts.values()) + list(self.edges.values())
        bbox_vertices = unary_union(all_shapes).envelope.exterior.coords.xy
        min_x = min(bbox_vertices[0])
        max_x = max(bbox_vertices[0])
        min_y = min(bbox_vertices[1])
        max_y = max(bbox_vertices[1])
        return [min_x, max_x, min_y, max_y]

    def part_build_order(self) -> List[str]:
        """Returns the build order restricted to parts.

        Parameters
        ----------
        Returns
        -------
        build order restricted to parts.
        """
        priority = []
        for geo_item in self.build_order:
            if geo_item in self.parts:
                priority += [geo_item]
        return priority

    def part_coord_list(self, part_name: str) -> List:
        """Get the list of vertex coordinates for a part

        Parameters
        ----------
        part_name : str
            Name of the part
        Returns
        -------
        coord_list
        """
        # Note that in shapely, the first coord is repeated at the end, which we trim off:
        coord_list = list(np.array(self.parts[part_name].exterior.coords.xy).T)[:-1]
        return coord_list

    def edge_coord_list(self, edge_name: str) -> List:
        """Get the list of vertex coordinates for an edge.

        Parameters
        ----------
        edge_name : str
            Name of the edge.
        Returns
        -------
        coord_list
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
        """ Plots the 2d geometry

        Parameters
        ----------
        parts_to_exclude : Sequence[str]
            Part/edge names that won't be plotted (Default value = [])
        line_width : float
            Thickness of lines (only for edge lines). (Default value = 20.0)
        ax : Optional[Axes]
            You can pass in a matplotlib axes to plot in. If it's None, a new
            figure with its corresponding axes will be created
            (Default value = None)
        colors : Sequence[str]
            Colors to use for plotting the parts and edges
            (Default value = list(mcd.XKCD_COLORS.values()))
        Returns
        -------
        Axes object.

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
