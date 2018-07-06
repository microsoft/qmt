# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

from __future__ import absolute_import, division, print_function
import pytest
import qmt
from qmt.freecad.fileIO import *
import os


def repo_path():
    """Retrieve path to the directory containing the qmt repository."""
    return os.path.join(os.path.dirname(qmt.__file__), os.pardir)


def test_setupModelFile():
    myDoc = FreeCAD.newDocument('testDoc')
    testDir = os.path.join(repo_path(), 'tests')
    filePath = os.path.join(testDir, 'testModel.json')
    dummy = myDoc.addObject("Part::Box", "modelFilePath")
    setupModelFile(filePath)
    assert 'testModel.json' in os.listdir(testDir)
    assert FreeCAD.ActiveDocument.modelFilePath.A1 == 'Path to model file:'
    assert FreeCAD.ActiveDocument.modelFilePath.B1 == filePath
    os.remove(filePath)
    FreeCAD.closeDocument('testDoc')


def test_getModel():
    myDoc = FreeCAD.newDocument('testDoc')
    testDir = os.path.join(repo_path(), 'tests')
    filePath = os.path.join(testDir, 'testModel.json')
    setupModelFile(filePath)
    myModel = getModel()
    testModel = qmt.Model()
    assert (myModel.modelDict == testModel.modelDict)
    os.remove(filePath)
    FreeCAD.closeDocument('testDoc')


def test_exportMeshed():
    myDoc = FreeCAD.newDocument('testDoc')
    testDir = os.path.join(repo_path(), 'tests')
    filePath = os.path.join(testDir, 'testExport.stl')
    from qmt.freecad.geomUtils import makeBB
    testBB = (-1., 1., -2., 2., -3., 3.)
    testShape = makeBB(testBB)
    exportMeshed(testShape, filePath)
    import Mesh
    Mesh.insert(filePath, 'testDoc')
    meshImport = myDoc.getObject("testExport")
    xMin = meshImport.Mesh.BoundBox.XMin
    xMax = meshImport.Mesh.BoundBox.XMax
    yMin = meshImport.Mesh.BoundBox.YMin
    yMax = meshImport.Mesh.BoundBox.YMax
    zMin = meshImport.Mesh.BoundBox.ZMin
    zMax = meshImport.Mesh.BoundBox.ZMax
    assert testBB == (xMin, xMax, yMin, yMax, zMin, zMax)
    os.remove(filePath)
    FreeCAD.closeDocument('testDoc')


def test_exportCAD():
    myDoc = FreeCAD.newDocument('testDoc')
    testDir = os.path.join(repo_path(), 'tests')
    filePath = os.path.join(testDir, 'testExport.step')
    from qmt.freecad.geomUtils import makeBB
    testBB = (-1., 1., -2., 2., -3., 3.)
    testShape = makeBB(testBB)
    exportCAD(testShape, filePath)
    import Part
    Part.insert(filePath, 'testDoc')
    CADImport = myDoc.getObject("testExport")
    xMin = CADImport.Shape.BoundBox.XMin
    xMax = CADImport.Shape.BoundBox.XMax
    yMin = CADImport.Shape.BoundBox.YMin
    yMax = CADImport.Shape.BoundBox.YMax
    zMin = CADImport.Shape.BoundBox.ZMin
    zMax = CADImport.Shape.BoundBox.ZMax
    assert testBB == (xMin, xMax, yMin, yMax, zMin, zMax)
    os.remove(filePath)

    with pytest.raises(ValueError) as err:
        exportCAD(testShape, 'not_a_step_file')
    assert 'does not end' in str(err.value)

    FreeCAD.closeDocument('testDoc')


def test_updateParams():
    '''Test updating of parameters in the FC gui.
       TODO: this should probably work with only 1 param (right now it doesn't).
    '''
    myDoc = FreeCAD.newDocument('testDoc')
    testDir = os.path.join(repo_path(), 'tests')
    filePath = os.path.join(testDir, 'testModel.json')
    setupModelFile(filePath)
    model = qmt.Model(modelPath=filePath)

    dummy = myDoc.addObject("Part::Box", "modelParams")
    model.modelDict['geometricParams']['length1'] = (2, 'freeCAD')
    updateParams()
    model.modelDict['geometricParams']['length2'] = (3, 'freeCAD')
    model.modelDict['geometricParams']['param3'] = (3, 'python')
    updateParams(model)
    model.modelDict['geometricParams']['param4'] = (3, 'unknown')
    model.saveModel()
    with pytest.raises(ValueError) as err:
        updateParams()
    assert 'Unknown geometric parameter' in str(err.value)

    fcFilePath = os.path.splitext(filePath)[0] + '.FCStd'
    myDoc.saveAs(fcFilePath)
    myDoc2 = FreeCAD.newDocument('testDoc2')
    myDoc2.load(fcFilePath)
    assert myDoc2.modelParams.length1 == 2
    assert myDoc2.modelParams.length2 == 3

    os.remove(fcFilePath)
    os.remove(filePath)
    FreeCAD.closeDocument('testDoc')
