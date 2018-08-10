# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

"""Utilities to work with general geometries."""


import numpy as np

from qmt.geometry.freecad import FreeCAD
from qmt.geometry.freecad import Draft
from qmt.geometry.freecad import Part

from .auxiliary import *
from .sketchUtils import findSegments

vec = FreeCAD.Vector


def extrude_partwb(sketch, length, reverse=False, name=None):
    '''Extrude via Part workbench.'''
    doc = FreeCAD.ActiveDocument
    if name is None:
        f = doc.addObject('Part::Extrusion')
    else:
        f = doc.addObject('Part::Extrusion', name)
    f.Base = sketch
    f.DirMode = "Normal"
    f.DirLink = None
    f.LengthFwd = length
    f.LengthRev = 0.
    f.Solid = True
    f.Reversed = reverse
    f.Symmetric = False
    f.TaperAngle = 0.
    f.TaperAngleRev = 0.
    # ~ f.Base.ViewObject.hide()
    doc.recompute()
    return f


def extrude(sketch, length, reverse=False, name=None):
    '''Selector for extrude method.'''
    return extrude_partwb(sketch, length, reverse, name)


def copy_move(obj, moveVec=(0., 0., 0.), copy=True):
    '''Create a duplciate of the object using a draft move operation.
    '''
    f = Draft.move([obj], vec(moveVec[0], moveVec[1], moveVec[2]), copy=copy)
    if f.Shape.Vertexes:
        f.Shape = f.Shape.removeSplitter()  # get rid of redundant lines
    FreeCAD.ActiveDocument.recompute()
    return f


def makeHexFace(sketch, zBottom, width):
    '''Given a sketch for a wire, make the first face. Also need to make sure it
    is placed normal to the initial line segment in the sketch. This will ensure
    that the wire and shell can be constructed with sweep operations.
    '''
    doc = FreeCAD.ActiveDocument
    lineSegments = findSegments(sketch)
    lineSegment = lineSegments[0]
    # ~ x0, y0, z0 = lineSegment[0]
    # ~ x1, y1, z1 = lineSegment[1]
    x0, y0, _ = lineSegment[0]
    x1, y1, _ = lineSegment[1]
    dx = x1 - x0
    dy = y1 - y0
    # ~ xBar = 0.5 * (x0 + x1)
    # ~ yBar = 0.5 * (y0 + y1)
    # First, make the initial face:
    face = Draft.makePolygon(6, radius=width * 0.5, inscribed=False, face=True)
    doc.recompute()
    # Spin the face so that its faces are oriented normal to the path:
    alpha = 90 - np.arctan(-dy / dx) * 180. / np.pi
    center = vec(0., 0., 0.)
    axis = vec(0., 0., 1.)
    face1 = Draft.rotate(face, alpha, center, axis=axis, copy=True)
    doc.recompute()
    # Rotate the wire into the proper plane:
    alpha = 90.
    center = vec(0., 0., 0.)
    axis = vec(-dy, dx, 0)
    face2 = Draft.rotate(face1, 90., center, axis=axis, copy=True)
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
    '''Generates a Union non-destructively.
    '''
    doc = FreeCAD.ActiveDocument
    if not objList:
        return None
    elif len(objList) == 1:
        returnObj = copy_move(objList[0])
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
        doc.removeObject(union.Name)
        doc.recompute()
        if consumeInputs:
            for obj in objList:
                doc.removeObject(obj.Name)
            doc.recompute()
        return unionDupe


def getBB(obj):
    '''Get the bounding box coords of an object.
    '''
    xMin = obj.Shape.BoundBox.XMin
    xMax = obj.Shape.BoundBox.XMax
    yMin = obj.Shape.BoundBox.YMin
    yMax = obj.Shape.BoundBox.YMax
    zMin = obj.Shape.BoundBox.ZMin
    zMax = obj.Shape.BoundBox.ZMax
    return (xMin, xMax, yMin, yMax, zMin, zMax)


