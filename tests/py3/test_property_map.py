import numpy as np
from qmt.materials import Materials
from qmt.geometry import PropertyMap, MaterialPropertyMap


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
    str_map = DummyPartMap(['part1', 'part2'])

    prop_map1 = PropertyMap(int_map, np.vectorize(lambda p: 'yes' if p > 0 else 'no'))
    assert prop_map1.get_part((1., 2.)) == 1
    assert np.all(prop_map1.get_part(-np.ones((2, 3))) == 0)
    assert prop_map1((1., 2.)) == 'yes'
    assert np.all(prop_map1(-np.ones((2, 3))) == 'no')

    props = {'part1': 'yes', 'part2': 'no'}
    prop_map2 = PropertyMap(str_map, np.vectorize(lambda p: props[p]))
    assert prop_map2.get_part((1., 2.)) == 'part2'
    assert np.all(prop_map2.get_part(-np.ones((2, 3))) == 'part1')
    assert prop_map1((1., 2.)) == 'yes'
    assert np.all(prop_map1(-np.ones((2, 3))) == 'no')


def test_materials_property_map():
    int_map = DummyPartMap([0, 1])
    str_map = DummyPartMap(['part1', 'part2'])
    part_materials1 = {0: 'InAs', 1: 'GaSb'}
    part_materials2 = {'part1': 'InAs', 'part2': 'Al'}
    mat_lib = Materials(matDict={})
    mat_lib.add_material('InAs', 'semi', electronMass=0.026, directBandGap=417.,
                         valenceBandOffset=-590.)
    mat_lib.add_material('GaSb', 'semi', electronMass=.039, directBandGap=812.,
                         valenceBandOffset=-30.)
    mat_lib.add_material('Al', 'metal', workFunction=4280.)

    prop_map1 = MaterialPropertyMap(int_map, part_materials1, mat_lib, 'electronMass')
    assert prop_map1.get_part((1., 2.)) == 1
    assert np.all(prop_map1.get_part(-np.ones((2, 3))) == 0)
    assert prop_map1((1., 2.)) == mat_lib['GaSb']['electronMass']
    assert np.all(prop_map1(-np.ones((2, 3))) == mat_lib['InAs']['electronMass'])

    prop_map2 = MaterialPropertyMap(str_map, part_materials2, mat_lib, 'directBandGap', eunit='eV',
                                    fill_value=0.)
    assert prop_map2.get_part((1., 2.)) == 'part2'
    assert np.all(prop_map2.get_part(-np.ones((2, 3))) == 'part1')
    assert prop_map2((1., 2.)) == 0.
    assert np.all(prop_map2(-np.ones((2, 3))) == mat_lib.find('InAs', 'eV')['directBandGap'])
