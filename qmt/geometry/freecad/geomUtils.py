# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

"""Utilities to work with general geometries."""

import numpy as np

import FreeCAD
import Draft
import Part

from .auxiliary import *
from .sketchUtils import findSegments

vec = FreeCAD.Vector


def extrude_partwb(sketch, length, reverse=False, name=None):
    """Extrude via Part workbench.

    Parameters
    ----------
    sketch :

    length :

    reverse :
        (Default value = False)
    name : str
        (Default value = None)

    Returns
    -------
    FreeCAD.Part.Feature

    """
    doc = FreeCAD.ActiveDocument
    if name is None:
        f = doc.addObject("Part::Extrusion")
    else:
        f = doc.addObject("Part::Extrusion", name)
    f.Base = sketch
    f.DirMode = "Normal"
    f.DirLink = None
    f.LengthFwd = length
    f.LengthRev = 0.0
    f.Solid = True
    f.Reversed = reverse
    f.Symmetric = False
    f.TaperAngle = 0.0
    f.TaperAngleRev = 0.0
    # ~ f.Base.ViewObject.hide()
    doc.recompute()
    return f


def extrude(sketch, length, reverse=False, name=None):
    """Selector for extrude method.

    Parameters
    ----------
    sketch :

    length :

    reverse :
        (Default value = False)
    name : str
        (Default value = None)

    Returns
    -------
    FreeCAD.Part.Feature

    """
    return extrude_partwb(sketch, length, reverse, name)


def copy_move(obj, moveVec=(0.0, 0.0, 0.0), copy=True):
    """Create a duplciate of the object using a draft move operation.

    Parameters
    ----------
    obj : FreeCAD.App.Document
        A FreeCAD object.
    moveVec :
        (Default value = (0.0, 0.0, 0.0))
    copy :
        (Default value = True)

    Returns
    -------
    f
    """
    f = Draft.move([obj], vec(moveVec[0], moveVec[1], moveVec[2]), copy=copy)
    if f.Shape.Vertexes:
        f.Shape = f.Shape.removeSplitter()  # get rid of redundant lines
    FreeCAD.ActiveDocument.recompute()
    return f


# ~ # TODO: consuming is questionable because inputs might be needed in a delayed fashion
def make_solid(obj, consumeInputs=False):
    doc = FreeCAD.ActiveDocument
    shell = obj.Shape.Faces
    shell = Part.Solid(Part.Shell(shell))
    solid = doc.addObject("Part::Feature", obj.Label + "_solid")
    solid.Label = obj.Label + "_solid"
    solid.Shape = shell
    doc.recompute()
    del shell, solid
    return solid


def makeHexFace(sketch, zBottom, width):
    """Given a sketch for a wire, make the first face. Also need to make sure it
    is placed normal to the initial line segment in the sketch. This will ensure
    that the wire and shell can be constructed with sweep operations.

    Parameters
    ----------
    sketch :

    zBottom :

    width :


    Returns
    -------
    face3

    """
    doc = FreeCAD.ActiveDocument
    lineSegments = findSegments(sketch)
    lineSegment = lineSegments[0]
    x0, y0, _ = lineSegment[0]
    x1, y1, _ = lineSegment[1]
    dx = x1 - x0
    dy = y1 - y0
    # First, make the initial face:
    face = Draft.makePolygon(6, radius=width * 0.5, inscribed=False, face=True)
    doc.recompute()
    # Spin the face so that its faces are oriented normal to the path:
    alpha = 90 - np.arctan(-dy / dx) * 180.0 / np.pi
    center = vec(0.0, 0.0, 0.0)
    axis = vec(0.0, 0.0, 1.0)
    face1 = Draft.rotate(face, alpha, center, axis=axis, copy=True)
    doc.recompute()
    # Rotate the wire into the proper plane:
    alpha = 90.0
    center = vec(0.0, 0.0, 0.0)
    axis = vec(-dy, dx, 0)
    face2 = Draft.rotate(face1, 90.0, center, axis=axis, copy=True)
    doc.recompute()
    # Finally, move it into position:
    rVec = vec(x0, y0, 0.5 * width + zBottom)
    face3 = Draft.move(face2, rVec, copy=True)
    delete(face)
    delete(face1)
    delete(face2)
    doc.recompute()
    return face3


