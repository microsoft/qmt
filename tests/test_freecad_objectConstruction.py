# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

from __future__ import absolute_import, division, print_function
from qmt.geometry.freecad.objectConstruction import *
import pytest


def test_build(fix_exampleDir, fix_FCDoc):
    from qmt.data import Part3DData
    myPart = Part3DData('block_of_gold', 'Sketch', 'extrude', 'metal_gate',
                        material='Au', thickness=10)
    opts = {
        'file_path': os.path.join(fix_exampleDir, 'geometry_sweep', 'geometry_sweep_showcase.fcstd'),
        'input_parts': [myPart],
        'xsec_dict': {}
    }
    fix_FCDoc.load(opts['file_path'])
    build(opts)
    # TODO


def test_build_extrude(fix_FCDoc, fix_hexagon_sketch):
    from qmt.data import Part3DData
    sketch = fix_hexagon_sketch()
    input_part = Part3DData('label', sketch.Name, 'extrude', 'metal_gate',
                            material='Au', thickness=10)
    built_part = build_extrude(input_part)
    # TODO

# ~ def test_buildWire():
# ~ '''Test wire via bounding box for default offsets/zBottom.
# ~ TODO: all cases
# ~ '''
# ~ sketch = myDoc.addObject('Sketcher::SketchObject','Sketch')
# ~ geoList = []
# ~ geoList.append(Part.LineSegment(FreeCAD.Vector(0,0,0),FreeCAD.Vector(1,2,0)))
# ~ geoList.append(Part.LineSegment(FreeCAD.Vector(1,2,0),FreeCAD.Vector(3,3,0)))
# ~ sketch.addGeometry(geoList,False)
# ~ myDoc.recompute()
# ~ wire = buildWire(sketch, 0, 1)
# ~ print(getBB(wire))
# ~ assert wire.TypeId == 'Part::Feature'
# ~ assert np.allclose(getBB(wire)[4:6], (0,1))  # z direction constrained


def test_makeSAG_typical(fix_FCDoc, fix_rectangle_sketch):
    r'''
    Test the case where there's a flat top
          __
         /  \
        /    \
       /      \
      /        \        NOT TO SCALE
     /          \ 
    /_          _\
      |________|
    '''
    sketch = fix_rectangle_sketch()
    sag = makeSAG(sketch, 0, 1, 2, 0.1, 0.1)[0]
    assert sag.TypeId == "Part::Feature"
    assert np.allclose(getBB(sag), (-0.1, 1.1, -0.1, 1.1, 0, 2))
    # Volume of incomplete pyramid is h(a^2 + ab + b^2)/3
    assert np.isclose(sag.Shape.Volume, 2.01333)


def test_makeSAG_triangle_with_rectangular_base(fix_FCDoc, fix_rectangle_sketch):
    r'''
    Test the case where the top collapses down to a line 
          /\
         /  \
        /    \
       /      \        NOT TO SCALE
      /        \
     /          \ 
    /_          _\
      |________|
    '''
    sketch = fix_rectangle_sketch(1, 2)
    sag = makeSAG(sketch, 0, 1, 2, 0.5, 0.1)[0]
    assert sag.TypeId == "Part::Feature"
    assert np.allclose(getBB(sag), (-0.1, 1.1, -0.1, 2.1, 0, 2))
    # Volume of pyramid is hwl/3
    # Volume of triangular prism is hwl/2
    assert np.isclose(sag.Shape.Volume, 3.08, 0.0001)


def test_makeSAG_triangle_with_square_base(fix_FCDoc, fix_rectangle_sketch):
    r'''
    Test the case where the top collapses down to a point 
          /\
         /  \
        /    \
       /      \        NOT TO SCALE
      /        \
     /          \ 
    /_          _\
      |________|
    '''
    sketch = fix_rectangle_sketch()
    sag = makeSAG(sketch, 0, 1, 2, 0.5, 0.1)[0]
    assert sag.TypeId == "Part::Feature"
    assert np.allclose(getBB(sag), (-0.1, 1.1, -0.1, 1.1, 0, 2))
    # Volume of pyramid is hwl/3
    assert np.isclose(sag.Shape.Volume, 1.48, 0.0001)


