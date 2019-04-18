# -*-coding: utf-8 -*-
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

"""Functions that deal with file i/o."""

import os
from typing import Sequence

import Part
import Mesh

from .auxiliary import silent_stdout


def exportMeshed(obj_list: Sequence, file_name: str):
    """Export a STL 3D Mesh file.

    Parameters
    ----------
    obj_list : list
        List of objects to export.
    file_name : str
        Name of file to create and export into.

    Returns
    -------
    None

    """
    if not isinstance(obj_list, list):
        raise TypeError("obj_list must be a list of objects.")
    # These previous methods use more complicated routines (netgen or mefisto)
    # that produce more controllable meshes but sometimes fail.
    # obj = obj_list[0]
    # meshedObj = FreeCAD.ActiveDocument.addObject("Mesh::Feature",obj.Name+"_mesh")
    # meshedObj.Mesh=MeshPart.meshFromShape(Shape=obj.Shape,Fineness=0,SecondOrder=0,Optimize=0,
    # AllowQuad=0)
    # meshedObj.Mesh=Mesh.Mesh(obj.Shape.tessellate(0.01))
    # meshedObj.Mesh.write(fileName,"STL",meshedObj.Name)
    supported_ext = ".stl"
    if file_name.endswith(supported_ext):
        with silent_stdout():
            Mesh.export(obj_list, file_name)
    else:
        raise ValueError(
            file_name
            + " is not a supported extension ("
            + ", ".join(supported_ext)
            + ")"
        )


def exportCAD(obj_list: Sequence, file_name: str):
    """Export a STEP (Standard for the Exchange of Product Data) 3D CAD file.

    Parameters
    ----------
    obj_list : list
        List of objects to export.
    file_name : str
        Name of file to create and export into.

    Returns
    -------


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