def genUnion(objList, consumeInputs=False):
    """Generates a Union non-destructively.

    Parameters
    ----------
    objList :

    consumeInputs :
        (Default value = False)

    Returns
    -------
    Object(s).

    """
    doc = FreeCAD.ActiveDocument
    if not objList:
        return None
    elif len(objList) == 1:
        returnObj = copy_move(objList[0])
        returnObj.Label = objList[0].Label
        if consumeInputs:
            delete(objList[0])
        return returnObj
    else:
        union = doc.addObject("Part::MultiFuse")
        nonZeroList = []
        for obj in objList:
            if isNonempty(obj):
                nonZeroList += [obj]
        union.Shapes = nonZeroList
        doc.recompute()  # crucial recompute
        unionDupe = copy_move(union)
        unionDupe.Label = objList[0].Label
        doc.removeObject(union.Name)
        doc.recompute()
        if consumeInputs:
            for obj in objList:
                doc.removeObject(obj.Name)
            doc.recompute()
        return unionDupe


def getBB(obj):
    """Get the bounding box coords of an object.

    Parameters
    ----------
    obj : FreeCAD.App.Document
        A FreeCAD object.
    Returns
    -------
    Tuple of (xMin, xMax, yMin, yMax, zMin, zMax).

    """
    xMin = obj.Shape.BoundBox.XMin
    xMax = obj.Shape.BoundBox.XMax
    yMin = obj.Shape.BoundBox.YMin
    yMax = obj.Shape.BoundBox.YMax
    zMin = obj.Shape.BoundBox.ZMin
    zMax = obj.Shape.BoundBox.ZMax
    return (xMin, xMax, yMin, yMax, zMin, zMax)


def makeBB(BB):
    """Make a bounding box given BB tuple.

    Parameters
    ----------
    BB :


    Returns
    -------
    box

    """
    doc = FreeCAD.ActiveDocument
    xMin, xMax, yMin, yMax, zMin, zMax = BB
    box = doc.addObject("Part::Box")
    centerVector = vec(xMin, yMin, zMin)
    box.Placement = FreeCAD.Placement(
        centerVector, FreeCAD.Rotation(vec(0.0, 0.0, 0.0), 0.0)
    )
    box.Length = xMax - xMin
    box.Width = yMax - yMin
    box.Height = zMax - zMin
    doc.recompute()
    return box


def subtract(obj0, obj1, consumeInputs=False):
    """Subtract two objects, optionally deleting the input objects.

    Parameters
    ----------
    obj0 :

    obj1 :

    consumeInputs :
        (Default value = False)

    Returns
    -------
    FreeCAD.App.Document

    """
    doc = FreeCAD.ActiveDocument
    tempObj = doc.addObject("Part::Cut")
    tempObj.Base = obj0
    tempObj.Tool = obj1
    doc.recompute()
    returnObj = copy_move(tempObj)
    doc.removeObject(tempObj.Name)
    doc.recompute()
    if consumeInputs:
        doc.removeObject(obj0.Name)
        doc.removeObject(obj1.Name)
        doc.recompute()
    return returnObj


def subtractParts(domainObj, partList):
    """Subtract given part objects from a domain.

    Parameters
    ----------
    domainObj :

    partList :


    Returns
    -------
    FreeCAD.App.Document

    """
    doc = FreeCAD.ActiveDocument
    diffObj = copy_move(domainObj)
    for obj in partList:
        diffObjTemp = Draft.downgrade([diffObj, obj], delete=True)[0][0]
        doc.recompute()
        diffObj = copy_move(diffObjTemp)
        delete(diffObjTemp)
    # TODO : This routine is leaving some nuisance objects around that should
    # be deleted.
    return diffObj


