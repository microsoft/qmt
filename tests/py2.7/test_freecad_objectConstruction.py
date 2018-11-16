# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

from __future__ import absolute_import, division, print_function

from qmt.geometry.freecad.objectConstruction import *


def test_build(fix_exampleDir, fix_FCDoc):
    from qmt.data import Part3DData
    myPart = Part3DData('block_of_gold', 'Sketch', 'extrude', 'metal_gate',
                        material='Au', thickness=10)
    opts = {
        'pyenv': 'python2',
        'file_path': os.path.join(fix_exampleDir, 'geometry_sweep_showcase.fcstd'),
        'input_parts': [myPart],
        'xsec_dict':{}
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


# ~ def test_makeSAG():
# ~ '''Test SAG construction via bounding box.'''
# ~ sketch = aux_unit_square_sketch()
# ~ sag = makeSAG(sketch, 0, 1, 2, 0.3, 0.1)
# ~ assert sag.TypeId == "Part::Feature"
# ~ assert np.allclose(getBB(sag)[0:2], (-0.1, 1.1))
# ~ assert np.allclose(getBB(sag)[2:4], (-0.1, 1.1))
# ~ assert np.allclose(getBB(sag)[4:6], (0., 2.))


# ~ def test_modelBuilder_saveFreeCADState():
# ~ mb = modelBuilder()
# ~ fcFilePath = os.path.splitext(modelFilePath)[0]+'.FCStd'
# ~ mb.saveFreeCADState(fcFilePath)
# ~ assert 'testModel.FCStd' in os.listdir(testDir)
# ~ os.remove(fcFilePath)
