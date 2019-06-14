from shapely.geometry import LinearRing, LineString, MultiLineString, Polygon
from shapely.ops import unary_union
from shapely.geometry.collection import GeometryCollection
from typing import List, Optional, Sequence, Union
import numpy as np
from matplotlib.axes import Axes
import matplotlib._color_data as mcd
from .geo_data_base import GeoData
from collections import defaultdict


class Geo2DData(GeoData):
    def __init__(self, lunit: Optional[str] = None):
        """Class for holding a 2D geometry specification. The parts dict can contain
        shapely Polygon or LineString objects. Polygon are intended to be 2D domains,
        while LineString are used for setting boundary conditions and surface
        conditions.
        
        Parameters
        ----------
        lunit : str, optional
            Length unit, by default "nm"

        """
        super().__init__("nm" if lunit is None else lunit)

    def add_part(
        self, part_name: str, part: Union[LineString, Polygon], overwrite: bool = False
    ):
        """Add a part to this geometry.
        
        Parameters
        ----------
        part_name : str
            Name of the part to add
        part : Union[LineString, Polygon]
            Part to add
        overwrite : bool, optional
            Whether we allos this to overwrite existing part, by default False
        
        Raises
        ------
        ValueError
            Part is not a valid Polygon

        """
        if isinstance(part, Polygon) and not part.is_valid:
            raise ValueError(f"Part {part_name} is not a valid polygon.")

        part.virtual = False

        super().add_part(
            part_name,
            part,
            overwrite,
            lambda p: self.build_order.append(part_name) if p is not None else None,
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

    @property
    def polygons(self):
        """Return dictionary of parts that are polygons."""
        return {k: v for k, v in self.parts.items() if isinstance(v, Polygon)}

    @property
    def edges(self):
        """Return dictionary of parts that are lines."""
        return {k: v for k, v in self.parts.items() if isinstance(v, LineString)}

    def compute_bb(self) -> List[float]:
        """Compute the bounding box of all of the parts in the geometry.

        Returns
        -------
        List of [min_x, max_x, min_y, max_y].

        """
        all_shapes = list(self.parts.values())
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
            if geo_item in self.parts and isinstance(self.parts[geo_item], Polygon):
                priority += [geo_item]
        return priority

    def coord_list(self, part_name: str) -> List:
        """Get the list of vertex coordinates for a part

        Parameters
        ----------
        part_name : str
            Name of the part
        Returns
        -------
        coord_list
        """
        part = self.parts[part_name]
        if isinstance(part, Polygon):
            # Note that in shapely, the first coord is repeated at the end, which we
            # trim off:
            return list(np.array(part.exterior.coords.xy).T)[:-1]
        elif isinstance(part, LineString):
            return list(np.array(part.coords.xy).T)[:]

    def crop(
        self,
        x_min: float = None,
        x_max: float = None,
        y_min: float = None,
        y_max: float = None,
    ):
        if x_min is not None and x_max is not None:
            assert x_min < x_max, "x_max must be greater than x_min"
        if y_min is not None and y_max is not None:
            assert y_min < y_max, "y_max must be greater than y_min"
        cropped_geo = Geo2DData(self.lunit)
        x_min_old, x_max_old, y_min_old, y_max_old = self.compute_bb()
        x_min = x_min_old if x_min is None else x_min
        x_max = x_max_old if x_max is None else x_max
        y_min = y_min_old if y_min is None else y_min
        y_max = y_max_old if y_max is None else y_max
        crop_poly = Polygon(
            [[x_min, y_min], [x_min, y_max], [x_max, y_max], [x_max, y_min]]
        )

        ind_count = defaultdict(int)

        for name, part in self.parts.items():
            ind_name = name.split(":")[0] if ":" in name else name
            cropped_part = crop_poly.intersection(part)
            if cropped_part.is_empty:
                continue
            if isinstance(cropped_part, Polygon) or isinstance(
                cropped_part, LineString
            ):
                cropped_geo.add_part(name, cropped_part)
                ind_count[ind_name] += 1
            elif isinstance(cropped_part, GeometryCollection):
                for part in cropped_part:
                    if not (isinstance(part, Polygon) or isinstance(part, LineString)):
                        print(type(part))
                    cropped_geo.add_part(f"{ind_name}:{ind_count[ind_name]}", part)
                    ind_count[ind_name] += 1
            else:
                raise RuntimeError(
                    "Unknown intersection of type ({type(cropped_part)}) encountered "
                    f"during cropping of {name}"
                )
        assert [
            x_min,
            x_max,
            y_min,
            y_max,
        ] == cropped_geo.compute_bb(), "Cropped geometry has wrong bounds"

        return cropped_geo

    def plot(
        self,
        parts_to_exclude: Optional[Sequence[str]] = None,
        line_width: float = None,
        ax: Optional[Axes] = None,
        colors: Optional[Sequence] = None,
    ) -> Axes:
        """ Plots the 2d geometry

        Parameters
        ----------
        parts_to_exclude : Sequence[str]
            Part/edge names that won't be plotted (Default value = None)
        line_width : float
            Thickness of lines (only for edge lines). (Default value = None)
        ax : Optional[Axes]
            You can pass in a matplotlib axes to plot in. If it's None, a new
            figure with its corresponding axes will be created
            (Default value = None)
        colors : Sequence[str]
            Colors to use for plotting the parts
            (Default value = None)
        Returns
        -------
        Axes object.

        """
        from matplotlib import pyplot as plt
        import descartes

        if parts_to_exclude is None:
            parts_to_exclude = []
        if colors is None:
            colors = list(mcd.XKCD_COLORS.values())
        if line_width is None:
            x_min, x_max, y_min, y_max = self.compute_bb()
            width = min(x_max - x_min, y_max - y_min)
            line_width = width / 50
        if ax is None:
            ax = plt.figure().gca()

        pn = 0
        for part_name, part in self.parts.items():
            if part_name in parts_to_exclude:
                continue

            if isinstance(part, LineString):
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
            else:
                pgn = part

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

        # Set axis to auto. The user can change this later if he wishes
        ax.axis("auto")
        return ax
