# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

"""Testing QMT file I/O functions."""

import pytest

from qmt.geometry.freecad.fileIO import *


def test_exportMeshed(datadir, fix_FCDoc):
    """Test mesh export/import."""
    filePath = os.path.join(datadir, "testExport.stl")
    from qmt.geometry.freecad.geomUtils import makeBB

    testBB = (-1.0, 1.0, -2.0, 2.0, -3.0, 3.0)
    testShape = makeBB(testBB)
    exportMeshed([testShape], filePath)
    Mesh.insert(filePath, "testDoc")
    meshImport = fix_FCDoc.getObject("testExport")
    xMin = meshImport.Mesh.BoundBox.XMin
    xMax = meshImport.Mesh.BoundBox.XMax
    yMin = meshImport.Mesh.BoundBox.YMin
    yMax = meshImport.Mesh.BoundBox.YMax
    zMin = meshImport.Mesh.BoundBox.ZMin
    zMax = meshImport.Mesh.BoundBox.ZMax
    assert testBB == (xMin, xMax, yMin, yMax, zMin, zMax)


def test_exportCAD(datadir, fix_FCDoc):
    """Test step export/import."""
    filePath = os.path.join(datadir, "tmp_testExport.stp")
    from qmt.geometry.freecad.geomUtils import makeBB

    testBB = (-1.0, 1.5, -2.0, 2.5, -3.0, 3.5)
    testShape = makeBB(testBB)
    exportCAD([testShape], filePath)

    Part.insert(filePath, fix_FCDoc.Name)
    CADImport = fix_FCDoc.getObject("tmp_testExport")

    import FreeCAD

    transBB = testBB[0:][::2] + testBB[1:][::2]  # reformat to FreeCAD representation
    refBB = FreeCAD.Base.BoundBox(*transBB)
    assert repr(CADImport.Shape.BoundBox) == repr(refBB)

    with pytest.raises(TypeError) as err:
        exportCAD(testShape, "dummy.stp")
    assert "must be a list" in str(err.value)

    with pytest.raises(ValueError) as err:
        exportCAD([testShape], "not_a_step_file")
    assert "not a supported extension" in str(err.value)
