# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

"""Testing QMT sketch util functions."""


from __future__ import absolute_import, division, print_function
import pytest

import qmt
from qmt.geometry.freecad import FreeCAD
from qmt.geometry.freecad import Part
from qmt.geometry.freecad.sketchUtils import *

vec = FreeCAD.Vector


def test_findSegments(fix_FCDoc, fix_two_cycle_sketch):
    '''Test if segment finding is ordered correctly.'''
    b = (-33, 22, 0)
    d = (22, -11, 0)
    sketch = fix_two_cycle_sketch(b=b, d=d)
    segArr = findSegments(sketch)
    # ~ fix_FCDoc.saveAs("test.fcstd")
    assert (segArr[0][1] == [b]).all()
    assert (segArr[2][1] == [d]).all()


def test_nextSegment(fix_FCDoc, fix_two_cycle_sketch):
    '''Test if nextSegment correctly increments.'''

    # Match the cycle segments
    sketch = fix_two_cycle_sketch()  # trivial case
    segArr = findSegments(sketch)

    assert nextSegment(segArr, 0) == 1  # square cycle
    assert nextSegment(segArr, 1) == 2
    assert nextSegment(segArr, 2) == 3
    assert nextSegment(segArr, 3) == 0

    assert nextSegment(segArr, 4) == 5  # triangle cycle
    assert nextSegment(segArr, 5) == 6
    assert nextSegment(segArr, 6) == 4

    # Test order fixing
    segArr = np.array([[[0, 0, 0], [1, 0, 0]],
                       [[1, 1, 0], [1, 0, 0]],
                       [[1, 1, 0], [0, 0, 0]]])
    assert (segArr[1] == np.array([[1, 1, 0], [1, 0, 0]])).all()
    nextSegment(segArr, 0, fixOrder=False)
    assert (segArr[1] == np.array([[1, 1, 0], [1, 0, 0]])).all()
    nextSegment(segArr, 0, fixOrder=True)
    assert (segArr[1] == np.array([[1, 0, 0], [1, 1, 0]])).all()

    # Ambiguous cycles
    a = (20, 20, 0)
    sketch = fix_two_cycle_sketch(a=a, g=a)
    segArr = findSegments(sketch)
    with pytest.raises(ValueError) as err:
        nextSegment(segArr, 3)
    assert 'Multiple possible paths found' in str(err.value)

    # Open cycles
    segArr = np.array([ [[0,0,0],[1,0,0]] , [[1,0,0],[2,0,0]] ])
    with pytest.raises(ValueError) as err:
        nextSegment(segArr, 1)
    assert 'No paths found' in str(err.value)


def test_findCycle(fix_FCDoc, fix_two_cycle_sketch):
    '''Test cycle ordering.'''
    sketch = fix_two_cycle_sketch()
    segArr = findSegments(sketch)
    ref1 = [0, 1, 2, 3]  # square cycle indices
    ref2 = [4, 5, 6]     # triangular cycle indices
    for i in range(4):
        c = findCycle(segArr, i, range(segArr.shape[0]))  # update starting point
        # ~ print(c)
        assert c == ref1[i:] + ref1[:i]  # advancing rotation
    for i in range(3):
        c = findCycle(segArr, i + 4, range(segArr.shape[0]))
        assert c == ref2[i:] + ref2[:i]


def test_addCycleSketch(fix_FCDoc, fix_two_cycle_sketch):
    '''Test if cycles are correctly added.'''
    b = (-30, 20, 0)
    d = (20, -10, 0)
    sketch = fix_two_cycle_sketch(b=b, d=d)
    segArr, cycles = findEdgeCycles(sketch)
    addCycleSketch('cyclesketch', fix_FCDoc, cycles[0], segArr[0:4])
    segArr = findSegments(fix_FCDoc.cyclesketch)
    assert (segArr[0][1] == [b]).all()
    assert (segArr[2][1] == [d]).all()

    with pytest.raises(ValueError) as err:
        addCycleSketch('cyclesketch', fix_FCDoc, cycles[0], segArr[0:4])
    assert 'already exists' in str(err.value)


def test_addCycleSketch2(fix_FCDoc, fix_two_cycle_sketch):
    '''Test if cycles are correctly added.'''
    b = (-30, 20, 0)
    d = (20, -10, 0)
    sketch = fix_two_cycle_sketch()
    wire = sketch.Shape.Wires[0]
    sketch_new = addCycleSketch2('cyclesketch', wire)

    segArr = findSegments(sketch_new)
    assert (segArr[0][1] == [b]).all()
    assert (segArr[2][1] == [d]).all()

    with pytest.raises(ValueError) as err:
        addCycleSketch2('cyclesketch', wire)
    assert 'already exists' in str(err.value)


