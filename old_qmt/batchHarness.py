# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

#
# This file coordinates the deployment of a batch job among toolchain component.
# The geoGen component is included in this release. The run and
#

from __future__ import absolute_import, division, print_function

import glob
import itertools
import os
import subprocess
import sys
import time
from copy import deepcopy

from six import iteritems, text_type

import qmt as QMT


class Harness:
    def __init__(self, jsonPath, os=None):
        """Class to run a batch 3D job on the cluster.

        Parameters
        ----------
        jsonPath : str
            Path to the model json file used to build the run
        os : str
            Either 'linux' or 'windows'. The default None detects
            the OS from sys.platform.
        """
        try:
            self.jsonPath = os.path.abspath(jsonPath)
        except AttributeError:
            self.jsonPath = jsonPath
        self.model = QMT.Model(self.jsonPath)
        self.modelFilePaths = []
        self.model.loadModel()
        if os is None:
            if 'linux' in sys.platform:
                os = 'linux'
            elif 'win' in sys.platform:
                os = 'windows'
            else:
                raise RuntimeError(
                    'Operating system {} is not supported.'.format(
                        sys.platform))
        if os not in ['linux', 'windows']:
            raise ValueError('os must be either "windows" or "linux"!')
        self.os = os

    @staticmethod
    def convert_unicode_to_ascii(dic):
        """Convert any unicode entries in the dict."""
        for key, value in dic.iteritems():
            if isinstance(key, text_type) or isinstance(value, text_type):
                newkey = key.encode('ascii', 'ignore')
                newvalue = value.encode('ascii', 'ignore')
                del dic[key]
                dic[newkey] = newvalue
        return dic

    def setupRun(self, genModelFiles=True):
        """Set up the folder structure of a run, broken out by the geomSweep
        specified in the json file.
        """
        model_dict = self.model.modelDict
        self.rootPath = model_dict['jobSettings']['rootPath']
        if not os.path.isdir(self.rootPath):
            os.mkdir(self.rootPath)
        geoSweepKeys = model_dict['geomSweep'].keys()
        instanceLists = []
        for geoSweepKey in geoSweepKeys:
            numInstances = len(
                model_dict['geomSweep'][geoSweepKey]['vals'].split(','))
            valIDs = range(numInstances)
            instanceLists.append(valIDs)
        for prodInstance in itertools.product(*instanceLists):
            folderPath = 'geo_' + '_'.join(map(str, list(prodInstance)))
            if not os.path.isdir(self.rootPath + '/' + folderPath):
                os.mkdir(self.rootPath + '/' + folderPath)
            runPath = self.rootPath + '/' + folderPath
            tempModel = QMT.Model(runPath + '/model.json')
            self.modelFilePaths += [runPath + '/model.json']
            tempModel.modelDict = deepcopy(model_dict)
            tempModel.modelDict['geomSweep'] = {}  # Also reset this
            for index, name in zip(
                    prodInstance, model_dict['geomSweep'].keys()):
                # Populate the geo parameter names:
                paramName = name
                # freeCAD or python
                paramType = model_dict['geomSweep'][name]['type']
                paramValIndex = index
                paramValsStr = model_dict['geomSweep'][paramName][
                    'vals']
                paramValsList = paramValsStr.split(',')
                paramVal = paramValsList[paramValIndex]
                tempModel.modelDict['geometricParams'][paramName] = (
                    paramVal, paramType)
                # Populate the geo sweep (just one point, for bookkeeping
                # purposes):
                tempModel.genGeomSweep(paramName, [paramVal], type=paramType)
            tempModel.modelDict['pathSettings']['dirPath'] = runPath
            if genModelFiles:
                tempModel.saveModel()

    def runJob(self):
        """Run the batch job."""
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
        """Run batch geometry generation."""
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
            print('(' + str(i + 1) + '/' + str(totalParts) +
                  ') building part ' + partName + '...')
            buildModel.buildPart(partName)
        cadDirPath = dirPath + '/cadParts'
        stlDirPath = dirPath + '/stlParts'
        if not os.path.isdir(cadDirPath):
            os.mkdir(cadDirPath)
        if not os.path.isdir(stlDirPath):
            os.mkdir(stlDirPath)
        buildModel.exportBuiltParts(
            stepFileDir=dirPath + '/cadParts',
            stlFileDir=dirPath + '/stlParts')
        buildModel.saveFreeCADState(dirPath + '/freeCADModel.FCStd')

        # Now that we have rendered the 3D objects, we want to draw any
        # necessary 2D cross sections as 2D cuts:
        for sliceName, sliceData in iteritems(myModel.modelDict['slices']):
            if sliceData['sliceInfo'].get('crossSection'):
                parts = buildCrossSection(
                    sliceData['sliceInfo'], passModel=myModel)
            else:
                parts = build2DGeo(passModel=myModel)
            sliceData['parts'] = parts

        myModel.saveModel()

    def runBatchCOMSOLRun(self, modelFilePath):
        """Run batch COMSOL run. This requires proprietary components to be
        installed.
        """
        import qms
        from qms import comsol
        from qms.postProcessing import dataProcessing

        myModel = QMT.Model(modelPath=modelFilePath)
        myModel.loadModel()

        # Aliases
        model_dict = myModel.modelDict
        path_settings = model_dict['pathSettings']
        job_settings = model_dict['jobSettings']

        numNodes = job_settings['numNodes']
        numJobsPerNode = job_settings['numJobsPerNode']
        numCoresPerJob = job_settings['numCoresPerJob']
        hostFile = job_settings['hostFile']
        numParallelJobs = numNodes * numJobsPerNode
        comsolExecPath = path_settings['COMSOLExecPath']
        comsolCompilePath = path_settings['COMSOLCompilePath']
        jdkPath = path_settings['jdkPath']
        mpiPath = path_settings['mpiPath']
        folder = path_settings['dirPath']
        name = model_dict['comsolInfo']['fileName']
        myComsolModel = comsol.ComsolModel(
            modelFilePath, run_mode=self.model.modelDict['jobSettings']
            ['comsolRunMode'])

        print('Compiling COMSOL java file...')
        myComsolModel._write()
        if self.os == 'windows':
            compileList = [comsolCompilePath, '-jdkroot',
                           jdkPath, '{0}/{1}.java'.format(folder, name)]
        elif self.os == 'linux':
            compileList = [comsolExecPath, 'compile',
                           '{0}/{1}.java'.format(folder, name)]
        print('Running ' + ' '.join(compileList))
        subprocess.check_call(compileList)

        # If we are on the Linux cluster and not run by SLURM, we need to
        # enable the launcher hack
        slurmRun = self.os == 'linux' and 'SLURM_JOB_NODELIST' in os.environ
        my_env = os.environ.copy()
        if self.os == 'linux' and not slurmRun:
            launcherPath = os.path.dirname(qms.__file__) + '/launch.py'
            my_env['I_MPI_HYDRA_BOOTSTRAP_EXEC'] = launcherPath  # for Intel MPI
            my_env['HYDRA_LAUNCHER_EXEC'] = launcherPath  # for MPICH

        # Convert any unicode entries in the env
        my_env = self.convert_unicode_to_ascii(my_env)

        # Make the export directory if it doesn't exist:
        comsolSolsPath = path_settings['dirPath'] + \
            '/' + model_dict['comsolInfo']['exportDir']
        if not os.path.isdir(comsolSolsPath):
            os.mkdir(comsolSolsPath)
        if self.os == 'windows':
            comsolModelPath = ('\"'
                               + path_settings['dirPath']
                               + '/'
                               + myComsolModel.name
                               + '.class'
                               + '\"')
        elif self.os == 'linux':
            comsolModelPath = (path_settings['dirPath']
                               + '/'
                               + myComsolModel.name
                               + '.class')
        # Initiate the COMSOL run:
        # comsolCommand = [mpiPath, '-n', str(numCores), comsolExecPath, '-nosave', '-np', '1', '-inputFile', comsolModelPath]
        # The above doesn't work with double quotes in the path names

        # Note on cores: COMSOL uses the notation "computational node" to specify a shared
        # memory single job. The -np flag is used to set the number of cores used by each,
        # and it shouldn't exceed the number of physical cores on a machine. Apparently,
        # the MPI -n flag should be the number of computational nodes, not the number of total
        # cores.'
        comsolLogName = path_settings['dirPath'] + '/comsolLog.txt'
        stdOutLogName = path_settings['dirPath'] + '/comsolStdOut.txt'
        stdErrLogName = path_settings['dirPath'] + '/comsolStdErr.txt'
        # save the resulting file for manual inspection
        if not self.model.modelDict['jobSettings']['comsolRunMode'] == 'batch':
            if self.os == 'windows':
                comsolCommand = mpiPath + ' -n ' + str(numParallelJobs) + ' \"' + comsolExecPath +\
                    '\" -np ' + str(numCoresPerJob) + \
                    ' -inputFile ' + comsolModelPath
            elif self.os == 'linux':
                comsolCommand = comsolExecPath + ' batch -nn ' + str(numParallelJobs) + ' -nnhost ' + str(numJobsPerNode) +\
                    ' -np ' + str(numCoresPerJob) + ' -inputFile ' + comsolModelPath + ' -batchlog ' +\
                    comsolLogName + ' -mpifabrics shm:tcp'
        else:
            if self.os == 'windows':
                comsolCommand = mpiPath + ' -n ' + str(numParallelJobs) + ' \"' + comsolExecPath +\
                    '\" -nosave -np ' + \
                    str(numCoresPerJob) + ' -inputFile ' + comsolModelPath
            elif self.os == 'linux':
                comsolCommand = comsolExecPath + ' batch -nn ' + str(numParallelJobs) + ' -nnhost ' + str(numJobsPerNode) +\
                    ' -nosave -np ' + str(numCoresPerJob) + ' -inputFile ' + comsolModelPath + ' -batchlog ' +\
                    comsolLogName + ' -mpifabrics shm:tcp' + ' -mpiarg -verbose'
        # Intel MPI on SLURM needs an extra bootstrap argument
        if slurmRun:
            comsolCommand += ' -mpibootstrap slurm'

        if hostFile is not None:
            comsolCommand += ' -f ' + hostFile
        comsolLog = open(stdOutLogName, 'w')
        comsolErr = open(stdErrLogName, 'w')
        print('Running {} ...'.format(comsolCommand))

        comsolRun = subprocess.Popen(
            comsolCommand,
            stdout=comsolLog,
            stderr=comsolErr,
            shell=True,
            env=my_env)
        print('Starting COMSOL run...')
        # Determine the number of voltages we are expecting.
        numVoltages = model_dict['physicsSweep']['length']
        resultFileBase = '{}/{}_export'.format(
            comsolSolsPath, model_dict['comsolInfo']['fileName'])
        eigenFileBase = '{}/{}_eigvals'.format(
            comsolSolsPath, model_dict['comsolInfo']['fileName'])
        surIntFileBase = '{}/{}_sur_integrals'.format(
            comsolSolsPath, model_dict['comsolInfo']['fileName'])
        volIntFileBase = '{}/{}_vol_integrals'.format(
            comsolSolsPath, model_dict['comsolInfo']['fileName'])
        while True:
            if comsolRun.poll() is not None:  # If the run is done, tag it as complete
                print('COMSOL run finshed with exit code {}!'.format(
                    comsolRun.returncode))
                break
            else:
                fracComplete = 1.0
                if 'electrostatics' in self.model.modelDict['comsolInfo'][
                        'physics']:
                    solsList = glob.glob(resultFileBase + '*.txt')
                    fracComplete = min(
                        len(solsList) / float(numVoltages), fracComplete)
                if ('schrodinger' in self.model.modelDict['comsolInfo']['physics']) or (
                        'bdg' in self.model.modelDict['comsolInfo']['physics']):
                    eigenList = glob.glob(eigenFileBase + '*.txt')
                    fracComplete = min(
                        len(eigenList) / float(numVoltages), fracComplete)
                if self.model.modelDict['comsolInfo']['surfaceIntegrals']:
                    surfIntList = glob.glob(surIntFileBase + '*.txt')
                    fracComplete = min(len(surfIntList) /
                                       float(numVoltages), fracComplete)
                if self.model.modelDict['comsolInfo']['volumeIntegrals']:
                    volIntList = glob.glob(volIntFileBase + '*.txt')
                    fracComplete = min(len(volIntList) /
                                       float(numVoltages), fracComplete)
                print('... ' + str(fracComplete))
                time.sleep(5.)
                if fracComplete >= 1.0:  # we are done!
                    print('COMSOL run finished, but failed to exit!')
                    print('Closing it in 120 seconds...')
                    sys.stdout.flush()
                    time.sleep(120.)
                    comsolRun.terminate()
                    break
        comsolLog.close()
        comsolErr.close()

        # Now that we have run COMSOL, import the data as a binary:
        myData = dataProcessing.SimData(
            modelFilePath)  # initialize the bulk data
        myData.batch_import_solutions()  # gather up the data

    def runBatchPostProc(self, modelFilePath):
        """Run batch post-processing. This requires proprietary components
        to be installed.
        """
        import qms
        numJobsPerNode = self.model.modelDict['jobSettings']['numJobsPerNode']
        numNodes = self.model.modelDict['jobSettings']['numNodes']
        numCores = numNodes * numJobsPerNode
        mpiexecName = self.model.modelDict['pathSettings']['mpiPath']
        pythonName = self.model.modelDict['pathSettings']['pythonPath']
        hostFile = self.model.modelDict['jobSettings']['hostFile']

        # If we are on the Linux cluster and not run by SLURM, we need to
        # enable the launcher hack
        my_env = os.environ.copy()
        if self.os == 'linux' and 'SLURM_JOB_NODELIST' not in os.environ:
            launcherPath = os.path.dirname(qms.__file__) + '/launch.py'
            my_env['I_MPI_HYDRA_BOOTSTRAP_EXEC'] = launcherPath  # for Intel MPI
            my_env['HYDRA_LAUNCHER_EXEC'] = launcherPath  # for MPICH

        # Convert any unicode entries in the env
        my_env = self.convert_unicode_to_ascii(my_env)

        batchPostProcpath = qms.postProcessing.__file__.rstrip(
            '__init__.pyc') + 'batchPostProc.py'
        mpiCmd = [mpiexecName, '-n', str(numCores)]
        if hostFile:
            mpiCmd += ['-f', hostFile]
        pythonCmd = [pythonName, batchPostProcpath,
                     '\"' + modelFilePath + '\"']
        print('Running {}...'.format(mpiCmd + pythonCmd))
        subprocess.check_call(mpiCmd + pythonCmd, env=my_env)

        basePath = os.path.dirname(modelFilePath)
        solutionsPath = os.path.join(
            basePath, self.model.modelDict['comsolInfo']['exportDir'])
        solutionsPattern = os.path.join(
            solutionsPath,
            self.model.modelDict['comsolInfo']['fileName'] +
            '_export*')

        print('Deleting text solutions files...')
        print(solutionsPattern)
        for f in glob.glob(solutionsPattern):
            os.remove(f)
