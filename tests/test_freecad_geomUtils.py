# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

"""Testing QMT geometry util functions."""


from __future__ import absolute_import, division, print_function
import FreeCAD
import Part
import ProfileLib.RegularPolygon
from qmt.geometry.freecad.geomUtils import *

vec = FreeCAD.Vector


def aux_two_cycle_sketch( a=( 20, 20, 0), b=(-30, 20, 0), c=(-30,-10, 0), d=( 20,-10, 0),
                          e=( 50, 50, 0), f=( 60, 50, 0), g=( 55, 60, 0) ):
    '''Helper function to drop a simple multi-cycle sketch.
       The segments are ordered into one rectangle and one triangle.
    '''
    # Note: the z-component is zero, as sketches are plane objects.
    #       Adjust orientation with Sketch.Placement(Normal, Rotation)

    doc = FreeCAD.ActiveDocument
    sketch = doc.addObject('Sketcher::SketchObject', 'Sketch')
    sketch.addGeometry(Part.LineSegment(vec(*a), vec(*b)), False)
    sketch.addGeometry(Part.LineSegment(vec(*b), vec(*c)), False)
    sketch.addGeometry(Part.LineSegment(vec(*c), vec(*d)), False)
    sketch.addGeometry(Part.LineSegment(vec(*d), vec(*a)), False)
    sketch.addGeometry(Part.LineSegment(vec(*e), vec(*f)), False)
    sketch.addGeometry(Part.LineSegment(vec(*f), vec(*g)), False)
    sketch.addGeometry(Part.LineSegment(vec(*g), vec(*e)), False)
    doc.recompute()
    return sketch


def aux_unit_square_sketch():
    '''Helper function to drop a simple unit square sketch.
       The segments are carefully ordered.
    '''
    a = (0, 0, 0)
    b = (1, 0, 0)
    c = (1, 1, 0)
    d = (0, 1, 0)

    doc = FreeCAD.ActiveDocument
    sketch = doc.addObject('Sketcher::SketchObject', 'Sketch')
    sketch.addGeometry(Part.LineSegment(vec(*a), vec(*b)), False)
    sketch.addGeometry(Part.LineSegment(vec(*b), vec(*c)), False)
    sketch.addGeometry(Part.LineSegment(vec(*c), vec(*d)), False)
    sketch.addGeometry(Part.LineSegment(vec(*d), vec(*a)), False)
    doc.recompute()
    return sketch


def aux_hexagon_sketch(r=1):
    '''Helper function to drop a hexagonal sketch.'''

    doc = FreeCAD.ActiveDocument
    sketch = doc.addObject('Sketcher::SketchObject', 'HexSketch')
    ProfileLib.RegularPolygon.makeRegularPolygon('HexSketch', 6, vec(10,10,0), vec(20,20,0), False)
    doc.recompute()
    return sketch


def test_extrude(fix_FCDoc):
    '''Test if extrusion produces PartDesign parts.'''
    sketch = aux_two_cycle_sketch()
    pad = extrude(sketch, 50, name="pad", reverse=True)
    # ~ assert pad.Length.Value == 50
    # ~ assert pad.TypeId == 'PartDesign::Pad'
    assert pad.LengthFwd.Value == 50
    assert pad.TypeId == 'Part::Extrusion'


def test_copy(fix_FCDoc):
    '''Test copy.'''
    # TODO: warning.
    #~ sketch = aux_two_cycle_sketch() # WARNING: multi-cycle sketches don't get moved correctly -> need sanitation
    sketch = aux_hexagon_sketch()
    sketch2 = copy(sketch, vec(0,0,20), copy=True)
    fix_FCDoc.recompute()
    assert sketch.Shape.Edges[0].Vertexes[0].Point[2] + 20 == sketch2.Shape.Edges[0].Vertexes[0].Point[2]


def test_makeHexFace(fix_FCDoc):
    '''Test wire face positioning.'''
    # TODO: has /0 warning for given line
    sketch = fix_FCDoc.addObject('Sketcher::SketchObject', 'wireline')
    sketch.addGeometry(Part.LineSegment(vec(0,0,0), vec(0,2,0)), False)
    fix_FCDoc.recompute()
    face = makeHexFace(sketch, 0, 15)
    assert np.isclose(face.Shape.BoundBox.ZLength, 15)
    assert np.isclose(face.Shape.BoundBox.XMin, -face.Shape.BoundBox.XMax)
    assert np.isclose(face.Shape.BoundBox.YMin, 0)
    assert np.isclose(face.Shape.BoundBox.YMax, 0)
    assert np.isclose(face.Shape.BoundBox.ZMin, 0)


def test_genUnion(fix_FCDoc):
    '''Test union via bounding box.'''
    box1 = fix_FCDoc.addObject("Part::Box", "Box1")
    box2 = fix_FCDoc.addObject("Part::Box", "Box2")
    box2.Placement = FreeCAD.Placement(vec(10,0,0), FreeCAD.Rotation(vec(0,0,1), 0))
    box3 = fix_FCDoc.addObject("Part::Box", "Box2")
    fix_FCDoc.recompute()
    assert genUnion([]) is None
    assert genUnion([box3]).Shape.CenterOfMass == box1.Shape.CenterOfMass
    assert genUnion([box3], consumeInputs=True).Shape.CenterOfMass == box1.Shape.CenterOfMass
    union = genUnion([box1, box2], consumeInputs=True)
    assert union.Shape.BoundBox.XLength == 20


