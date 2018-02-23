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


def teardown_function(function):
    FreeCAD.closeDocument('testDoc')


def manual_testing(function):
    setup_function(function)
    function()
    teardown_function(function)


def aux_two_cycle_sketch( a=( 20, 20, 0), b=(-30, 20, 0), c=(-30,-10, 0), d=( 20,-10, 0),
                          e=( 50, 50, 0), f=( 60, 50, 0), g=( 55, 60, 0) ):
    '''Helper function to drop a simple multi-cycle sketch.
       The segments are carefully ordered.
    '''

    sketch = FreeCAD.activeDocument().addObject('Sketcher::SketchObject','Sketch')
    geoList = []
    geoList.append(Part.Line(FreeCAD.Vector(*a),FreeCAD.Vector(*b)))
    geoList.append(Part.Line(FreeCAD.Vector(*b),FreeCAD.Vector(*c)))
    geoList.append(Part.Line(FreeCAD.Vector(*c),FreeCAD.Vector(*d)))
    geoList.append(Part.Line(FreeCAD.Vector(*d),FreeCAD.Vector(*a)))
    geoList.append(Part.Line(FreeCAD.Vector(*e),FreeCAD.Vector(*f)))
    geoList.append(Part.Line(FreeCAD.Vector(*f),FreeCAD.Vector(*g)))
    geoList.append(Part.Line(FreeCAD.Vector(*g),FreeCAD.Vector(*e)))
    FreeCAD.ActiveDocument.Sketch.addGeometry(geoList,False)
    FreeCAD.ActiveDocument.recompute()
    return sketch


def test_deepRemove():
    '''Test deep (recursive) removal by all parameters.'''
    sketch = aux_two_cycle_sketch()
    part = qmt.freecad.extrude(sketch, 10)
    deepRemove(part)
    assert len(myDoc.Objects) == 0

    sketch = aux_two_cycle_sketch()
    part = qmt.freecad.extrude(sketch, 10)
    part2 = myDoc.copyObject(part, False)
    deepRemove(name=part2.Name)
    assert len(part.OutList) == 0  # part2 steals sketch from part1

    deepRemove(label=part.Label)
    assert len(myDoc.Objects) == 0

    with pytest.raises(RuntimeError) as err:
        deepRemove(None)
    assert 'No object selected' in str(err.value)

    box1 = myDoc.addObject("Part::Box","Box1")
    box2 = myDoc.addObject("Part::Box","Box2")
    box3 = myDoc.addObject("Part::Box","Box3")
    inter1 = myDoc.addObject("Part::MultiCommon","inter1")
    inter1.Shapes = [box1, box2,]
    myDoc.recompute()
    inter2 = myDoc.addObject("Part::MultiCommon","inter2")
    inter2.Shapes = [inter1, box3,]
    myDoc.recompute()
    deepRemove(inter2)


manual_testing(test_deepRemove)


def test_findSegments():
    '''Test if segment finding is ordered correctly.'''
    b = (-30, 20, 0)
    d = ( 20,-10, 0)
    sketch = aux_two_cycle_sketch(b=b, d=d)

    segL = findSegments(sketch)
    assert (segL[0][1] == [b]).all()
    assert (segL[2][1] == [d]).all()


def test_nextSegment():
    '''Test if nextSegment correctly increments.'''
    sketch = aux_two_cycle_sketch()  # trivial case
    lineSegments = findSegments(sketch)
    assert nextSegment(lineSegments, 0) == 1
    assert nextSegment(lineSegments, 1) == 2
    assert nextSegment(lineSegments, 2) == 3
    assert nextSegment(lineSegments, 3) == 0  # a square cycle

    deepRemove(sketch)
    a=( 20, 20, 0)
    sketch = aux_two_cycle_sketch(a=a, e=a)
    lineSegments = findSegments(sketch)
    with pytest.raises(ValueError) as err:
        nextSegment(lineSegments, 3)  # e is ambiguous
    assert 'possible paths found' in str(err.value)


def test_findCycle():
    '''Test cycle ordering.'''
    sketch = aux_two_cycle_sketch()
    lineSegments = findSegments(sketch)
    c0 = findCycle(lineSegments, 0, range(lineSegments.shape[0]))
    assert c0 == [ 1, 2, 3, 0 ]


def test_addCycleSketch():
    '''Test if cycles are correctly added.'''
    b = (-30, 20, 0)
    d = ( 20,-10, 0)
    sketch = aux_two_cycle_sketch(b=b, d=d)
    lineSegments, cycles = findEdgeCycles(sketch)
    addCycleSketch('cyclesketch', myDoc, cycles[0], lineSegments[0:4])
    segL = findSegments(myDoc.cyclesketch)
    assert (segL[0][0] == [b]).all()  # note: added cycle is shifted  (TODO: intentionally?)
    assert (segL[2][0] == [d]).all()
    
    with pytest.raises(ValueError) as err:
        addCycleSketch('cyclesketch', myDoc, cycles[0], lineSegments[0:4])
    assert 'already exists' in str(err.value)


def test_findEdgeCycles():
    '''Test multiple cycle ordering.'''
    sketch = aux_two_cycle_sketch()
    seg, cycles = findEdgeCycles(sketch)
    assert cycles[0] == [ 1, 2, 3, 0 ]
    assert cycles[1] == [ 5, 6, 4 ]


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
    geoList.append(Part.Line(FreeCAD.Vector(0,0,0),FreeCAD.Vector(0,2,0)))
    geoList.append(Part.Line(FreeCAD.Vector(0,2,0),FreeCAD.Vector(-2,2,0)))
    sketch.addGeometry(geoList,False)
    myDoc.recompute()
    ext = extendSketch(sketch, 1)
    assert ext.Shape.Vertexes[0].Point == FreeCAD.Vector(0,-1,0)
    assert ext.Shape.Vertexes[2].Point == FreeCAD.Vector(-3,2,0)

    deepRemove(sketch)
    deepRemove(ext)
    sketch = myDoc.addObject('Sketcher::SketchObject','Sketch')
    geoList = []
    geoList.append(Part.Line(FreeCAD.Vector(0,0,0),FreeCAD.Vector(2,0,0)))
    geoList.append(Part.Line(FreeCAD.Vector(2,0,0),FreeCAD.Vector(2,-2,0)))
    sketch.addGeometry(geoList,False)
    myDoc.recompute()
    ext = extendSketch(sketch, 1)
    assert ext.Shape.Length == 2 + sketch.Shape.Length


def test_draftOffset():
    '''Check if draft offset resizes the object. TODO: edge cases'''
    pl=FreeCAD.Placement()
    pl.Base=FreeCAD.Vector(1,1,0)
    draft = Draft.makeRectangle(length=2,height=2,placement=pl,face=False,support=None)
    draft2 = draftOffset(draft, 20)
    assert draft.Height.Value + 40 == draft2.Height.Value
