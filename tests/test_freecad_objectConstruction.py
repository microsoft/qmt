# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

from __future__ import absolute_import, division, print_function
import qmt
import os
import FreeCAD
import Part
from qmt.freecad.objectConstruction import *
from qmt.freecad.fileIO import setupModelFile


def setup_function(function):
    global myDoc
    myDoc = FreeCAD.newDocument('testDoc')
    repo_path = os.path.join(os.path.dirname(qmt.__file__), os.pardir)
    global testDir
    testDir = os.path.join(repo_path, 'tests')
    global modelFilePath
    modelFilePath = os.path.join(testDir, 'testModel.json')
    setupModelFile(modelFilePath)


def teardown_function(function):
    os.remove(modelFilePath)
    FreeCAD.closeDocument('testDoc')


def manual_testing(function):
    setup_function(function)
    function()
    teardown_function(function)


def repo_path():
    """Retrieve path to the directory containing the qmt repository."""
    return 


def aux_unit_square_sketch():
    '''Helper function to drop a simple unit square sketch.
       The segments are carefully ordered.
    '''
    a = (0,0,0)
    b = (1,0,0)
    c = (1,1,0)
    d = (0,1,0)

    sketch = FreeCAD.activeDocument().addObject('Sketcher::SketchObject','Sketch')
    geoList = []
    geoList.append(Part.Line(FreeCAD.Vector(*a),FreeCAD.Vector(*b)))
    geoList.append(Part.Line(FreeCAD.Vector(*b),FreeCAD.Vector(*c)))
    geoList.append(Part.Line(FreeCAD.Vector(*c),FreeCAD.Vector(*d)))
    geoList.append(Part.Line(FreeCAD.Vector(*d),FreeCAD.Vector(*a)))
    FreeCAD.ActiveDocument.Sketch.addGeometry(geoList,False)
    FreeCAD.ActiveDocument.recompute()
    return sketch


def test_buildWire():
    '''Test wire via bounding box for default offsets/zBottom.
       TODO: all cases
    '''
    sketch = myDoc.addObject('Sketcher::SketchObject','Sketch')
    geoList = []
    geoList.append(Part.Line(FreeCAD.Vector(0,0,0),FreeCAD.Vector(1,2,0)))
    geoList.append(Part.Line(FreeCAD.Vector(1,2,0),FreeCAD.Vector(3,3,0)))
    sketch.addGeometry(geoList,False)
    myDoc.recompute()
    wire = buildWire(sketch, 0, 1)
    print(getBB(wire))
    assert wire.TypeId == 'Part::Feature'
    assert np.allclose(getBB(wire)[4:6], (0,1))  # z direction constrained


def test_makeSAG():
    '''Test SAG construction via bounding box.'''
    sketch = aux_unit_square_sketch()
    sag = makeSAG(sketch, 0, 1, 2, 0.3, 0.1)
    assert sag.TypeId == "Part::Feature"
    assert np.allclose(getBB(sag)[0:2], (-0.1, 1.1))
    assert np.allclose(getBB(sag)[2:4], (-0.1, 1.1))
    assert np.allclose(getBB(sag)[4:6], (0., 2.))


def test_modelBuilder_saveFreeCADState():
    mb = modelBuilder()
    fcFilePath = os.path.splitext(modelFilePath)[0]+'.FCStd'
    mb.saveFreeCADState(fcFilePath)
    assert 'testModel.FCStd' in os.listdir(testDir)
    os.remove(fcFilePath)
