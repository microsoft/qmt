# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import os
import qmt
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


def test_genEmptyModelDict():
    '''Guarantee that the empty model doesn't change. If it does: update here.'''
    m = qmt.Model()
    d = m.genEmptyModelDict()
    assert(str(d) == "{'comsolInfo': {'zeroLevel': [None, None], 'surfaceIntegrals': {}, 'volumeIntegrals': {}}, 'buildOrder': {}, 'slices': {}, 'physicsSweep': {'sweepParts': {}, 'length': 1, 'type': 'sparse'}, 'geometricParams': {}, 'pathSettings': {}, '3DParts': {}, 'meshInfo': {}, 'geomSweep': {}, 'materials': {}, 'postProcess': {'tasks': {}, 'sweeps': {}}, 'jobSettings': {}}")


def test_genGeomSweep():
    m = qmt.Model()
    m.genGeomSweep('d', [0.1, 0.2, 0.3])
    assert m.modelDict['geomSweep']['d']['vals'] == '0.1, 0.2, 0.3'


def test_addJob():
    m = qmt.Model()
    jobPath = os.path.join(testDir, 'testJob')
    m.addJob(jobPath,jobSequence=['geoGen'],numCoresPerJob=1)
    assert(m.modelDict['jobSettings']['rootPath'] == jobPath)  # TODO: test in Model
