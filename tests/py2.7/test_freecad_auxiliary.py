# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

"""Testing FreeCAD helper functions."""


import pytest

from qmt.geometry.freecad.auxiliary import *
from qmt.geometry.freecad.geomUtils import extrude


def test_delete(fix_FCDoc, fix_two_cycle_sketch):
    '''Test direct deletion of objects.'''
    sketch = fix_two_cycle_sketch()
    part = extrude(sketch, 10)
    delete(sketch)
    assert fix_FCDoc.Objects
    delete(part)
    assert not fix_FCDoc.Objects


def test_deepRemove(fix_FCDoc, fix_two_cycle_sketch):
    '''Test deep (recursive) removal by all parameters.'''

    # check input sanitation
    with pytest.raises(RuntimeError) as err:
        deepRemove(None)
    assert 'No object selected' in str(err.value)

    # simple deletion
    sketch = fix_two_cycle_sketch()
    part1 = extrude(sketch, 10)
    deepRemove(part1)
    assert not fix_FCDoc.Objects

    # copied object deletion
    sketch = fix_two_cycle_sketch()
    part1 = extrude(sketch, 10)
    part2 = fix_FCDoc.copyObject(part1, False)
    deepRemove(name=part2.Name)  # part2 refs to sketch from part1
    assert not part1.OutList

    deepRemove(label=part1.Label)
    assert not fix_FCDoc.Objects

    # compound object deletion
    box1 = fix_FCDoc.addObject("Part::Box", "Box1")
    box2 = fix_FCDoc.addObject("Part::Box", "Box2")
    box3 = fix_FCDoc.addObject("Part::Box", "Box3")
    inter1 = fix_FCDoc.addObject("Part::MultiCommon", "inter1")
    inter1.Shapes = [box1, box2, ]
    fix_FCDoc.recompute()
    inter2 = fix_FCDoc.addObject("Part::MultiCommon", "inter2")
    inter2.Shapes = [inter1, box3, ]
    fix_FCDoc.recompute()
    fix_FCDoc.removeObject(box1.Name)  # interjected delete without recompute
    deepRemove(inter2)
    assert not fix_FCDoc.Objects
