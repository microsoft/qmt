# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import os
import qmt
from qmt.freecad.fileIO import *

def setup_function(function):
    global myDoc
    global testDir
    global model
    myDoc = FreeCAD.newDocument('testDoc')
    rootPath = os.path.join(os.path.dirname(qmt.__file__), os.pardir)
    testDir = os.path.join(rootPath, 'tests')
    model = qmt.Model()


def teardown_function(function):
    FreeCAD.closeDocument('testDoc')


def manual_testing(function):
    setup_function(function)
    function()
    teardown_function(function)


def test_genEmptyModelDict():
    '''Guarantee that the empty model doesn't change. If it does: update here.'''
    d = model.genEmptyModelDict()
    assert(str(d) == "{'comsolInfo': {'zeroLevel': [None, None], 'surfaceIntegrals': {}, 'volumeIntegrals': {}}, 'buildOrder': {}, 'slices': {}, 'physicsSweep': {'sweepParts': {}, 'length': 1, 'type': 'sparse'}, 'geometricParams': {}, 'pathSettings': {}, '3DParts': {}, 'meshInfo': {}, 'geomSweep': {}, 'materials': {}, 'postProcess': {'tasks': {}, 'sweeps': {}}, 'jobSettings': {}}")


def test_genPhysicsSweep():
    '''Test generation of physics sweeps.'''
    model.genPhysicsSweep('dummyPart', 'param1', [1.1, 1.2, 1.3])
    assert model.modelDict['physicsSweep']['sweepParts']['param1_dummyPart']['part'] == "dummyPart"
    assert model.modelDict['physicsSweep']['sweepParts']['param1_dummyPart']['values'] == [1.1, 1.2, 1.3]


def test_genGeomSweep():
    '''Check if geometry sweeps get added correctly with default FreeCAD type.'''
    model.genGeomSweep('d', [0.1, 0.2, 0.3])
    assert model.modelDict['geomSweep']['d']['vals'] == '0.1, 0.2, 0.3'


def test_genSurfaceIntegral():
    '''Test addition of surface integrals with default quantity 'V'.'''
    model.genSurfaceIntegral('dummyPart')
    assert model.modelDict['comsolInfo']['surfaceIntegrals']['dummyPart'] == ['V']


def test_genVolumeIntegral():
    '''Test addition of volume integrals with default quantity 'V'.'''
    model.genVolumeIntegral('dummyPart')
    assert model.modelDict['comsolInfo']['volumeIntegrals']['dummyPart'] == ['V']


def test_setSimZero():
    '''Test setting of cosmetic zero levels for default property 'workFunction'.'''
    model.setSimZero('dummyPart')
    assert model.modelDict['comsolInfo']['zeroLevel'] == ['dummyPart','workFunction']

def test_genComsolInfo():
    model.genComsolInfo()
    assert model.modelDict['comsolInfo']['meshExport'] == None
    assert model.modelDict['comsolInfo']['repairTolerance'] == None
    assert model.modelDict['comsolInfo']['fileName'] == 'comsolModel'
    assert model.modelDict['comsolInfo']['exportDir'] == 'solutions'


def test_addPart():




def test_addJob():
    jobPath = os.path.join(testDir, 'testJob')
    model.addJob(jobPath,jobSequence=['geoGen'],numCoresPerJob=1)
    assert(model.modelDict['jobSettings']['rootPath'] == jobPath)