def intersect(objList, consumeInputs=False):
    """Intersect a list of objects, optionally deleting the input objects.

    Parameters
    ----------
    objList :

    consumeInputs :
        (Default value = False)

    Returns
    -------
    FreeCAD.App.Document

    """
    doc = FreeCAD.ActiveDocument
    intersectTemp = doc.addObject("Part::MultiCommon")
    intersectTemp.Shapes = objList
    doc.recompute()
    returnObj = copy_move(intersectTemp)
    doc.removeObject(intersectTemp.Name)
    doc.recompute()
    if consumeInputs:
        for obj in objList:
            doc.removeObject(obj.Name)
        doc.recompute()
    return returnObj


def checkOverlap(objList):
    """Checks if a list of objects, when intersected, contains a finite volume.abs
    Returns true if it does, returns false if the intersection is empty.

    Parameters
    ----------
    objList :


    Returns
    -------
    Boolean

    """
    intObj = intersect(objList)
    if not intObj.Shape.Vertexes:
        overlap = False
    else:
        overlap = True
    delete(intObj)
    return overlap


def isNonempty(obj):
    """Checks if an object is nonempty (returns True) or empty (returns False).

    Parameters
    ----------
    obj : FreeCAD.App.Document
        A FreeCAD object.
    Returns
    -------
    Boolean

    """
    if not obj.Shape.Vertexes:
        return False
    else:
        return True


def extrudeBetween(sketch, zMin, zMax, name=None):
    """Non-destructively extrude a sketch between zMin and zMax.

    Parameters
    ----------
    sketch :

    zMin : float

    zMax : float

    name : str
        (Default value = None)

    Returns
    -------
    ext

    """
    doc = FreeCAD.ActiveDocument
    tempExt = extrude(sketch, zMax - zMin, name=name)
    ext = copy_move(tempExt, moveVec=(0.0, 0.0, zMin))
    doc.recompute()
    doc.removeObject(tempExt.Name)
    doc.recompute()
    return ext


def liftObject(obj, d, consumeInputs=False):
    """Create a new solid by lifting an object by a distance d along z, filling
    in the space swept out.

    Parameters
    ----------
    obj : FreeCAD.App.Document
        A FreeCAD object.
    d : float
        Distance.
    consumeInputs :
        (Default value = False)

    Returns
    -------
    returnObj

    """
    objBB = getBB(obj)
    # lift up the original sketch
    liftedObj = copy_move(obj, moveVec=(0.0, 0.0, d))
    fillBB = np.array(objBB)
    fillBB[5] = fillBB[4] + d  # Make a new BB defining the missing space
    fillObj = makeBB(tuple(fillBB))  # Make a box to fill the space
    returnObj = genUnion([fillObj, liftedObj], consumeInputs=True)
    if consumeInputs:
        deepRemove(obj)
    return returnObj


