# This is an example input deck to QMT - it constructs, runs, and 
# does some analysis on a 2DEG-based design. 

####################
####################

# Load the modules:
import qmt
import numpy as np
import os

# Path information -- change this to your configuration!
rootPath = 'C:/Users/jogambl/Documents/repositories/qmt/examples/1_3D_2DEG'
freeCADPath = os.path.join(rootPath, '2DEGFCDoc.FCStd')

# These are necessary for running MS Proprietary components, but are not needed for building the model
COMSOLExecPath = '\\\\gcr\\scratch\\rr1\\jogambl\\apps\\COMSOL\\COMSOL53\\Multiphysics\\bin\\win64\\comsolclusterbatch'
COMSOLCompilePath = '\\\\gcr\\scratch\\rr1\\jogambl\\apps\\COMSOL\\COMSOL53\\Multiphysics\\bin\\win64\\comsolcompile'
mpiPath = 'mpiexec'
pythonPath = '\\\\gcr\\scratch\\rr1\\jogambl\\apps\\Anaconda2\\python'
jdkPath = '\\\\gcr\\scratch\\rr1\\jogambl\\java_portable'

####################
####################


# Make the model file. This is a json file that handles all of the inter-module
# communication and also serves as a record regarding what has been run.
modelPath = os.path.join(rootPath, 'model.json')
runModel = qmt.Model(modelPath=modelPath)
runModel.modelDict = runModel.genEmptyModelDict()

# Import the materials we need:
rootDir = qmt.__file__[:-12]
matLib = qmt.Materials(matPath=rootDir + '/materials.json')
matLib.load()
runModel.modelDict['materials'] = matLib.serializeDict()


# Tell FreeCAD what to do with the names we passed in. All the units here are in microns.
# The simplest type of object directive is an extrude, which just takes one 2D
# shape and makes it into a 3D prism.


runModel.addPart('substrate','Rectangle','extrude','dielectric',
                 material = 'In81Al19As',z0=(-0.5 - 0.004 - 0.005),
                 thickness=0.5,meshMaxSize=0.2)
runModel.addPart('backBarrier','Rectangle','extrude','dielectric',
                 material = 'In81Ga19As',z0=(- 0.004 - 0.005),
                 thickness=0.004,meshMaxSize=0.2)
runModel.addPart('quantumWell','Rectangle','extrude','semiconductor',
                 material = 'InAs',z0=(- 0.005),
                 thickness=0.005,meshMaxSize=0.2)                
runModel.addPart('topBarrier','Rectangle','extrude','dielectric',
                 material = 'In81Ga19As',z0=0.0,
                 thickness=0.011,meshMaxSize=0.2)    
runModel.addPart('gateOxide','Rectangle','extrude','dielectric',
                 material = 'HfO2',z0=0.011,
                 thickness=0.04,meshMaxSize=0.2)  
runModel.addPart('vacuum','Rectangle','extrude','dielectric',
                 material = 'air',z0=0.051,
                 thickness=0.5,meshMaxSize=0.2)                   

runModel.addPart('AlFilm','i_AlEtch_Polyline003_sketch','extrude','dielectric',
                 material = 'Al',z0=0.011,thickness=0.0087,meshMaxSize=0.2)

runModel.addPart('tunnelGate','i_TopGate1_Polyline007_sketch','extrude','dielectric',
                 material = 'Au',z0=0.051,thickness=0.03,meshMaxSize=0.2)

runModel.addPart('wireGate','i_TopGate1_Polyline008_sketch','extrude','semiconductor',
                 material = 'Au',z0=0.051,thickness=0.03,meshMaxSize=0.2)

# Define a cut in the xz-plane for 2D postprocessing
# cross_section = {'crossSection': {'axis': (0, 1, 0), 'd': 0.}}
# runModel.modelDict['freeCADInfo']['crossSec1'] = cross_section

# Geometry sweeps are represented in two distinct ways:
# runModel.genGeomSweep('d',[0.0,0.05],type='freeCAD') # variables defined in the FreeCAD GUI
# runModel.genGeomSweep('Lz',[0.030,0.04],type='python') # Variables defined in the script above

# To perform a voltage sweep, we assign it to one of our geometry objects like so:
runModel.genPhysicsSweep('tunnelGate','V',np.linspace(0.0, -1.0, 3),unit='V') 
# We can also sweep other physical quantities connected to geometry objects:
runModel.genPhysicsSweep('quantumWell', 'bandOffset', [0., 0.1,0.3], unit='eV', dense=True)

# # Alternatively, this would do a sparse sweep:
# runModel.genPhysicsSweep('Rectangle_quantumWell', 'bandOffset', [0., 0.1, 0.2], unit='eV', dense=False)

# Next, let's set up some postprocessing tasks:
# qwell = 'stlParts/Rectangle_quantumWell.stl'
# x = {'min': {'bbox': qwell, 'anchor': 'left', 'offset': 0.2},
#      'max': {'bbox': qwell, 'anchor': 'right', 'offset': -0.2},
#      'steps': 400}
# y = {'min': {'bbox': qwell, 'anchor': 'left', 'offset': 0.2},
#      'max': {'bbox': qwell, 'anchor': 'right', 'offset': -0.2},
#      'steps': 400}
# # Plot the potential at the top boundary of the well
# z = {'value': {'bbox': qwell, 'anchor': 'right'}}
# runModel.addPlotPotentialTask(x, y, z, name=None, plot_format=None)

# # 2D cross section: simulation region should include the named parts
# cut_region = {'boundingBox': {'regions': ['Rectangle_quantumWell_section_0',
#                                           'i_TopGate1_Polyline007_sketch_0_section_0',
#                                           'Rectangle_backBarrier_section_0']}}
# runModel.addThomasFermi2dTask(cut_region, grid={'steps': 200})  # 200 steps in x and y direction

# # Finalize the model:
runModel.setPaths(COMSOLExecPath = COMSOLExecPath,\
                  COMSOLCompilePath=COMSOLCompilePath,\
                  mpiPath = mpiPath,\
                  pythonPath =pythonPath,\
                  jdkPath=jdkPath,\
                  freeCADPath = freeCADPath)

runModel.genComsolInfo(meshExport=None, fileName='comsolModel')
# Comment this in to run with proprietary components:
# runModel.addJob(rootPath,\
#                 jobSequence=['geoGen','comsolRun','postProc'],numCores=1)

runModel.addJob(rootPath,\
                jobSequence=['geoGen'])

# Save and execute the model:
runModel.saveModel()
jobHarness = qmt.Harness('model.json')
jobHarness.setupRun(genModelFiles=True)
jobHarness.runJob()

