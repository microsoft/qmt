import numpy as np


class PropertyMap(object):
    """Map points in the simulation domain to properties of parts containing the points.

    :param PartMap part_map: Mapper from spatial location to part identifier.
    :param callable prop_map: Map from part identifier to a property value.
    """

    def __init__(self, part_map, prop_map):
        self.partMap = part_map
        self.propMap = prop_map

    def get_part(self, x):
        """Find the part(s) containing one or more points.

        :param x: Coordinate vector or array of coordinate vectors.
        :return: Part identifier (if x is a single coordinate vector); or array of part identifiers, of the same shape as x except for the last axis corresponding to coordinate vector extent.
        """
        return self.partMap(x)

    def __call__(self, x):
        """Do the mapping.

        :param x: Coordinate vector or array of coordinate vectors.
        :return: Property of the part(s) containing `x`, of the same shape as `x` except for the last axis corresponding to coordinate vector extent.
        """
        parts = self.get_part(x)
        if np.isscalar(parts):
            return self.propMap(parts)

        unique_parts = set(np.asanyarray(parts).flat)
        unique_props = [self.propMap(p) for p in unique_parts]
        obj_types = [type(p) for p in unique_props]
        if obj_types[0] is str:
            assert all(t is str for t in obj_types)
            obj_type = object
        else:
            obj_type = np.result_type(*obj_types)
        result = np.empty(np.shape(parts), dtype=obj_type)
        for part, prop in zip(unique_parts, unique_props):
            result[parts == part] = prop
        return result


class MaterialPropertyMap(PropertyMap):
    """Map points in the simulation domain to material properties of parts containing the points.

    :param PartMap part_map: Function that takes a spatial location and maps it to a part identifier.
    :param dict part_materials: Dict mapping from part identifier to a material name.
    :param qmt.Materials mat_lib: Materials library used to look up the material properties.
    :param str prop_name: Name of the material property to be retrieved for each part.
    :param eunit: Energy unit, passed to `mat_lib.find()`.
    :param fill_value: Value to be filled in places where there is no part or the part does not have a material or the material does not have the property `prop_name`. The default behavior `fill_value='raise'` is to raise a KeyError in these cases.
    """

    def __init__(
        self,
        part_map,
        part_materials,
        mat_lib,
        prop_name,
        eunit=None,
        fill_value="raise",
    ):
        self.fillValue = fill_value
        self.materialsDict = dict(
            (p, mat_lib.find(m, eunit)) for p, m in part_materials.items()
        )

        self.partProps = {}
        for p, mat in self.materialsDict.items():
            try:
                if prop_name == "conductionBandMinimum":
                    self.partProps[p] = mat_lib.conduction_band_minimum(mat)
                elif prop_name == "valenceBandMaximum":
                    self.partProps[p] = mat_lib.valence_band_maximum(mat)
                elif prop_name == "lightHoleMass":
                    self.partProps[p] = mat.hole_mass("light", "dos")
                elif prop_name == "heavyHoleMass":
                    self.partProps[p] = mat.hole_mass("heavy", "dos")
                elif prop_name == "dosHoleMass":
                    self.partProps[p] = mat.hole_mass("dos", "dos")
                else:
                    self.partProps[p] = mat[prop_name]
            except KeyError:
                pass

        def prop_map(part):
            try:
                return self.partProps[part]
            except KeyError:
                if self.fillValue == "raise":
                    raise
                return self.fillValue

        super(MaterialPropertyMap, self).__init__(part_map, prop_map)
