# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

"""Testing QMT file I/O functions."""


from __future__ import absolute_import, division, print_function

import pytest

from qmt.geometry.freecad.fileIO import *


# ~ def test_setupModelFile(fix_testDir, fix_modelPath, fix_FCDoc):
    # ~ '''Test the setup function for model files.'''
    # ~ dummy = fix_FCDoc.addObject("Part::Box", "modelFilePath")
    # ~ setupModelFile(fix_modelPath)
    # ~ assert 'testModel.json' in os.listdir(fix_testDir)
    # ~ assert FreeCAD.ActiveDocument.modelFilePath.A1 == 'Path to model file:'
    # ~ assert FreeCAD.ActiveDocument.modelFilePath.B1 == fix_modelPath
    # ~ os.remove(fix_modelPath)


# ~ def test_getModel(fix_modelPath, fix_FCDoc, fix_model):
    # ~ '''Test model retrieval.'''
    # ~ setupModelFile(fix_modelPath)
    # ~ myModel = getModel()
    # ~ assert myModel.modelDict == fix_model.modelDict
    # ~ os.remove(fix_modelPath)


def test_exportMeshed(fix_testDir, fix_FCDoc):
    '''Test mesh export/import.'''
    filePath = os.path.join(fix_testDir, 'testExport.stl')
    from qmt.geometry.freecad.geomUtils import makeBB
    testBB = (-1., 1., -2., 2., -3., 3.)
    testShape = makeBB(testBB)
    exportMeshed(testShape, filePath)
    Mesh.insert(filePath, 'testDoc')
    meshImport = fix_FCDoc.getObject("testExport")
    xMin = meshImport.Mesh.BoundBox.XMin
    xMax = meshImport.Mesh.BoundBox.XMax
    yMin = meshImport.Mesh.BoundBox.YMin
    yMax = meshImport.Mesh.BoundBox.YMax
    zMin = meshImport.Mesh.BoundBox.ZMin
    zMax = meshImport.Mesh.BoundBox.ZMax
    assert testBB == (xMin, xMax, yMin, yMax, zMin, zMax)
    os.remove(filePath)


def test_exportCAD(fix_testDir, fix_FCDoc):
    '''Test step export/import.'''
    filePath = os.path.join(fix_testDir, 'testExport.step')
    from qmt.geometry.freecad.geomUtils import makeBB
    testBB = (-1., 1., -2., 2., -3., 3.)
    testShape = makeBB(testBB)
    exportCAD(testShape, filePath)
    Part.insert(filePath, 'testDoc')
    CADImport = fix_FCDoc.getObject("testExport")
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
    assert 'not a supported extension' in str(err.value)


# ~ def test_updateParams(fix_modelPath, fix_FCDoc):
    # ~ '''Test updating of parameters in the FC gui.
       # ~ TODO: this should probably work with only 1 param (right now it doesn't).
    # ~ '''
    # ~ setupModelFile(fix_modelPath)
    # ~ model = qmt.Model(modelPath=fix_modelPath)

    # ~ dummy = fix_FCDoc.addObject("Part::Box", "modelParams")
    # ~ model.modelDict['geometricParams']['length1'] = (2, 'freeCAD')
    # ~ updateParams()
    # ~ model.modelDict['geometricParams']['length2'] = (3, 'freeCAD')
    # ~ model.modelDict['geometricParams']['param3'] = (3, 'python')
    # ~ updateParams(model)
    # ~ model.modelDict['geometricParams']['param4'] = (3, 'unknown')
    # ~ model.saveModel()
    # ~ with pytest.raises(ValueError) as err:
        # ~ updateParams()
    # ~ assert 'Unknown geometric parameter' in str(err.value)

    # ~ fcFilePath = os.path.splitext(fix_modelPath)[0] + '.FCStd'
    # ~ fix_FCDoc.saveAs(fcFilePath)
    # ~ myDoc2 = FreeCAD.newDocument('testDoc2')
    # ~ myDoc2.load(fcFilePath)
    # ~ assert myDoc2.modelParams.length1 == 2
    # ~ assert myDoc2.modelParams.length2 == 3

    # ~ FreeCAD.closeDocument('testDoc2')
    # ~ os.remove(fcFilePath)
    # ~ os.remove(fix_modelPath)
