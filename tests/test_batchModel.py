# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

"""Testing QMT batch model class."""


def test_genEmptyModelDict(fix_model):
    '''Guarantee the empty model specification. If it does: adjust here.'''
    d = fix_model.genEmptyModelDict()
    assert str(d) == "{'comsolInfo': {'zeroLevel': [None, None], 'surfaceIntegrals': {}, 'volumeIntegrals': {}}, 'buildOrder': {}, 'slices': {}, 'physicsSweep': {'sweepParts': {}, 'length': 1, 'type': 'sparse'}, 'geometricParams': {}, 'pathSettings': {}, '3DParts': {}, 'meshInfo': {}, 'geomSweep': {}, 'materials': {}, 'postProcess': {'tasks': {}, 'sweeps': {}}, 'jobSettings': {}}"


def test_genPhysicsSweep(fix_model):
    '''Test generation of physics sweeps.'''
    fix_model.addPart('dummyPart', 'dummySketch', 'extrude', 'dielectric',
                      material='SiO2', z0=-0.2, thickness=0.2, meshMaxSize=0.2)
    fix_model.genPhysicsSweep('dummyPart', 'param1', [1.1, 1.2, 1.3])
    assert fix_model.modelDict['physicsSweep']['sweepParts']['param1_dummyPart']['part'] == "dummyPart"
    assert fix_model.modelDict['physicsSweep']['sweepParts']['param1_dummyPart']['values'] == [1.1, 1.2, 1.3]


def test_genGeomSweep(fix_model):
    '''Check if geometry sweeps get added correctly by default.'''
    fix_model.genGeomSweep('d', [0.1, 0.2, 0.3])
    assert fix_model.modelDict['geomSweep']['d']['vals'] == '0.1, 0.2, 0.3'


def test_genSurfaceIntegral(fix_model):
    '''Test addition of surface integrals with default quantity 'V'.'''
    fix_model.genSurfaceIntegral('dummyPart')
    assert fix_model.modelDict['comsolInfo']['surfaceIntegrals']['dummyPart'] == ['V']


def test_genVolumeIntegral(fix_model):
    '''Test addition of volume integrals with default quantity 'V'.'''
    fix_model.genVolumeIntegral('dummyPart')
    assert fix_model.modelDict['comsolInfo']['volumeIntegrals']['dummyPart'] == ['V']


def test_setSimZero(fix_model):
    '''Test cosmetic zero levels for default property 'workFunction'.'''
    fix_model.setSimZero('dummyPart')
    assert fix_model.modelDict['comsolInfo']['zeroLevel'] == ['dummyPart', 'workFunction']


def test_genComsolInfo(fix_model):
    '''Check for correct COMSOL default information.'''
    fix_model.genComsolInfo()
    assert fix_model.modelDict['comsolInfo']['meshExport'] is None
    assert fix_model.modelDict['comsolInfo']['repairTolerance'] is None
    assert fix_model.modelDict['comsolInfo']['fileName'] == 'comsolModel'
    assert fix_model.modelDict['comsolInfo']['exportDir'] == 'solutions'


def test_addPart(fix_model):
    '''Test addition of geometric parts.'''
    fix_model.addPart('test_part_1', 'i_AlEtch_Polyline003_sketch', 'extrude',
                      'dielectric', material='SiO2', z0=-0.2, thickness=0.2,
                      meshMaxSize=0.2)
    # TODO: clean checks


def test_addJob(fix_model, fix_testDir):
    '''Test addition of jobs.'''
    import os
    jobPath = os.path.join(fix_testDir, 'testJob')
    fix_model.addJob(jobPath, jobSequence=['geoGen'], numCoresPerJob=1)
    assert fix_model.modelDict['jobSettings']['rootPath'] == jobPath
    # TODO: more checks
