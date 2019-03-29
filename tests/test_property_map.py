import numpy as np

from qmt.geometry import PropertyMap, MaterialPropertyMap
from qmt.materials import Materials


class DummyPartMap:
    def __init__(self, part_ids):
        assert len(part_ids) == 2
        self.partIds = part_ids

    def __call__(self, x):
        assert np.ndim(x) >= 1
        x = np.asanyarray(x)
        if np.ndim(x) == 1:
            return self.partIds[x[0] > 0]
        else:
            return np.where(x[..., 0] > 0, self.partIds[1], self.partIds[0])


def test_property_map():
    int_map = DummyPartMap([0, 1])
    str_map = DummyPartMap(["part1", "part2"])

    prop_map1 = PropertyMap(int_map, np.vectorize(lambda p: "yes" if p > 0 else "no"))
    assert prop_map1.get_part((1.0, 2.0)) == 1
    assert np.all(prop_map1.get_part(-np.ones((2, 3))) == 0)
    assert prop_map1((1.0, 2.0)) == "yes"
    assert np.all(prop_map1(-np.ones((2, 3))) == "no")

    props = {"part1": "yes", "part2": "no"}
    prop_map2 = PropertyMap(str_map, np.vectorize(lambda p: props[p]))
    assert prop_map2.get_part((1.0, 2.0)) == "part2"
    assert np.all(prop_map2.get_part(-np.ones((2, 3))) == "part1")
    assert prop_map1((1.0, 2.0)) == "yes"
    assert np.all(prop_map1(-np.ones((2, 3))) == "no")


def test_property_map_nonuniform_types():
    str_map = DummyPartMap(["part1", "part2"])
    props = {"part1": 1, "part2": 1.5}
    prop_map = PropertyMap(str_map, lambda p: props[p])
    assert prop_map((1.0, 2.0)) == 1.5
    assert np.all(prop_map(np.ones((2, 3))) == 1.5)
    assert np.all(prop_map(-np.ones((2, 3))) == 1)


def test_materials_property_map():
    int_map = DummyPartMap([0, 1])
    str_map = DummyPartMap(["part1", "part2"])
    part_materials1 = {0: "InAs", 1: "GaSb"}
    part_materials2 = {"part1": "InAs", "part2": "Al"}
    mat_lib = Materials(matDict={})
    mat_lib.add_material(
        "InAs",
        "semi",
        electronMass=0.026,
        directBandGap=417.0,
        valenceBandOffset=-590.0,
    )
    mat_lib.add_material(
        "GaSb", "semi", electronMass=0.039, directBandGap=812.0, valenceBandOffset=-30.0
    )
    mat_lib.add_material("Al", "metal", workFunction=4280.0)

    prop_map1 = MaterialPropertyMap(int_map, part_materials1, mat_lib, "electronMass")
    assert prop_map1.get_part((1.0, 2.0)) == 1
    assert np.all(prop_map1.get_part(-np.ones((2, 3))) == 0)
    assert prop_map1((1.0, 2.0)) == mat_lib["GaSb"]["electronMass"]
    assert np.all(prop_map1(-np.ones((2, 3))) == mat_lib["InAs"]["electronMass"])

    prop_map2 = MaterialPropertyMap(
        str_map, part_materials2, mat_lib, "directBandGap", eunit="eV", fill_value=0.0
    )
    assert prop_map2.get_part((1.0, 2.0)) == "part2"
    assert np.all(prop_map2.get_part(-np.ones((2, 3))) == "part1")
    assert prop_map2((1.0, 2.0)) == 0.0
    assert np.all(
        prop_map2(-np.ones((2, 3))) == mat_lib.find("InAs", "eV")["directBandGap"]
    )