def draftOffset(inputSketch, t):
    """Attempt to offset the draft figure by a thickness t. Positive t is an
    inflation, while negative t is a deflation.

    Parameters
    ----------
    inputSketch :

    t : float
        Thickness.


    Returns
    -------
    returnSketch

    """
    # ~ from qmt.geometry.freecad.geomUtils import extrude, copy_move, delete

    if np.isclose(t, 0):
        return copy_move(inputSketch)
    deltaT = np.abs(t)
    offsetVec1 = vec(-deltaT, -deltaT, 0.0)
    offsetVec2 = vec(deltaT, deltaT, 0.0)

    offset0 = copy_move(inputSketch)
    # Currently FreeCAD throws an error if we try to collapse a shape into a
    # point through offsetting. If that happens, set delta to 5E-5. Any closer
    # and FreeCAD seems to suffer from numerical errors
    try:
        offset1 = Draft.offset(inputSketch, offsetVec1, copy=True)
    except BaseException:
        deltaT -= 5e-5
        offset1 = Draft.offset(inputSketch, vec(-deltaT, -deltaT, 0.0), copy=True)
    try:
        offset2 = Draft.offset(inputSketch, offsetVec2, copy=True)
    except BaseException:
        deltaT -= 5e-5
        offset2 = Draft.offset(inputSketch, vec(deltaT, deltaT, 0.0), copy=True)

    # Compute the areas of the sketches. FreeCAD will throw an exception if we
    # try to make a Face out of a line or a point, we catch that give it an
    # area of 0
    try:
        A0 = np.abs(Part.Face(offset0.Shape).Area)
    except BaseException:
        A0 = 0
    try:
        A1 = np.abs(Part.Face(offset1.Shape).Area)
    except BaseException:
        A1 = 0
    try:
        A2 = np.abs(Part.Face(offset2.Shape).Area)
    except BaseException:
        A2 = 0

    # If everything worked properly, these should either be ordered as
    # A1<A0<A2 or A2<A0<A1:
    if A2 > A0 and A0 > A1:
        bigSketch = offset2
        littleSketch = offset1
    elif A1 > A0 and A0 > A2:
        bigSketch = offset1
        littleSketch = offset2
    elif A2 > A1 and A1 > A0:
        bigSketch = offset2
        littleSketch = None
    # If we aren't in correct case, we still might be able to salvage things
    # for certain values of t:
    elif A1 > A2 and A2 > A0:
        bigSketch = offset1
        littleSketch = None
    elif A2 < A1 and A1 < A0:
        bigSketch = None
        littleSketch = offset2
    elif A1 < A2 and A2 < A0:
        bigSketch = None
        littleSketch = offset1
    else:
        bigSketch = None
        littleSketch = None
    if t < 0 and littleSketch is not None:
        returnSketch = copy_move(littleSketch)
    elif t > 0 and bigSketch is not None:
        returnSketch = copy_move(bigSketch)
    else:
        raise ValueError(
            "Failed to offset the sketch "
            + str(inputSketch.Name)
            + " by amount "
            + str(t)
        )

    # # now that we have the three solids, we need to figure out which is bigger
    # # and which is smaller.
    # diff10 = subtract(solid1,solid0)
    # diff20 = subtract(solid2,solid0)
    # numVerts10 = len(diff10.Shape.Vertexes)
    # numVerts20 = len(diff20.Shape.Vertexes)
    # if numVerts10 > 0 and numVerts20 == 0:
    #     positiveOffsetIndex = 1
    # elif numVerts10 == 0 and numVerts20 > 0 :
    #     positiveOffsetIndex = 2
    # else:
    #     raise ValueError('draftOffset has failed to give a non-empty shape!')
    # delete(solid0)
    # delete(solid1)
    # delete(solid2)
    # delete(diff10)
    # delete(diff20)
    # if t > 0:
    #     if positiveOffsetIndex == 1:
    #         returnSketch = copy_move(offset1)
    #     else:
    #         returnSketch = copy_move(offset2)
    # elif t<0:
    #     if positiveOffsetIndex == 1:
    #         returnSketch = copy_move(offset2)
    #     else:
    #         returnSketch = copy_move(offset1)
    delete(offset0)
    delete(offset1)
    delete(offset2)
    return returnSketch


def centerObjects(objsList):
    """Move all the objects in the list in the x-y plane so that they are
    centered about the origin.

    Parameters
    ----------
    objsList :


    Returns
    -------
    None

    """
    if not objsList:
        return
    wholeObj = genUnion(objsList)
    wholeBB = getBB(wholeObj)
    x0 = 0.5 * (wholeBB[0] + wholeBB[1])
    y0 = 0.5 * (wholeBB[2] + wholeBB[3])
    for obj in objsList:
        copy_move(obj, moveVec=(-x0, -y0, 0.0), copy=False)
    delete(wholeObj)


def crossSection(obj, axis=(1.0, 0.0, 0.0), d=1.0, name=None):
    """Return cross section of object along axis.

    Parameters
    ----------
    obj : FreeCAD.App.Document
        A FreeCAD object.
    axis :
        (Default value = (1.0, 0.0, 0.0)
    d : float
        (Default value = 1.0)
    name : str
        (Default value = None)

    Returns
    -------
    returnObj

    """
    doc = FreeCAD.ActiveDocument
    if name is None:
        name = obj.Name + "_section"
    wires = list()
    shape = obj.Shape
    for i in shape.slice(vec(axis[0], axis[1], axis[2]), d):
        wires.append(i)
    returnObj = doc.addObject("Part::Feature", name)
    returnObj.Shape = Part.Compound(wires)
    return returnObj
