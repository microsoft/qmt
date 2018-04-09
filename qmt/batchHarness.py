# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

#
# This file coordinates the deployment of a batch job among toolchain component.
# The geoGen component is included in this release. The run and 
#

from __future__ import absolute_import, division, print_function
from six import iteritems
import qmt as QMT
import os
import sys
import glob
import subprocess
import itertools
from copy import deepcopy
import time


class Harness:
    def __init__(self, jsonPath):
        ''' Class to run a batch 3D job on the cluster. 

            Parameters
            ----------
            jsonPath : str
                Path to the model json file used to build the run
        '''
        self.jsonPath = os.path.abspath(jsonPath)
        self.model = QMT.Model(self.jsonPath)
        self.modelFilePaths = []
        self.model.loadModel()

    def setupRun(self, genModelFiles=True):
        ''' Set up the folder structure of a run, broken out by the geomSweep
            specified in the json file.
        '''
        self.rootPath = self.model.modelDict['jobSettings']['rootPath']
        if not os.path.isdir(self.rootPath):
            os.mkdir(self.rootPath)
        geoSweepKeys = self.model.modelDict['geomSweep'].keys()
        instanceLists = []
        for geoSweepKey in geoSweepKeys:
            numInstances = len(self.model.modelDict['geomSweep'][geoSweepKey]['vals'].split(','))
            valIDs = range(numInstances)
            instanceLists += [valIDs]
        prodInstanceKeys = list(itertools.product(*instanceLists))
        for prodInstance in prodInstanceKeys:
            folderPath = 'geo_' + '_'.join(map(str, list(prodInstance)))
            if not os.path.isdir(self.rootPath + '/' + folderPath):
                os.mkdir(self.rootPath + '/' + folderPath)
            runPath = self.rootPath + '/' + folderPath
            tempModel = QMT.Model(runPath + '/model.json')
            self.modelFilePaths += [runPath + '/model.json']
            tempModel.modelDict = deepcopy(self.model.modelDict)
            tempModel.modelDict['geomSweep'] = {}  # Also reset this
            for index, name in zip(prodInstance, self.model.modelDict['geomSweep'].keys()):
                # Populate the geo parameter names:
                paramName = name
                paramType = self.model.modelDict['geomSweep'][name]['type']  # freeCAD or python
                paramValIndex = index
                paramValsStr = self.model.modelDict['geomSweep'][paramName]['vals']
                paramValsList = paramValsStr.split(',')
                paramVal = paramValsList[paramValIndex]
                tempModel.modelDict['geometricParams'][paramName] = (paramVal, paramType)
                # Populate the geo sweep (just one point, for bookkeeping purposes):
                tempModel.genGeomSweep(paramName, [paramVal], type=paramType)
            tempModel.modelDict['pathSettings']['dirPath'] = runPath
            if genModelFiles:
                tempModel.saveModel()

    def runJob(self):
        ''' Run the batch job.
        '''
        for modelFilePath in self.modelFilePaths:  # For now, this is the serial part
            for jobStep in self.model.modelDict['jobSettings']['jobSequence']:
                if jobStep == 'geoGen':
                    self.runBatchGeoGen(modelFilePath)
                elif jobStep == 'comsolRun':
                    start = time.time()
                    self.runBatchCOMSOLRun(modelFilePath)
                    end = time.time()
                    print('Elapsed time is {0} s.'.format(end - start))
                elif jobStep == 'postProc':
                    self.runBatchPostProc(modelFilePath)
                else:
                    raise ValueError('Job step is not defined!')

    def runBatchGeoGen(self, modelFilePath):
        ''' Run batch geometry generation.
        '''
        # Import the FreeCAD functions we will need:
        import FreeCAD
        from qmt.freecad import modelBuilder, build2DGeo, buildCrossSection

        # Load the model:
        myModel = QMT.Model(modelPath=modelFilePath)
        myModel.loadModel()
        dirPath = myModel.modelDict['pathSettings']['dirPath']
        FCDocPath = myModel.modelDict['pathSettings']['freeCADPath']
        FreeCAD.openDocument(FCDocPath)
        # Build the model
        buildModel = modelBuilder(passModel=myModel)
        for i in range(len(myModel.modelDict['buildOrder'])):
            partName = myModel.modelDict['buildOrder'][str(i)]
            totalParts = len(myModel.modelDict['buildOrder'])
            print('('+str(i+1)+'/'+str(totalParts)+') building part '+partName+'...')
            buildModel.buildPart(partName)
        cadDirPath = dirPath + '/cadParts'
        stlDirPath = dirPath+'/stlParts'
        if not os.path.isdir(cadDirPath):
            os.mkdir(cadDirPath)
        if not os.path.isdir(stlDirPath):
            os.mkdir(stlDirPath)
        buildModel.exportBuiltParts(stepFileDir=dirPath + '/cadParts',stlFileDir=dirPath+'/stlParts')
        buildModel.saveFreeCADState(dirPath+'/freeCADModel.FCStd')
        
        # Now that we have rendered the 3D objects, we want to draw any
        # necessary 2D cross sections as 2D cuts:
        for sliceName, sliceData in iteritems(myModel.modelDict['slices']):
            if sliceData['sliceInfo'].get('crossSection'):
                parts = buildCrossSection(sliceData['sliceInfo'], passModel=myModel)
            else:
                parts = build2DGeo(passModel=myModel)
            sliceData['parts'] = parts

        myModel.saveModel()



    def runBatchCOMSOLRun(self, modelFilePath):
        ''' Run batch COMSOL run. This requires proprietary components to be 
        installed.
        '''
        from qms import comsol
        myModel = QMT.Model(modelPath=modelFilePath)
        myModel.loadModel()
        numCoresPerJob = myModel.modelDict['jobSettings']['numCoresPerJob']
        numParallelJobs = myModel.modelDict['jobSettings']['numParallelJobs']
        comsolExecPath = myModel.modelDict['pathSettings']['COMSOLExecPath']
        mpiPath = myModel.modelDict['pathSettings']['mpiPath']
        myComsolModel = comsol.ComsolModel(modelFilePath, run_mode=self.model.modelDict['jobSettings']['comsolRunMode'])
        print('Compiling COMSOL java file...')
        myComsolModel._compile()
        # Make the export directory if it doesn't exist:
        comsolSolsPath = myModel.modelDict['pathSettings']['dirPath'] + \
                         '/' + myModel.modelDict['comsolInfo']['exportDir']
        if not os.path.isdir(comsolSolsPath):
            os.mkdir(comsolSolsPath)
        comsolModelPath = '\"' + myModel.modelDict['pathSettings'][
            'dirPath'] + '/' + myComsolModel.name + '.class' + '\"'

        # Initiate the COMSOL run:
        # comsolCommand = [mpiPath, '-n', str(numCores), comsolExecPath, '-nosave', '-np', '1', '-inputFile', comsolModelPath]
        # The above doesn't work with double quotes in the path names
        
        # Note on cores: COMSOL uses the notation "computational node" to specify a shared
        # memory single job. The -np flag is used to set the number of cores used by each, 
        # and it shouldn't exceed the number of physical cores on a machine. Apparently, 
        # the MPI -n flag should be the number of computational nodes, not the number of total
        # cores.'
        if not self.model.modelDict['jobSettings']['comsolRunMode'] == 'batch': # save the resulting file for manual inspection
            comsolCommand = mpiPath + ' -n ' + str(numParallelJobs) + ' \"' + comsolExecPath +\
            '\" -np ' + str(numCoresPerJob)+ ' -inputFile ' + comsolModelPath
        else:
            comsolCommand = mpiPath + ' -n ' + str(numParallelJobs) + ' \"' + comsolExecPath +\
            '\" -nosave -np ' +str(numCoresPerJob)+ ' -inputFile ' + comsolModelPath
        comsolLogName = myModel.modelDict['pathSettings']['dirPath'] + '/comsolLog.txt'
        comsolErrName = myModel.modelDict['pathSettings']['dirPath'] + '/comsolErr.txt'
        # Log file for COMSOL run:
        comsolLog = open(comsolLogName, 'w')
        comsolErr = open(comsolErrName, 'w')

        print('Running {}...'.format(comsolCommand))
        comsolRun = subprocess.Popen(comsolCommand, stdout=comsolLog, stderr=comsolErr)
        print('Starting COMSOL run...')
        # Determine the number of voltages we are expecting.
        numVoltages = myModel.modelDict['physicsSweep']['length']
        resultFileBase = '{}/{}_export'.format(comsolSolsPath,
                                               myModel.modelDict['comsolInfo']['fileName'])
        eigenFileBase = '{}/{}_eigvals'.format(comsolSolsPath,
                                               myModel.modelDict['comsolInfo']['fileName'])
        while True:
            if comsolRun.poll() != None:  # If the run is done, tag it as complete
                print('COMSOL run finshed!')
                break
            else:
                fracComplete = 1.0
                if 'electrostatics' in self.model.modelDict['comsolInfo']['physics']:
                    solsList = glob.glob(resultFileBase + '*.txt')
                    fracComplete = min(len(solsList) / float(numVoltages),fracComplete)
                if ('schrodinger' in self.model.modelDict['comsolInfo']['physics']) or ('bdg' in self.model.modelDict['comsolInfo']['physics']):
                    eigenList = glob.glob(eigenFileBase + '*.txt')
                    fracComplete = min(len(eigenList) / float(numVoltages),fracComplete)
                print('... ' + str(fracComplete))
                time.sleep(5.)
                if len(solsList) >= numVoltages:  # we are done!
                    print('COMSOL run finished, but failed to exit!')
                    print('Closing it in 10 seconds...')
                    sys.stdout.flush()
                    time.sleep(10.)
                    comsolRun.terminate()
                    break
        comsolLog.close()
        comsolErr.close()

    def runBatchPostProc(self, modelFilePath):
        ''' Run batch post-processing. This requires proprietary components
        to be installed.
        '''
        import qms as QMTP
        numCores = self.model.modelDict['jobSettings']['numCoresPerJob'] \
                   * self.model.modelDict['jobSettings']['numParallelJobs']
        mpiexecName = self.model.modelDict['pathSettings']['mpiPath']
        pythonName = self.model.modelDict['pathSettings']['pythonPath']
        batchPostProcpath = QMTP.postProcessing.__file__.rstrip('__init__.pyc') + 'batchPostProc.py'
        mpiCmd = [mpiexecName, '-n', str(numCores)]
        pythonCmd = [pythonName, batchPostProcpath, '\"' + modelFilePath + '\"']
        print('Running {}...'.format(mpiCmd + pythonCmd))
        subprocess.check_call(mpiCmd + pythonCmd)
