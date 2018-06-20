# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

from __future__ import absolute_import, division, print_function
import pytest
import qmt
import FreeCAD
import Part
from qmt.freecad.sketchUtils import *


def setup_function(function):
    global myDoc
    myDoc = FreeCAD.newDocument('testDoc')
    global vec
    vec = FreeCAD.Vector


def teardown_function(function):
    FreeCAD.closeDocument('testDoc')


def manual_testing(function):
    setup_function(function)
    function()
    teardown_function(function)


def aux_two_cycle_sketch( a=( 20, 20, 0), b=(-30, 20, 0), c=(-30,-10, 0), d=( 20,-10, 0),
                          e=( 50, 50, 0), f=( 60, 50, 0), g=( 55, 60, 0) ):
    '''Helper function to drop a simple multi-cycle sketch.
       The segments are carefully ordered into one rectangle and one triangle.
    '''
    # Note: the z-component is zero, as sketches are plane objects.
    #       Adjust orientation with Sketch.Placement(Normal, Rotation)

    sketch = FreeCAD.activeDocument().addObject('Sketcher::SketchObject','Sketch')
    geoList = []
    sketch.addGeometry(Part.LineSegment(vec(*a),vec(*b)),False)
    sketch.addGeometry(Part.LineSegment(vec(*b),vec(*c)),False)
    sketch.addGeometry(Part.LineSegment(vec(*c),vec(*d)),False)
    sketch.addGeometry(Part.LineSegment(vec(*d),vec(*a)),False)
    sketch.addGeometry(Part.LineSegment(vec(*e),vec(*f)),False)
    sketch.addGeometry(Part.LineSegment(vec(*f),vec(*g)),False)
    sketch.addGeometry(Part.LineSegment(vec(*g),vec(*e)),False)
    myDoc.recompute()
    return sketch


def test_delete():
    sketch = aux_two_cycle_sketch()
    part = qmt.freecad.extrude(sketch, 10)
    delete(sketch)
    delete(part)
    assert len(myDoc.Objects) == 0

    sketch = aux_two_cycle_sketch()
    part = qmt.freecad.extrude(sketch, 10)
    part2 = myDoc.copyObject(part, False)
    deepRemove(name=part2.Name)
    assert len(part.OutList) == 0  # part2 steals sketch from part1

def test_deepRemove():
    '''Test deep (recursive) removal by all parameters.'''

    # check input sanitation
    with pytest.raises(RuntimeError) as err:
        deepRemove(None)
    assert 'No object selected' in str(err.value)

    # simple deletion
    sketch = aux_two_cycle_sketch()
    part1 = qmt.freecad.extrude(sketch, 10)
    deepRemove(part1)
    assert len(myDoc.Objects) == 0

    # copied object deletion
    sketch = aux_two_cycle_sketch()
    part1 = qmt.freecad.extrude(sketch, 10)
    part2 = myDoc.copyObject(part1, False)
    deepRemove(name=part2.Name)  # part2 refs to sketch from part1
    assert len(part1.OutList) == 0

    deepRemove(label=part1.Label)
    assert len(myDoc.Objects) == 0

    # compound object deletion
    box1 = myDoc.addObject("Part::Box","Box1")
    box2 = myDoc.addObject("Part::Box","Box2")
    box3 = myDoc.addObject("Part::Box","Box3")
    inter1 = myDoc.addObject("Part::MultiCommon","inter1")
    inter1.Shapes = [box1, box2,]
    myDoc.recompute()
    inter2 = myDoc.addObject("Part::MultiCommon","inter2")
    inter2.Shapes = [inter1, box3,]
    myDoc.recompute()
    myDoc.removeObject(box1.Name) # annoying interjected delete
    deepRemove(inter2)
    assert len(myDoc.Objects) == 0


def test_findSegments():
    '''Test if segment finding is ordered correctly.'''
    b = (-33, 22, 0)
    d = ( 22,-11, 0)
    sketch = aux_two_cycle_sketch(b=b, d=d)
    segArr = findSegments(sketch)
    assert (segArr[0][1] == [b]).all()
    assert (segArr[2][1] == [d]).all()