def test_addPolyLineSketch(fix_FCDoc):
    '''Test if polylines are correctly added.'''
    pass
    #TODO


def test_findEdgeCycles(fix_FCDoc, fix_two_cycle_sketch):
    '''Test multiple cycle ordering.'''
    sketch = fix_two_cycle_sketch()
    _, cycles = findEdgeCycles(sketch)
    assert cycles[0] == [0, 1, 2, 3]
    assert cycles[1] == [4, 5, 6]


def test_findEdgeCycles2(fix_FCDoc, fix_two_cycle_sketch):
    '''Test multiple cycle ordering.'''
    sketch = fix_two_cycle_sketch()
    com_ref = [(e.CenterOfMass.x, e.CenterOfMass.y, e.CenterOfMass.z)
               for e in [wire.Edges for wire in sketch.Shape.Wires][0]]

    wires = findEdgeCycles2(sketch)
    com = [(e.CenterOfMass.x, e.CenterOfMass.y, e.CenterOfMass.z)
           for e in [wire.Edges for wire in wires][0]]
    assert np.allclose(com, com_ref)


def test_splitSketch(fix_FCDoc, fix_two_cycle_sketch):
    '''Test if multi-cycle sketches are split correctly.'''
    sketch = fix_two_cycle_sketch()

    newsketchL = splitSketch(sketch)
    centers_orig = [e.CenterOfMass for e in sketch.Shape.Edges]
    centers_sq = [e.CenterOfMass for e in newsketchL[0].Shape.Edges]
    centers_tri = [e.CenterOfMass for e in newsketchL[1].Shape.Edges]

    for p in centers_sq:
        assert p in centers_orig and p not in centers_tri
    for p in centers_tri:
        assert p in centers_orig and p not in centers_sq


def test_splitSketch2(fix_FCDoc, fix_two_cycle_sketch, fix_unit_square_sketch):
    '''Test if multi-cycle sketches are split correctly.'''
    sketch = fix_two_cycle_sketch()

    newsketchL = splitSketch2(sketch)
    centers_orig = [e.CenterOfMass for e in sketch.Shape.Edges]
    centers_sq = [e.CenterOfMass for e in newsketchL[0].Shape.Edges]
    centers_tri = [e.CenterOfMass for e in newsketchL[1].Shape.Edges]

    for p in centers_sq:
        assert p in centers_orig and p not in centers_tri
    for p in centers_tri:
        assert p in centers_orig and p not in centers_sq
    # ~ fix_FCDoc.saveAs("test.fcstd")

    sketch = fix_unit_square_sketch()
    assert sketch.Content == splitSketch2(sketch).Content


def test_extendSketch(fix_FCDoc):
    '''Test unconnected sketch extension, all cases.'''
    sketch = fix_FCDoc.addObject('Sketcher::SketchObject', 'Sketch')
    geoList = []
    geoList.append(Part.LineSegment(vec(0,0,0),vec(0,2,0)))
    geoList.append(Part.LineSegment(vec(0,2,0),vec(-2,2,0)))
    sketch.addGeometry(geoList, False)
    fix_FCDoc.recompute()
    ext = extendSketch(sketch, 1)
    assert ext.Shape.Vertexes[0].Point == vec(0,-1,0)
    assert ext.Shape.Vertexes[2].Point == vec(-3,2,0)

    deepRemove(sketch)
    deepRemove(ext)
    sketch = fix_FCDoc.addObject('Sketcher::SketchObject', 'Sketch')
    geoList = []
    geoList.append(Part.LineSegment(vec(0,0,0),vec(2,0,0)))
    geoList.append(Part.LineSegment(vec(2,0,0),vec(2,-2,0)))
    sketch.addGeometry(geoList, False)
    fix_FCDoc.recompute()
    ext = extendSketch(sketch, 1)
    assert ext.Shape.Length == 2 + sketch.Shape.Length


def test_makeIntoSketch(fix_FCDoc):
    #TODO
    pass

def test_draftOffset(fix_FCDoc):
    '''Check if draft offset resizes the object. TODO: edge cases'''
    pl = FreeCAD.Placement()
    pl.Base = vec(1, 1, 0)
    draft = Draft.makeRectangle(length=2, height=2, placement=pl, face=False, support=None)
    draft2 = draftOffset(draft, 20)
    assert draft.Height.Value + 40 == draft2.Height.Value