def test_makeSAG_triangle_with_no_rectangular_part(fix_FCDoc, fix_rectangle_sketch):
    r'''
    Test the case where there is no rectangular part at the bottom
          /\
         /  \
        /    \
       /      \        NOT TO SCALE
      /        \
     /          \ 
    /____________\
    '''
    sketch = fix_rectangle_sketch()
    sag = makeSAG(sketch, 0, 0, 1, 0.5, 0.1)[0]
    assert sag.TypeId == "Part::Feature"
    assert np.allclose(getBB(sag), (-0.1, 1.1, -0.1, 1.1, 0, 1))
    # Volume of pyramid is hwl/3
    assert np.isclose(sag.Shape.Volume, 0.48, 0.0001)


def test_makeSAG_with_fat_top(fix_FCDoc, fix_rectangle_sketch):
    r'''
    Test the case where the top is fatter than the bottom, but not fatter than the middle
     ____________
    /__        __\        NOT TO SCALE
       |______|
    '''
    sketch = fix_rectangle_sketch()
    sag = makeSAG(sketch, 0, 1, 2, -0.1, 0.2)[0]
    assert sag.TypeId == "Part::Feature"
    assert np.allclose(getBB(sag), (-0.2, 1.2, -0.2, 1.2, 0, 2))
    # Volume of incomplete pyramid is h(a^2 + ab + b^2)/3
    assert np.isclose(sag.Shape.Volume, 2.69333)


def test_makeSAG_with_fattest_top(fix_FCDoc, fix_rectangle_sketch):
    r'''
    Test the case where the top is fatter than the bottom and than the middle
    Not physical, but the software should be able to handle it anyway
    ______________
    \__        __/        NOT TO SCALE
       |______|
    '''
    sketch = fix_rectangle_sketch()
    sag = makeSAG(sketch, 0, 1, 2, -0.2, 0.1)[0]
    assert sag.TypeId == "Part::Feature"
    assert np.allclose(getBB(sag), (-0.2, 1.2, -0.2, 1.2, 0, 2))
    # Volume of incomplete pyramid is h(a^2 + ab + b^2)/3
    assert np.isclose(sag.Shape.Volume, 2.69333)


def test_makeSAG_with_no_over_hang(fix_FCDoc, fix_rectangle_sketch):
    r'''
    Test the case where there is no overhang
     ________
    /        \        NOT TO SCALE
    |________|
    '''
    sketch = fix_rectangle_sketch()
    sag = makeSAG(sketch, 0, 1, 2, 0.1, 0)[0]
    assert sag.TypeId == "Part::Feature"
    assert np.allclose(getBB(sag), (0, 1, 0, 1, 0, 2))
    # Volume of incomplete pyramid is h(a^2 + ab + b^2)/3
    assert np.isclose(sag.Shape.Volume, 1.81333)


def test_makeSAG_with_no_top(fix_FCDoc, fix_rectangle_sketch):
    r'''
    Assertion should fail if you try to build a SAG with no top. This is because there is no way to calculate offset if there is no height to the roof, and that case needs to be handled separately. However it's a pretty useless case so we don't support it
     ________
    |________|        NOT TO SCALE
    '''
    sketch = fix_rectangle_sketch()
    with pytest.raises(Exception):
        sag = makeSAG(sketch, 0, 1, 1, 0.1, 0)[0]

# ~ def test_modelBuilder_saveFreeCADState():
# ~ mb = modelBuilder()
# ~ fcFilePath = os.path.splitext(modelFilePath)[0]+'.FCStd'
# ~ mb.saveFreeCADState(fcFilePath)
# ~ assert 'testModel.FCStd' in os.listdir(testDir)
# ~ os.remove(fcFilePath)