def test_nextSegment():
    '''Test if nextSegment correctly increments.'''

    # Match the cycle segments
    sketch = aux_two_cycle_sketch()  # trivial case
    segArr = findSegments(sketch)

    assert nextSegment(segArr, 0) == 1 # square cycle
    assert nextSegment(segArr, 1) == 2
    assert nextSegment(segArr, 2) == 3
    assert nextSegment(segArr, 3) == 0

    assert nextSegment(segArr, 4) == 5 # triangle cycle
    assert nextSegment(segArr, 5) == 6
    assert nextSegment(segArr, 6) == 4

    # Test order fixing
    segArr = np.array([ [[0,0,0],[1,0,0]] , [[1,1,0],[1,0,0]] , [[1,1,0],[0,0,0]] ])
    assert ( segArr[1] == np.array([[1,1,0],[1,0,0]]) ).all()
    seg = nextSegment(segArr, 0, fixOrder=False)
    assert ( segArr[1] == np.array([[1,1,0],[1,0,0]]) ).all()
    seg = nextSegment(segArr, 0, fixOrder=True)
    assert ( segArr[1] == np.array([[1,0,0],[1,1,0]]) ).all()

    # Ambiguous cycles
    a=( 20, 20, 0)
    sketch = aux_two_cycle_sketch(a=a, g=a)
    segArr = findSegments(sketch)
    with pytest.raises(ValueError) as err:
        nextSegment(segArr, 3)
    assert 'Multiple possible paths found' in str(err.value)

    # Open cycles
    segArr = np.array([ [[0,0,0],[1,0,0]] , [[1,0,0],[2,0,0]] ])
    with pytest.raises(ValueError) as err:
        nextSegment(segArr, 1)
    assert 'No paths found' in str(err.value)


def test_findCycle():
    '''Test cycle ordering.'''
    sketch = aux_two_cycle_sketch()
    segArr = findSegments(sketch)
    ref1 = [ 0, 1, 2, 3 ]  # square cycle indices
    ref2 = [ 4, 5, 6 ]     # triangular cycle indices
    for i in range(4):
        c = findCycle(segArr, i, range(segArr.shape[0]))  # update starting point
        assert c == ref1[i:] + ref1[:i]  # advancing rotation
    for i in range(3):
        c = findCycle(segArr, i+4, range(segArr.shape[0]))
        assert c == ref2[i:] + ref2[:i]


def test_addCycleSketch():
    '''Test if cycles are correctly added.'''
    b = (-30, 20, 0)
    d = ( 20,-10, 0)
    sketch = aux_two_cycle_sketch(b=b, d=d)
    segArr, cycles = findEdgeCycles(sketch)
    addCycleSketch('cyclesketch', myDoc, cycles[0], segArr[0:4])
    segArr = findSegments(myDoc.cyclesketch)
    assert (segArr[0][1] == [b]).all()
    assert (segArr[2][1] == [d]).all()

    with pytest.raises(ValueError) as err:
        addCycleSketch('cyclesketch', myDoc, cycles[0], segArr[0:4])
    assert 'already exists' in str(err.value)


def test_addPolyLineSketch():
    '''Test if polylines are correctly added.'''
    pass
    #TODO


def test_findEdgeCycles():
    '''Test multiple cycle ordering.'''
    sketch = aux_two_cycle_sketch()
    seg, cycles = findEdgeCycles(sketch)
    assert cycles[0] == [ 0, 1, 2, 3 ]
    assert cycles[1] == [ 4, 5, 6 ]


def test_splitSketch():
    '''Test if multi-cycle sketches are split correctly.'''
    sketch = aux_two_cycle_sketch()

    newsketchL = splitSketch(sketch)
    centers_orig = [e.CenterOfMass for e in sketch.Shape.Edges]
    centers_sq = [e.CenterOfMass for e in newsketchL[0].Shape.Edges]
    centers_tri = [e.CenterOfMass for e in newsketchL[1].Shape.Edges]

    for p in centers_sq:
        assert p in centers_orig and p not in centers_tri
    for p in centers_tri:
        assert p in centers_orig and p not in centers_sq


def test_extendSketch():
    '''Test unconnected sketch extension, all cases.'''
    sketch = myDoc.addObject('Sketcher::SketchObject','Sketch')
    geoList = []
    geoList.append(Part.LineSegment(vec(0,0,0),vec(0,2,0)))
    geoList.append(Part.LineSegment(vec(0,2,0),vec(-2,2,0)))
    sketch.addGeometry(geoList,False)
    myDoc.recompute()
    ext = extendSketch(sketch, 1)
    assert ext.Shape.Vertexes[0].Point == vec(0,-1,0)
    assert ext.Shape.Vertexes[2].Point == vec(-3,2,0)

    deepRemove(sketch)
    deepRemove(ext)
    sketch = myDoc.addObject('Sketcher::SketchObject','Sketch')
    geoList = []
    geoList.append(Part.LineSegment(vec(0,0,0),vec(2,0,0)))
    geoList.append(Part.LineSegment(vec(2,0,0),vec(2,-2,0)))
    sketch.addGeometry(geoList,False)
    myDoc.recompute()
    ext = extendSketch(sketch, 1)
    assert ext.Shape.Length == 2 + sketch.Shape.Length


def test_draftOffset():
    '''Check if draft offset resizes the object. TODO: edge cases'''
    pl=FreeCAD.Placement()
    pl.Base=vec(1,1,0)
    draft = Draft.makeRectangle(length=2,height=2,placement=pl,face=False,support=None)
    draft2 = draftOffset(draft, 20)
    assert draft.Height.Value + 40 == draft2.Height.Value

