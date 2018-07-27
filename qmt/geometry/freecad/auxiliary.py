# -*-coding: utf-8 -*-
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

"""General FreeCAD helper functions."""


from qmt.geometry.freecad import FreeCAD

def delete(obj):
    '''Delete an object by FreeCAD name.
    '''
    doc = FreeCAD.ActiveDocument
    doc.removeObject(obj.Name)
    doc.recompute()


def _deepRemove_impl(obj):
    ''' Implementation helper for deepRemove.
    '''
    for child in obj.OutList:
        _deepRemove_impl(child)
    FreeCAD.ActiveDocument.removeObject(obj.Name)


def deepRemove(obj=None, name=None, label=None):
    ''' Remove a targeted object and recursively delete all its sub-objects.
    '''
    doc = FreeCAD.ActiveDocument
    if obj is not None:
        pass
    elif name is not None:
        obj = doc.getObject(name)
    elif label is not None:
        obj = doc.getObjectsByLabel(label)[0]
    else:
        raise RuntimeError('No object selected!')
    _deepRemove_impl(obj)
    doc.recompute()