def test_getBB(fix_FCDoc):
    '''Test if getBB captures default Part Box.'''
    box = fix_FCDoc.addObject("Part::Box", "Box1")
    fix_FCDoc.recompute()
    bb = getBB(box)
    assert bb == (0, 10, 0, 10, 0, 10)


def test_makeBB(fix_FCDoc):
    '''Test if makeBB generates default Part Box bb.'''
    box1 = fix_FCDoc.addObject("Part::Box", "Box1")
    fix_FCDoc.recompute()
    box2 = makeBB((0, 10, 0, 10, 0, 10))
    assert getBB(box1) == getBB(box2)


def test_subtract(fix_FCDoc):
    '''Test subtract by checking volume.'''
    box1 = fix_FCDoc.addObject("Part::Box", "Box1")
    box2 = fix_FCDoc.addObject("Part::Box", "Box2")
    box2.Placement = FreeCAD.Placement(vec(5,0,0), FreeCAD.Rotation(vec(0,0,1), 0))
    fix_FCDoc.recompute()
    cut = subtract(box1, box2, consumeInputs=True)
    assert np.isclose(cut.Shape.Volume, 10**3 * 0.5)


def test_subtractParts(fix_FCDoc):
    '''Test subtract by checking volume.
    '''
    #   TODO: the FC v0.16 Draft requires UiLoader, which doesn't work from the cli.
    box1 = fix_FCDoc.addObject("Part::Box", "Box1")
    box2 = fix_FCDoc.addObject("Part::Box", "Box2")
    box3 = fix_FCDoc.addObject("Part::Box", "Box3")
    box2.Placement = FreeCAD.Placement(vec(5,0,0), FreeCAD.Rotation(vec(0,0,1), 0))
    box3.Placement = FreeCAD.Placement(vec(-8,0,0), FreeCAD.Rotation(vec(0,0,1), 0))
    #~ cut = subtractParts(box1, [box2, box3])
    #~ assert np.isclose(cut.Shape.Volume, 10**3 * 0.3)


def test_intersect(fix_FCDoc):
    '''Test intersect by checking volume.'''
    box1 = fix_FCDoc.addObject("Part::Box", "Box1")
    box2 = fix_FCDoc.addObject("Part::Box", "Box2")
    box2.Placement = FreeCAD.Placement(vec(7,0,0), FreeCAD.Rotation(vec(0,0,1), 0))
    fix_FCDoc.recompute()
    cut = intersect((box1, box2), consumeInputs=True)
    assert np.isclose(cut.Shape.Volume, 10**3 * 0.3)


def test_checkOverlap(fix_FCDoc):
    '''Test overlap between two volumes.'''
    box1 = fix_FCDoc.addObject("Part::Box", "Box1")
    box2 = fix_FCDoc.addObject("Part::Box", "Box2")
    box2.Placement = FreeCAD.Placement(vec(9.9,0,0), FreeCAD.Rotation(vec(0,0,1), 0))
    fix_FCDoc.recompute()
    assert checkOverlap((box1, box2)) is True
    box2.Placement = FreeCAD.Placement(vec(10.1,0,0), FreeCAD.Rotation(vec(0,0,1), 0))
    fix_FCDoc.recompute()
    assert checkOverlap((box1, box2)) is False


def test_extrudeBetween(fix_FCDoc):
    '''Test if extrusion bounding box is within z interval.'''
    sketch = aux_hexagon_sketch()
    pad = extrudeBetween(sketch, 10, 20)
    assert getBB(pad)[-2:] == (10, 20)


def test_liftObject(fix_FCDoc):
    '''Test sweeping lift for sketches.'''
    # TODO: why do we have to make union with the lifted sketch?.
    sketch = aux_unit_square_sketch()
    #~ vol = liftObject(sketch, 42, consumeInputs=False)
    #~ assert vol.Shape.Volume == 42


def test_centerObjects(fix_FCDoc):
    '''Check centering of boxes.'''
    # TODO: centering or snapping to zero?
    box1 = fix_FCDoc.addObject("Part::Box", "Box1")
    box2 = fix_FCDoc.addObject("Part::Box", "Box2")
    box2.Placement = FreeCAD.Placement(vec(1.5,3.5,2.5), FreeCAD.Rotation(vec(0,0,1), 0))
    fix_FCDoc.recompute()
    assert centerObjects(()) is None
    #~ print(getBB(box1))
    #~ print(getBB(box2))
    centerObjects((box1, box2))
    #~ print(getBB(box1))
    #~ print(getBB(box2))
    assert getBB(box1) == getBB(box2)


def test_crossSection(fix_FCDoc):
    '''TODO.'''
    box = fix_FCDoc.addObject("Part::Box", "Box")
    fix_FCDoc.recompute()
    cross = crossSection(box)
    assert getBB(cross) == (1.0,1.0,0,10,0,10)
