# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

###
### Utilities to work with general geometries
###

import FreeCAD
import Draft
import Part
import numpy as np
from qmt.freecad import findSegments


def delete(obj):
    doc = FreeCAD.ActiveDocument
    doc.removeObject(obj.Name)
    doc.recompute()



def extrude(sketch, length,reversed=False,name=None):
    '''
    Extrude sketch up to given length. Optional name (default: append '_extr').
    Return handle to extrude.
    '''
    if name is None:
        f = FreeCAD.ActiveDocument.addObject('PartDesign::Pad')
    else:
        f = FreeCAD.ActiveDocument.addObject('PartDesign::Pad',name)
    f.Sketch = sketch
    f.Length = length
    if reversed:
        f.Reversed = 1
    FreeCAD.ActiveDocument.recompute()
    return f


def copy(obj, moveVec=(0., 0., 0.), copy=True):
    '''
    Create a duplciate of the object using a draft move operation.
    '''

    f = Draft.move([obj], FreeCAD.Vector(moveVec[0], moveVec[1], moveVec[2]), copy=copy)
    if len(f.Shape.Vertexes)>0:
        f.Shape = f.Shape.removeSplitter() # get rid of redundant lines
    FreeCAD.ActiveDocument.recompute()
    return f


def makeHexFace(sketch, zBottom, width):
    ''' Given a sketch for a wire, make the first face. Also need to make sure it
    is placed normal to the initial line segment in the sketch. This will ensure
    that the wire and shell can be constructed with sweep operations.
    '''
    doc = FreeCAD.ActiveDocument
    lineSegments = findSegments(sketch)
    lineSegment = lineSegments[0]
    x0, y0, z0 = lineSegment[0];
    x1, y1, z1 = lineSegment[1]
    dx = x1 - x0;
    dy = y1 - y0
    xBar = 0.5 * (x0 + x1);
    yBar = 0.5 * (y0 + y1)
    # First, make the initial face:
    face = Draft.makePolygon(6, radius=width * 0.5, inscribed=False, face=True)
    doc.recompute()
    # Spin the face so that its faces are oriented normal to the path:
    alpha = 90 - np.arctan(-dy / dx) * 180. / np.pi
    center = FreeCAD.Vector(0., 0., 0.)
    axis = FreeCAD.Vector(0., 0., 1.)
    face1 = Draft.rotate(face, alpha, center, axis=axis, copy=True)
    doc.recompute()
    # Rotate the wire into the proper plane:
    alpha = 90.
    center = FreeCAD.Vector(0., 0., 0.)
    axis = FreeCAD.Vector(-dy, dx, 0)
    face2 = Draft.rotate(face1, 90., center, axis=axis, copy=True)
    doc.recompute()
    # Finally, move it into position:
    rVec = FreeCAD.Vector(x0, y0, 0.5 * width + zBottom)
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
    if len(objList) == 0:
        return None
    elif len(objList) == 1:
        returnObj = copy(objList[0])
        if consumeInputs:
            delete(objList[0])
        return returnObj
    else:
        union = doc.addObject("Part::MultiFuse")
        union.Shapes = objList
        doc.recompute()
        unionDupe = copy(union)
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
    centerVector = FreeCAD.Vector(xMin, yMin, zMin)
    box.Placement = FreeCAD.Placement(centerVector, \
                                      FreeCAD.Rotation(FreeCAD.Vector(0., 0., 0.), 0.))
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
    returnObj = copy(tempObj)
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
    diffObj = copy(domainObj)
    for obj in partList:
        diffObjTemp = Draft.downgrade([diffObj, obj], delete=True)[0][0]
        FreeCAD.ActiveDocument.recompute()
        diffObj = copy(diffObjTemp)
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
    returnObj = copy(intersectTemp)
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
    if len(intObj.Shape.Vertexes) == 0:
        overlap = False
    else:
        overlap = True
    delete(intObj)
    return overlap


def extrudeBetween(sketch, zMin, zMax):
    ''' Non-destructively extrude a sketch between zMin and zMax.
    '''
    doc = FreeCAD.ActiveDocument
    tempExt = extrude(sketch, zMax - zMin)
    ext = copy(tempExt, moveVec=(0., 0., zMin))
    doc.recompute()
    doc.removeObject(tempExt.Name)
    doc.recompute()
    return ext


def liftObject(obj, d, consumeInputs=False):
    ''' Create a new solid by lifting an object by a distance d along z, filling 
    in the space swept out. 
    '''
    objBB = getBB(obj)
    liftedObj = copy(obj, moveVec=(0., 0., d))  # lift up the original sketch
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
    if len(objsList) == 0:
        return None
    wholeObj = genUnion(objsList)
    wholeBB = getBB(wholeObj)
    x0 = 0.5 * (wholeBB[0] + wholeBB[1])
    y0 = 0.5 * (wholeBB[2] + wholeBB[3])
    for obj in objsList:
        copy(obj, moveVec=(-x0, -y0, 0.), copy=False)
    delete(wholeObj)

def crossSection(obj,axis=(1.,0.,0.),d=1.0,name=None):
    doc = FreeCAD.ActiveDocument
    if name is None:
        name = obj.Name+'_section'
    wires=list()
    shape=obj.Shape
    for i in shape.slice(FreeCAD.Vector(axis[0],axis[1],axis[2]),d):
        wires.append(i)
    returnObj=doc.addObject("Part::Feature",name)
    returnObj.Shape=Part.Compound(wires)
    return returnObj
