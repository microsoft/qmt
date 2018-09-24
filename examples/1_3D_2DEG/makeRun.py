# This is an example input deck to QMT - it constructs, runs, and
# does some analysis on a 2DEG-based design.

####################
####################

import os

import numpy as np

# Load the modules:
import qmt

# Path information -- change this to your configuration!
rootPath = 'PATH_TO_QMT/qmt/examples/1_3D_2DEG'
freeCADPath = os.path.join(rootPath, '2DEGFCDoc.FCStd')

# These are necessary for running MS Proprietary components, but are not
# needed for building the model
COMSOLExecPath = 'PATH_TO_COMSOL/Multiphysics/bin/win64/comsolclusterbatch'
COMSOLCompilePath = 'PATH_TO_COMSOL/Multiphysics/bin/win64/comsolcompile'
mpiPath = 'mpiexec'
pythonPath = 'PATH_TO_QMT_ENV/envs/qmt/python'
jdkPath = 'PATH_TO_JDK/jdk1.8.0_144'

numParallelJobs = 2

####################
####################

# Make the model file. This is a json file that handles all of the inter-module
# communication and also serves as a record regarding what has been run.
modelPath = os.path.join(rootPath, 'model.json')
runModel = qmt.Model(modelPath=modelPath)
runModel.modelDict = runModel.genEmptyModelDict()

# Import the materials we need:
matLib = qmt.Materials()
runModel.modelDict['materials'] = matLib.serialize_dict()

# Tell FreeCAD what to do with the names we passed in. All the units here are in microns.
# The simplest type of object directive is an extrude, which just takes one 2D
# shape and makes it into a 3D prism.
runModel.addPart('substrate', 'Rectangle', 'extrude', 'dielectric',
                 material='GaAs', z0=(-0.5 - 0.004 - 0.005),
                 thickness=0.5, meshMaxSize=0.1)
runModel.addPart('backBarrier', 'Rectangle', 'extrude', 'dielectric',
                 material='GaAs', z0=(- 0.004 - 0.005),
                 thickness=0.004, meshMaxSize=0.02)
runModel.addPart('quantumWell', 'Rectangle', 'extrude', 'semiconductor',
                 material='InAs', z0=(- 0.005),
                 thickness=0.005, meshMaxSize=0.02)
runModel.addPart('topBarrier', 'Rectangle', 'extrude', 'dielectric',
                 material='GaAs', z0=0.0,
                 thickness=0.011, meshMaxSize=0.02)
runModel.addPart('gateOxide', 'Rectangle', 'extrude', 'dielectric',
                 material='HfO2', z0=0.011,
                 thickness=0.04, meshMaxSize=0.02)
runModel.addPart('vacuum', 'Rectangle', 'extrude', 'dielectric',
                 material='air', z0=0.051,
                 thickness=0.5, meshMaxSize=0.2)

runModel.addPart(
    'AlFilm',
    'i_AlEtch_Polyline003_sketch',
    'extrude',
    'metalGate',
    material='Al',
    z0=0.011,
    thickness=0.0087,
    meshMaxSize=0.05,
    boundaryCondition={
        'voltage': 0.0})

runModel.addPart(
    'tunnelGate',
    'i_TopGate1_Polyline007_sketch',
    'extrude',
    'metalGate',
    material='Au',
    z0=0.051,
    thickness=0.03,
    meshMaxSize=0.05,
    boundaryCondition={
        'voltage': 0.0})

runModel.addPart(
    'wireGate',
    'i_TopGate1_Polyline008_sketch',
    'extrude',
    'metalGate',
    material='Au',
    z0=0.051,
    thickness=0.03,
    meshMaxSize=0.05,
    boundaryCondition={
        'voltage': 0.0})

# To perform a voltage sweep, we assign it to one of our geometry objects
# like so:
runModel.genPhysicsSweep(
    'tunnelGate', 'V', np.linspace(0.0, -1.0, 3), unit='V')

# Finalize the model:
runModel.setPaths(COMSOLExecPath=COMSOLExecPath,
                  COMSOLCompilePath=COMSOLCompilePath,
                  mpiPath=mpiPath,
                  pythonPath=pythonPath,
                  jdkPath=jdkPath,
                  freeCADPath=freeCADPath)

runModel.genComsolInfo(meshExport=None, fileName='comsolModel',
                       physics=['electrostatics'],
                       exportScalingVec=[0.5, 0.5, .5])

runModel.addJob(rootPath,
                jobSequence=['geoGen', 'comsolRun'],
                numParallelJobs=numParallelJobs,
                numCoresPerJob=4, comsolRunMode='debug')

# Save and execute the model:
runModel.saveModel()
jobHarness = qmt.Harness('model.json')
jobHarness.setupRun(genModelFiles=True)
jobHarness.runJob()
