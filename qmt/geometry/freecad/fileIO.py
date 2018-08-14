# -*-coding: utf-8 -*-
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

"""Functions that deal with file i/o."""


import os

import FreeCAD
import Part
import Mesh


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


def exportCAD(obj_list, file_name):
    ''' Export a STEP (Standard for the Exchange of Product Data) 3D CAD file.

    :param list obj_list:       List of objects to export.
    :param string file_name:    Name of file to create and export into.
    '''
    # The export format is determined by the extension, so we should check it:
    if file_name.endswith('.step') or file_name.endswith('.stp'):
        Part.export(obj_list, file_name)
    else:
        raise ValueError(file_name + ' is not a supported extension (.stp, .step)')


# TODO: this is sketchUtils or geomUtils, not fileIO
def updateParams(doc, paramDict):
    ''' Update the parameters in the modelParams spreadsheet to reflect the
        current value in the dict.
    '''
    # ~ doc = FreeCAD.ActiveDocument

    # ~ if passModel is None:
        # ~ myModel = getModel()
    # ~ else:
        # ~ myModel = passModel
    # ~ paramDict = myModel.modelDict['geometricParams']

    # We only want to do something if geometric parameters are defined
    # in the model. This means that if we have old parameters sitting
    # in the FreeCAD file, they won't get wiped out if we comment out
    # a geometry sweep in the model script.
    if paramDict:
        # Internal: unconditional removeObject on spreadSheet breaks param dependencies.
        # ~ spreadSheet = doc.addObject('Spreadsheet::Sheet', 'modelParams')
        try:
            spreadSheet = doc.modelParams
            spreadSheet.clearAll()  # clear existing spreadsheet
        except:
            doc.removeObject('modelParams')  # otherwise it was not a good spreadsheet
            spreadSheet = doc.addObject('Spreadsheet::Sheet', 'modelParams')
        spreadSheet.set('A1', 'paramName')
        spreadSheet.set('B1', 'paramValue')
        spreadSheet.setColumnWidth('A', 200)
        spreadSheet.setStyle('A1:B1', 'bold', 'add')
        for i, key in enumerate(paramDict):
            paramType = paramDict[key][1]
            if paramType == 'freeCAD':
                idx = str(i + 2)
                spreadSheet.set('A' + idx, key)
                spreadSheet.set('B' + idx, str(paramDict[key][0]))
                spreadSheet.setAlias('B' + idx, str(key))
            elif paramType == 'python':
                pass
            else:
                raise ValueError('Unknown geometric parameter type.')

        doc.recompute()


def store_serial(target_dict, target_label, save_fct, ext, obj):
    '''Store a serialised representation of save_fct(obj, temporary_file.ext)
    inside target_dict[target_label].
    '''
    import codecs
    import uuid
    tmp_path = 'tmp_' + uuid.uuid4().hex + '.' + ext
    save_fct(obj, tmp_path)
    with open(tmp_path, 'rb') as f:
        # ~ target_dict[target_label] = codecs.encode(f.read(), 'base64')
        target_dict[target_label] = codecs.encode(f.read(), 'base64').decode()  # TODO test
    os.remove(tmp_path)
