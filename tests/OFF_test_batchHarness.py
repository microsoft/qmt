# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

"""Testing QMT batch harness class."""


import FreeCAD
import os
import shutil

import numpy as np
import pytest
from qmt.freecad.fileIO import setupModelFile, getModel

import qmt


def test_setupRun(fix_testDir, fix_modelPath, fix_FCDoc):
    '''The run instances must have the same root as the original model.
    '''
    modelPath = fix_modelPath
    setupModelFile(modelPath)

    m = getModel()
    jobPath = os.path.join(fix_testDir, 'testJob')
    m.addJob(jobPath, jobSequence=['geoGen'], numCoresPerJob=1)
    m.genGeomSweep('param1', [0.1, 0.2, 0.3])
    # TODO: agree to start counting with geo_0 even if we don't sweep
    m.saveModel()

    harn = qmt.Harness(modelPath)
    harn.setupRun()

    job0ModelPath = os.path.join(jobPath, 'geo_0', 'model.json')
    job2ModelPath = os.path.join(jobPath, 'geo_2', 'model.json')
    jm0 = qmt.Model(modelPath=job0ModelPath)
    jm2 = qmt.Model(modelPath=job2ModelPath)
    assert jm0.modelDict['jobSettings']['rootPath'] == jobPath
    assert jm2.modelDict['jobSettings']['rootPath'] == jobPath

    os.remove(modelPath)
    shutil.rmtree(os.path.join(jobPath, 'geo_0'))
    shutil.rmtree(os.path.join(jobPath, 'geo_1'))
    shutil.rmtree(os.path.join(jobPath, 'geo_2'))
    os.rmdir(jobPath)  # use os.ramdir for safety if jobPath == rootPath


def test_runJob(fix_testDir, fix_modelPath, fix_FCDoc):
    '''Check results of run: here only geoGen (generated FreeCAD model files).
    '''
    modelPath = fix_modelPath
    setupModelFile(modelPath)

    m = getModel()
    jobPath = os.path.join(fix_testDir, 'testJob')
    m.addJob(jobPath, jobSequence=['geoGen'], numCoresPerJob=1)
    m.genGeomSweep('d', [0.1, 0.2, 0.3])
    m.setPaths(freeCADPath=os.path.join(
               fix_testDir, '..', 'examples', '1_3D_2DEG', '2DEGFCDoc.FCStd'))
    # ~ m.addPart('tunnelGate','i_TopGate1_Polyline007_sketch','extrude','metalGate',
                 # ~ material = 'Au',z0=0.051,thickness=0.03,meshMaxSize=0.05, boundaryCondition={'voltage' : 0.0})
    m.saveModel()

    harn = qmt.Harness(modelPath)
    harn.setupRun()
    harn.runJob()

    fc_job2 = os.path.join(jobPath, 'geo_2', 'freeCADModel.FCStd')
    myDoc2 = FreeCAD.newDocument('testDoc2')
    myDoc2.load(fc_job2)
    assert myDoc2.modelParams.d == 0.3
    assert np.isclose(myDoc2.getObject("i_TopGate1_Polyline007_sketch").Constraints[11].Value, 0.475642)

    # Check for illegal steps
    m.addJob(jobPath, jobSequence=['wrongStep'], numCoresPerJob=1)
    m.saveModel()
    harn = qmt.Harness(modelPath)
    harn.setupRun()
    with pytest.raises(ValueError) as err:
        harn.runJob()
    assert 'Job step is not defined' in str(err.value)

    os.remove(modelPath)
    shutil.rmtree(os.path.join(jobPath, 'geo_0'))  # TODO: glob geo_*
    shutil.rmtree(os.path.join(jobPath, 'geo_1'))
    shutil.rmtree(os.path.join(jobPath, 'geo_2'))
    os.rmdir(jobPath)  # use os.ramdir for safety if jobPath == rootPath
