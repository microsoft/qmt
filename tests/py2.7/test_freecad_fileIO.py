# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

"""Testing QMT file I/O functions."""


from __future__ import absolute_import, division, print_function

import pytest

from qmt.geometry.freecad.fileIO import *


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
    filePath = os.path.join(fix_testDir, 'tmp_testExport.stp')
    from qmt.geometry.freecad.geomUtils import makeBB
    testBB = (-1., 1.5, -2., 2.5, -3., 3.5)
    testShape = makeBB(testBB)
    exportCAD([testShape], filePath)

    Part.insert(filePath, fix_FCDoc.Name)
    CADImport = fix_FCDoc.getObject("tmp_testExport")

    import FreeCAD
    transBB = testBB[0:][::2] + testBB[1:][::2]  # reformat to FreeCAD representation
    refBB = FreeCAD.Base.BoundBox(*transBB)
    assert repr(CADImport.Shape.BoundBox) == repr(refBB)

    os.remove(filePath)

    with pytest.raises(TypeError) as err:
        exportCAD(testShape, 'dummy.stp')
    assert 'must be a list' in str(err.value)

    with pytest.raises(ValueError) as err:
        exportCAD([testShape], 'not_a_step_file')
    assert 'not a supported extension' in str(err.value)

def test_store_serial(fix_testDir, fix_FCDoc):
    '''Test serialisation to memory.'''
    # Serialise document
    obj = fix_FCDoc.addObject('App::FeaturePython', 'some_content')
    serial_data = store_serial(fix_FCDoc, lambda d, p: d.saveAs(p), 'fcstd')

    # Write to a file
    file_path = 'test.fcstd'
    import codecs
    data = codecs.decode(serial_data.encode(), 'base64')
    with open(file_path, 'wb') as of:
        of.write(data)

    # Load back and check
    doc = FreeCAD.newDocument('instance')
    FreeCAD.setActiveDocument('instance')
    doc.load(file_path)

    assert doc.getObject('some_content') is not None
