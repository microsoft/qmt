# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

"""Testing QMT geometry util functions."""


from __future__ import division

from qmt.geometry.freecad.geomUtils import *

vec = FreeCAD.Vector


def test_extrude(fix_FCDoc, fix_two_cycle_sketch):
    '''Test if extrusion produces PartDesign parts.'''
    sketch = fix_two_cycle_sketch()
    pad = extrude(sketch, 50, name="pad", reverse=True)
    # ~ assert pad.Length.Value == 50
    # ~ assert pad.TypeId == 'PartDesign::Pad'
    assert pad.LengthFwd.Value == 50
    assert pad.TypeId == 'Part::Extrusion'


def test_copy_move(fix_FCDoc, fix_hexagon_sketch):
    '''Test copy.'''
    # TODO: warning.
    # ~ sketch = aux_two_cycle_sketch() # WARNING: multi-cycle sketches don't get moved correctly -> need sanitation
    sketch = fix_hexagon_sketch()
    sketch2 = copy_move(sketch, vec(0,0,20), copy=True)
    fix_FCDoc.recompute()
    assert sketch.Shape.Edges[0].Vertexes[0].Point[2] + 20 == sketch2.Shape.Edges[0].Vertexes[0].Point[2]


def test_makeHexFace(fix_FCDoc):
    '''Test wire face positioning.'''
    # TODO: has /0 warning for given line
    sketch = fix_FCDoc.addObject('Sketcher::SketchObject', 'wireline')
    sketch.addGeometry(Part.LineSegment(vec(0, 0, 0), vec(0, 2, 0)), False)
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
    box2.Placement = FreeCAD.Placement(vec(10, 0, 0), FreeCAD.Rotation(vec(0, 0, 1), 0))
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
    box2.Placement = FreeCAD.Placement(vec(5, 0, 0), FreeCAD.Rotation(vec(0, 0, 1), 0))
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
    box2.Placement = FreeCAD.Placement(vec(5, 0, 0), FreeCAD.Rotation(vec(0, 0, 1), 0))
    box3.Placement = FreeCAD.Placement(vec(-8, 0, 0), FreeCAD.Rotation(vec(0, 0, 1), 0))
    # ~ cut = subtractParts(box1, [box2, box3])
    # ~ assert np.isclose(cut.Shape.Volume, 10**3 * 0.3)


def test_intersect(fix_FCDoc):
    '''Test intersect by checking volume.'''
    box1 = fix_FCDoc.addObject("Part::Box", "Box1")
    box2 = fix_FCDoc.addObject("Part::Box", "Box2")
    box2.Placement = FreeCAD.Placement(vec(7, 0, 0), FreeCAD.Rotation(vec(0, 0, 1), 0))
    fix_FCDoc.recompute()
    cut = intersect((box1, box2), consumeInputs=True)
    assert np.isclose(cut.Shape.Volume, 10**3 * 0.3)


def test_checkOverlap(fix_FCDoc):
    '''Test overlap between two volumes.'''
    box1 = fix_FCDoc.addObject("Part::Box", "Box1")
    box2 = fix_FCDoc.addObject("Part::Box", "Box2")
    box2.Placement = FreeCAD.Placement(vec(9.9, 0, 0), FreeCAD.Rotation(vec(0, 0, 1), 0))
    fix_FCDoc.recompute()
    assert checkOverlap((box1, box2)) is True
    box2.Placement = FreeCAD.Placement(vec(10.1, 0, 0), FreeCAD.Rotation(vec(0, 0, 1), 0))
    fix_FCDoc.recompute()
    assert checkOverlap((box1, box2)) is False


def test_extrudeBetween(fix_FCDoc, fix_hexagon_sketch):
    '''Test if extrusion bounding box is within z interval.'''
    sketch = fix_hexagon_sketch()
    pad = extrudeBetween(sketch, 10, 20)
    assert getBB(pad)[-2:] == (10, 20)


def test_liftObject(fix_FCDoc, fix_unit_square_sketch):
    '''Test sweeping lift for sketches.'''
    # TODO: why do we have to make union with the lifted sketch?.
    sketch = fix_unit_square_sketch()
    # ~ vol = liftObject(sketch, 42, consumeInputs=False)
    # ~ assert vol.Shape.Volume == 42


def test_draftOffset(fix_FCDoc):
    '''Check if draft offset resizes the object. TODO: edge cases'''
    pl = FreeCAD.Placement()
    pl.Base = vec(1, 1, 0)
    draft = Draft.makeRectangle(length=2, height=2, placement=pl, face=False, support=None)
    draft2 = draftOffset(draft, 20)
    assert draft.Height.Value + 40 == draft2.Height.Value


def test_centerObjects(fix_FCDoc):
    '''Check centering of boxes.'''
    # TODO: centering or snapping to zero?
    box1 = fix_FCDoc.addObject("Part::Box", "Box1")
    box2 = fix_FCDoc.addObject("Part::Box", "Box2")
    box2.Placement = FreeCAD.Placement(vec(1.5, 3.5, 2.5), FreeCAD.Rotation(vec(0, 0, 1), 0))
    fix_FCDoc.recompute()
    assert centerObjects(()) is None
    # ~ print(getBB(box1))
    # ~ print(getBB(box2))
    centerObjects((box1, box2))
    # ~ print(getBB(box1))
    # ~ print(getBB(box2))
    assert getBB(box1) == getBB(box2)


def test_crossSection(fix_FCDoc):
    '''TODO.'''
    box = fix_FCDoc.addObject("Part::Box", "Box")
    fix_FCDoc.recompute()
    cross = crossSection(box)
    assert getBB(cross) == (1.0, 1.0, 0, 10, 0, 10)