def makeBB(BB):
    '''Make a bounding box given BB tuple.
    '''
    doc = FreeCAD.ActiveDocument
    xMin, xMax, yMin, yMax, zMin, zMax = BB
    box = doc.addObject("Part::Box")
    centerVector = vec(xMin, yMin, zMin)
    box.Placement = FreeCAD.Placement(centerVector,
                                      FreeCAD.Rotation(vec(0., 0., 0.), 0.))
    box.Length = xMax - xMin
    box.Width = yMax - yMin
    box.Height = zMax - zMin
    doc.recompute()
    return box


def subtract(obj0, obj1, consumeInputs=False):
    '''Subtract two objects, optionally deleting the input objects.
    '''
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
    ''' Subtract given part objects from a domain.
    '''
    doc = FreeCAD.ActiveDocument
    diffObj = copy_move(domainObj)
    for obj in partList:
        diffObjTemp = Draft.downgrade([diffObj, obj], delete=True)[0][0]
        doc.recompute()
        diffObj = copy_move(diffObjTemp)
        delete(diffObjTemp)
    # TODO : This routine is leaving some nuisance objects around that should be deleted.
    return diffObj


def intersect(objList, consumeInputs=False):
    '''Intersect a list of objects, optionally deleting the input objects.
    '''
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
    ''' Checks if a list of objects, when intersected, contains a finite volume.abs
    Returns true if it does, returns false if the intersection is empty.
    '''
    intObj = intersect(objList)
    if not intObj.Shape.Vertexes:
        overlap = False
    else:
        overlap = True
    delete(intObj)
    return overlap


def isNonempty(obj):
    ''' Checks if an object is nonempty (returns True) or empty (returns False).
    '''
    if not obj.Shape.Vertexes:
        return False
    else:
        return True


def extrudeBetween(sketch, zMin, zMax, name=None):
    ''' Non-destructively extrude a sketch between zMin and zMax.
    '''
    doc = FreeCAD.ActiveDocument
    tempExt = extrude(sketch, zMax - zMin, name=name)
    ext = copy_move(tempExt, moveVec=(0., 0., zMin))
    doc.recompute()
    doc.removeObject(tempExt.Name)
    doc.recompute()
    return ext


def liftObject(obj, d, consumeInputs=False):
    ''' Create a new solid by lifting an object by a distance d along z, filling
    in the space swept out.
    '''
    objBB = getBB(obj)
    liftedObj = copy_move(obj, moveVec=(0., 0., d))  # lift up the original sketch
    fillBB = np.array(objBB)
    fillBB[5] = fillBB[4] + d  # Make a new BB defining the missing space
    fillObj = makeBB(tuple(fillBB))  # Make a box to fill the space
    returnObj = genUnion([fillObj, liftedObj], consumeInputs=True)
    if consumeInputs:
        deepRemove(obj)
    return returnObj


def centerObjects(objsList):
    ''' Move all the objects in the list in the x-y plane so that they are
    centered about the origin.
    '''
    if not objsList:
        return
    wholeObj = genUnion(objsList)
    wholeBB = getBB(wholeObj)
    x0 = 0.5 * (wholeBB[0] + wholeBB[1])
    y0 = 0.5 * (wholeBB[2] + wholeBB[3])
    for obj in objsList:
        copy_move(obj, moveVec=(-x0, -y0, 0.), copy=False)
    delete(wholeObj)


def crossSection(obj, axis=(1., 0., 0.), d=1.0, name=None):
    '''Return cross section of object along axis.'''
    doc = FreeCAD.ActiveDocument
    if name is None:
        name = obj.Name + '_section'
    wires = list()
    shape = obj.Shape
    for i in shape.slice(vec(axis[0], axis[1], axis[2]), d):
        wires.append(i)
    returnObj = doc.addObject("Part::Feature", name)
    returnObj.Shape = Part.Compound(wires)
    return returnObj