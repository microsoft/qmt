# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import os
import qmt
import pytest
import shutil
from qmt.freecad.fileIO import *

def setup_function(function):
    global myDoc
    global testDir
    global modelPath
    myDoc = FreeCAD.newDocument('testDoc')
    rootPath = os.path.join(os.path.dirname(qmt.__file__), os.pardir)
    testDir = os.path.join(rootPath, 'tests')
    modelPath = os.path.join(testDir, 'testModel.json')


def teardown_function(function):
    FreeCAD.closeDocument('testDoc')


def manual_testing(function):
    setup_function(function)
    function()
    teardown_function(function)


def test_setupRun():
    '''The run instances must have the same root as the original model.
    '''
    setupModelFile(modelPath)

    m = getModel()
    jobPath = os.path.join(testDir, 'testJob')
    m.addJob(jobPath,jobSequence=['geoGen'],numCoresPerJob=1)
    m.genGeomSweep('param1', [0.1, 0.2, 0.3])
    # TODO: agree to start counting with geo_0 even if we don't sweep
    m.saveModel()

    harn = qmt.Harness(modelPath)
    harn.setupRun()

    job0ModelPath = os.path.join(jobPath, 'geo_0', 'model.json')
    job2ModelPath = os.path.join(jobPath, 'geo_2', 'model.json')
    jm0 = qmt.Model(modelPath=job0ModelPath)
    jm2 = qmt.Model(modelPath=job2ModelPath)
    assert(jm0.modelDict['jobSettings']['rootPath'] == jobPath)
    assert(jm2.modelDict['jobSettings']['rootPath'] == jobPath)

    os.remove(modelPath)
    shutil.rmtree(os.path.join(jobPath, 'geo_0'))
    shutil.rmtree(os.path.join(jobPath, 'geo_1'))
    shutil.rmtree(os.path.join(jobPath, 'geo_2'))
    os.rmdir(jobPath)  # safety if jobPath == rootPath

def test_runJob():
    '''Check results of run: here only geoGen (generated FreeCAD model files).
    '''
    setupModelFile(modelPath)

    m = getModel()
    jobPath = os.path.join(testDir, 'testJob')
    m.addJob(jobPath,jobSequence=['geoGen'],numCoresPerJob=1)
    m.genGeomSweep('d', [0.1, 0.2, 0.3])
    m.setPaths(freeCADPath = os.path.join(testDir, '2DEG_example.FCStd'))
    m.saveModel()

    harn = qmt.Harness(modelPath)
    harn.setupRun()
    harn.runJob()

    fc_job2 = os.path.join(jobPath, 'geo_2', 'freeCADModel.FCStd')
    myDoc2 = FreeCAD.newDocument('testDoc2')
    myDoc2.load(fc_job2)
    assert myDoc2.modelParams.d == 0.3

    # Check for illegal steps
    m.addJob(jobPath,jobSequence=['wrongStep'],numCoresPerJob=1)
    m.saveModel()
    harn = qmt.Harness(modelPath)
    harn.setupRun()
    with pytest.raises(ValueError) as err:
        harn.runJob()
    assert 'Job step is not defined' in str(err.value)

    os.remove(modelPath)
    shutil.rmtree(os.path.join(jobPath, 'geo_0'))
    shutil.rmtree(os.path.join(jobPath, 'geo_1'))
    shutil.rmtree(os.path.join(jobPath, 'geo_2'))
    os.rmdir(jobPath)  # safety if jobPath == rootPath

manual_testing(test_runJob)
