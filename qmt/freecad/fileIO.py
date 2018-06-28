# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

###
### Functions that deal with file i/o
###

import FreeCAD
import Part
import Mesh
import qmt as QMT


def setupModelFile(fileName):
    ''' Makes an empty json model file and sets up a spreadsheet to sync with it.
    '''
    doc = FreeCAD.ActiveDocument
    objList = doc.Objects
    objNames = [x.Name for x in objList]
    if 'modelFilePath' in objNames:
        doc.removeObject('modelFilePath')
    doc.recompute()
    spreadSheet = doc.addObject('Spreadsheet::Sheet', 'modelFilePath')
    spreadSheet.set('A1', 'Path to model file:')
    spreadSheet.set('B1', fileName)
    spreadSheet.setAlias('B1', 'modelFilePath')
    spreadSheet.setColumnWidth('A', 200)
    myModelFile = QMT.Model(modelPath=fileName)
    myModelFile.loadModel()
    myModelFile.saveModel()
    doc.recompute()


def getModel():
    ''' return the model file associated with the current FreeCAD document.
    '''
    modelPath = FreeCAD.ActiveDocument.modelFilePath.modelFilePath
    myModel = QMT.Model(modelPath=modelPath)
    myModel.loadModel()
    return myModel


def exportMeshed(obj, fileName):
    ''' Export a mesh of an object to the given file name.
    '''
    # These previous methods use more complicated routines (netgen or mefisto)
    # that produce more controllable meshes but sometimes fail.
    # meshedObj = FreeCAD.ActiveDocument.addObject("Mesh::Feature",obj.Name+"_mesh")
    # meshedObj.Mesh=MeshPart.meshFromShape(Shape=obj.Shape,Fineness=0,SecondOrder=0,Optimize=0,AllowQuad=0)
    # meshedObj.Mesh=Mesh.Mesh(obj.Shape.tessellate(0.01))
    # meshedObj.Mesh.write(fileName,"STL",meshedObj.Name)
    meshedObj = Mesh.export([obj], fileName)
    return meshedObj


def exportCAD(obj, fileName):
    ''' Export a STEP (Standard for the Exchange of Product Data) 3D CAD file
    for the object.
    '''
    # The export format is determined by the extension, so we should check it:
    if (fileName[-5:] == '.step') or (fileName[-4:] == '.stp'):
        Part.export([obj], fileName)
    else:
        raise ValueError('The file path' + fileName + ' does not end in .step or .stp. \
                          Please fix this and try your export again.')


def updateParams(passModel=None):
    ''' Update the parameters in the modelParams spreadsheet to reflect the 
        current value in the model file.
    '''
    doc = FreeCAD.ActiveDocument
    if passModel is None:
        myModel = getModel()
    else:
        myModel = passModel
    paramDict = myModel.modelDict['geometricParams']
    # We only want to do something if geometric parameters are defined
    # in the model. This means that if we have old parameters sitting
    # in the FreeCAD file, they won't get wiped out if we comment out
    # a geometry sweep in the model script.
    if len(paramDict) > 0:
        # Internal: do not removeObject the spreadsheet, param dependencies will break.
        try: spreadSheet = doc.modelParams
        except: spreadSheet = doc.addObject('Spreadsheet::Sheet', 'modelParams')
        spreadSheet.clearAll()  # delete existing spreadsheet
        spreadSheet.set('A1', 'paramName')
        spreadSheet.set('B1', 'paramValue')
        spreadSheet.setColumnWidth('A', 200)
        spreadSheet.setStyle('A1:B1', 'bold', 'add')
        for i, key in enumerate(paramDict):
            paramType = paramDict[key][1]
            if paramType == 'freeCAD':
                idx = str(i + 2)
                spreadSheet.set('A' + idx, key)
                spreadSheet.set('B' + idx, paramDict[key][0])
                spreadSheet.setAlias('B' + idx, str(key))
            elif paramType == 'python':
                pass
            else:
                raise ValueError('Unknown geometric parameter type.')
        doc.recompute()
