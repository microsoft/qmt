# -*-coding: utf-8 -*-
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

"""Functions that deal with file i/o."""

import os

import FreeCAD
import Part
import Mesh

from .auxiliary import silent_stdout


def exportMeshed(obj, fileName):
    """ Export a mesh of an object to the given file name.
    """
    # These previous methods use more complicated routines (netgen or mefisto)
    # that produce more controllable meshes but sometimes fail.
    # meshedObj = FreeCAD.ActiveDocument.addObject("Mesh::Feature",obj.Name+"_mesh")
    # meshedObj.Mesh=MeshPart.meshFromShape(Shape=obj.Shape,Fineness=0,SecondOrder=0,Optimize=0,
    # AllowQuad=0)
    # meshedObj.Mesh=Mesh.Mesh(obj.Shape.tessellate(0.01))
    # meshedObj.Mesh.write(fileName,"STL",meshedObj.Name)
    meshedObj = Mesh.export([obj], fileName)
    return meshedObj


def exportCAD(obj_list, file_name):
    """ Export a STEP (Standard for the Exchange of Product Data) 3D CAD file.

    :param list obj_list:       List of objects to export.
    :param string file_name:    Name of file to create and export into.
    """
    if not isinstance(obj_list, list):
        raise TypeError("obj_list must be a list of objects.")
    # The export format is determined by the extension, so we should check it:
    supported_ext = (".step", ".stp")
    if file_name.endswith(supported_ext):
        with silent_stdout():
            Part.export(obj_list, file_name)
    else:
        raise ValueError(
            file_name
            + " is not a supported extension ("
            + ", ".join(supported_ext)
            + ")"
        )
