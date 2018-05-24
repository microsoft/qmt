# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

from __future__ import absolute_import, division, print_function
import FreeCAD
import Part
import ProfileLib.RegularPolygon
from qmt.freecad.geomUtils import *


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
       The segments are carefully ordered.
    '''

    sketch = FreeCAD.activeDocument().addObject('Sketcher::SketchObject','Sketch')
    sketch.addGeometry(Part.LineSegment(vec(*a),vec(*b)),False)
    sketch.addGeometry(Part.LineSegment(vec(*b),vec(*c)),False)
    sketch.addGeometry(Part.LineSegment(vec(*c),vec(*d)),False)
    sketch.addGeometry(Part.LineSegment(vec(*d),vec(*a)),False)
    sketch.addGeometry(Part.LineSegment(vec(*e),vec(*f)),False)
    sketch.addGeometry(Part.LineSegment(vec(*f),vec(*g)),False)
    sketch.addGeometry(Part.LineSegment(vec(*g),vec(*e)),False)
    myDoc.recompute()
    return sketch


def aux_unit_square_sketch():
    '''Helper function to drop a simple unit square sketch.
       The segments are carefully ordered.
    '''
    a = (0,0,0)
    b = (1,0,0)
    c = (1,1,0)
    d = (0,1,0)

    sketch = FreeCAD.activeDocument().addObject('Sketcher::SketchObject','Sketch')
    sketch.addGeometry(Part.LineSegment(vec(*a),vec(*b)),False)
    sketch.addGeometry(Part.LineSegment(vec(*b),vec(*c)),False)
    sketch.addGeometry(Part.LineSegment(vec(*c),vec(*d)),False)
    sketch.addGeometry(Part.LineSegment(vec(*d),vec(*a)),False)
    FreeCAD.ActiveDocument.recompute()
    return sketch


def aux_hexagon_sketch(r=1):
    '''Helper function to drop a hexagonal sketch.'''

    sketch = FreeCAD.activeDocument().addObject('Sketcher::SketchObject','HexSketch')
    ProfileLib.RegularPolygon.makeRegularPolygon('HexSketch',6,FreeCAD.Vector(10,10,0),FreeCAD.Vector(20,20,0),False)
    FreeCAD.ActiveDocument.recompute()
    return sketch


def test_extrude():
    '''Test if extrusion produces PartDesign parts.'''
    sketch = aux_two_cycle_sketch()
    pad = extrude(sketch, 50, name = "pad", reverse=True)
    # ~ assert pad.Length.Value == 50
    # ~ assert pad.TypeId == 'PartDesign::Pad'
    assert pad.LengthFwd.Value == 50
    assert pad.TypeId == 'Part::Extrusion'


def test_copy():
    '''Test copy. TODO: warning.'''
    #~ sketch = aux_two_cycle_sketch() # WARNING: multi-cycle sketches don't get moved correctly -> need sanitation
    sketch = aux_hexagon_sketch()
    sketch2 = copy(sketch, FreeCAD.Vector(0,0,20), copy=True)
    myDoc.recompute()
    assert sketch.Shape.Edges[0].Vertexes[0].Point[2] + 20 == sketch2.Shape.Edges[0].Vertexes[0].Point[2]


def test_makeHexFace():
    '''Test wire face positioning. TODO: has /0 warning for given line'''
    sketch = myDoc.addObject('Sketcher::SketchObject','wireline')
    sketch.addGeometry(Part.LineSegment(vec(0,0,0),vec(0,2,0)),False)
    myDoc.recompute()
    face = makeHexFace(sketch, 0, 15)
    assert np.isclose(face.Shape.BoundBox.ZLength, 15)
    assert np.isclose(face.Shape.BoundBox.XMin, -face.Shape.BoundBox.XMax)
    assert np.isclose(face.Shape.BoundBox.YMin, 0)
    assert np.isclose(face.Shape.BoundBox.YMax, 0)
    assert np.isclose(face.Shape.BoundBox.ZMin, 0)

def test_genUnion():
    '''Test union via bounding box.'''
    box1 = myDoc.addObject("Part::Box","Box1")
    box2 = myDoc.addObject("Part::Box","Box2")
    box2.Placement = FreeCAD.Placement(FreeCAD.Vector(10,0,0),FreeCAD.Rotation(FreeCAD.Vector(0,0,1),0))
    box3 = myDoc.addObject("Part::Box","Box2")
    myDoc.recompute()
    assert genUnion([]) == None
    assert genUnion([box3]).Shape.CenterOfMass == box1.Shape.CenterOfMass
    assert genUnion([box3], consumeInputs=True).Shape.CenterOfMass == box1.Shape.CenterOfMass
    union = genUnion([box1, box2], consumeInputs=True)
    assert union.Shape.BoundBox.XLength == 20


def test_getBB():
    '''Test if getBB captures default Part Box.'''
    box = myDoc.addObject("Part::Box","Box1")
    myDoc.recompute()
    bb = getBB(box)
    assert bb == (0, 10, 0, 10, 0, 10)


def test_makeBB():
    '''Test if makeBB generates default Part Box bb.'''
    box1 = myDoc.addObject("Part::Box","Box1")
    myDoc.recompute()
    box2 = makeBB( (0, 10, 0, 10, 0, 10) )
    assert getBB(box1) == getBB(box2)


def test_subtract():
    '''Test subtract by checking volume.'''
    box1 = myDoc.addObject("Part::Box","Box1")
    box2 = myDoc.addObject("Part::Box","Box2")
    box2.Placement = FreeCAD.Placement(FreeCAD.Vector(5,0,0),FreeCAD.Rotation(FreeCAD.Vector(0,0,1),0))
    myDoc.recompute()
    cut = subtract(box1, box2, consumeInputs=True)
    assert np.isclose(cut.Shape.Volume, 10**3 * 0.5)


def test_subtractParts():
    '''Test subtract by checking volume.
       TODO: the FC v0.16 Draft requires UiLoader, which doesn't work from the cli.
    '''
    box1 = myDoc.addObject("Part::Box","Box1")
    box2 = myDoc.addObject("Part::Box","Box2")
    box3 = myDoc.addObject("Part::Box","Box3")
    box2.Placement = FreeCAD.Placement(FreeCAD.Vector(5,0,0),FreeCAD.Rotation(FreeCAD.Vector(0,0,1),0))
    box3.Placement = FreeCAD.Placement(FreeCAD.Vector(-8,0,0),FreeCAD.Rotation(FreeCAD.Vector(0,0,1),0))
    #~ cut = subtractParts(box1, [box2, box3])
    #~ assert np.isclose(cut.Shape.Volume, 10**3 * 0.3)


def test_intersect():
    '''Test intersect by checking volume.'''
    box1 = myDoc.addObject("Part::Box","Box1")
    box2 = myDoc.addObject("Part::Box","Box2")
    box2.Placement = FreeCAD.Placement(FreeCAD.Vector(7,0,0),FreeCAD.Rotation(FreeCAD.Vector(0,0,1),0))
    myDoc.recompute()
    cut = intersect((box1, box2), consumeInputs=True)
    assert np.isclose(cut.Shape.Volume, 10**3 * 0.3)


def test_checkOverlap():
    '''Test overlap between two volumes.'''
    box1 = myDoc.addObject("Part::Box","Box1")
    box2 = myDoc.addObject("Part::Box","Box2")
    box2.Placement = FreeCAD.Placement(FreeCAD.Vector(9.9,0,0),FreeCAD.Rotation(FreeCAD.Vector(0,0,1),0))
    myDoc.recompute()
    assert checkOverlap((box1, box2)) == True
    box2.Placement = FreeCAD.Placement(FreeCAD.Vector(10.1,0,0),FreeCAD.Rotation(FreeCAD.Vector(0,0,1),0))
    myDoc.recompute()
    assert checkOverlap((box1, box2)) == False


def test_extrudeBetween():
    '''Test if extrusion bounding box is within z interval.'''
    sketch = aux_hexagon_sketch()
    pad = extrudeBetween(sketch, 10, 20)
    assert getBB(pad)[-2:] == (10, 20)


def test_liftObject():
    '''Test sweeping lift for sketches. TODO: why do we have to make union with the lifted sketch?.'''
    sketch = aux_unit_square_sketch()
    # TODO
    #~ vol = liftObject(sketch, 42, consumeInputs=False)
    #~ assert vol.Shape.Volume == 42


def test_centerObjects():
    '''Check centering of boxes. TODO: centering or snapping to zero?'''
    box1 = myDoc.addObject("Part::Box","Box1")
    box2 = myDoc.addObject("Part::Box","Box2")
    box2.Placement = FreeCAD.Placement(FreeCAD.Vector(1.5,3.5,2.5),FreeCAD.Rotation(FreeCAD.Vector(0,0,1),0))
    myDoc.recompute()
    assert centerObjects(()) == None
    #~ print(getBB(box1))
    #~ print(getBB(box2))
    centerObjects((box1, box2))
    #~ print(getBB(box1))
    #~ print(getBB(box2))
    assert getBB(box1) == getBB(box2)


def test_crossSection():
    box = myDoc.addObject("Part::Box","Box")
    myDoc.recompute()
    cross = crossSection(box)
    assert getBB(cross) == (1.0,1.0,0,10,0,10)
