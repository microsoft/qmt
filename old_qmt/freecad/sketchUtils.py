# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

###
### Functions that work with sketches
###

import FreeCAD
from copy import deepcopy

import Draft
import Part
import Sketcher
import numpy as np


def deepRemove_impl(obj):
    for child in obj.OutList:
        deepRemove_impl(child)
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
    deepRemove_impl(obj)
    doc.recompute()


def delete(obj):
    doc = FreeCAD.ActiveDocument
    doc.removeObject(obj.Name)
    doc.recompute()


def findSegments(sketch):
    '''Return the line segments in a sketch as a numpy array.
    '''
    lineSegments = []
    # The old way would also discover guide segments, which we probably don't want to do...
    # for seg in sketch.Geometry:
    #     lineSegments += [[[seg.StartPoint[0], seg.StartPoint[1], seg.StartPoint[2]], \
    #                       [seg.EndPoint[0], seg.EndPoint[1], seg.EndPoint[2]]]]
    # ~ for edge in sketch.Shape.Edges:
        # ~ lineSegments.append([tuple(edge.Vertexes[0].Point), tuple(edge.Vertexes[1].Point)])
    for wire in sketch.Shape.Wires:  # fc17: wires should be defined for all sketches
        for edge in wire.Edges:
            lineSegments.append([tuple(edge.Vertexes[0].Point), tuple(edge.Vertexes[1].Point)])
    # TODO: reuse list of wires for cycles
    return np.array(lineSegments)


def nextSegment(lineSegments, segIndex, tol=1e-8, fixOrder=True):
    '''Return the next line segment index in a collection of tuples defining
    several cycles.
    WARNING: this will by default fixOrder, i.e. side effects on the caller.

    Args:
        lineSegments: ndarray with [lineSegmentIndex,start/end point,coordinate]
        segIndex:     the index to consider
        tol:          repair tolerance for matching
        fixOrder:     whether the order lineSegments should be repaired on the fly
    '''
    diffList0 = np.sum(np.abs(lineSegments[segIndex, 1, :] - lineSegments[:, 0, :]), axis=1) # initial end point - all other segment starts
    diffList1 = np.sum(np.abs(lineSegments[segIndex, 1, :] - lineSegments[:, 1, :]), axis=1) # initial end point - all other segment ends
    diffList0[segIndex] = 1000.
    diffList1[segIndex] = 1000.
    nextList0 = np.where(diffList0 <= tol)[0]
    nextList1 = np.where(diffList1 <= tol)[0]
    if len(nextList0) + len(nextList1) > 1:
        raise ValueError('Multiple possible paths found while parsing cycles in sketch.')
    elif len(nextList0) + len(nextList1) < 1:
        raise ValueError('No paths found while parsing cycles in sketch.')
    elif len(nextList0) == 1:
        return nextList0[0]
    else:
        if fixOrder:
            # the points were out of order, so they need to be switched            
            nextPoint0 = deepcopy(lineSegments[nextList1[0], 0, :])
            nextPoint1 = deepcopy(lineSegments[nextList1[0], 1, :])
            lineSegments[nextList1[0], 0, :] = nextPoint1
            lineSegments[nextList1[0], 1, :] = nextPoint0
        return nextList1[0]


def findCycle(lineSegments, startingIndex, availSegIDs):
    '''Find a cycle in a collection of line segments given a starting index.
    Return the list of indices in the cycle.
    '''
    currentIndex = startingIndex
    segList = [startingIndex]
    for i in availSegIDs:
        currentIndex = nextSegment(lineSegments, currentIndex)  # throws eventually if not in cycle
        if currentIndex in segList:
            break
        else:
            segList += [currentIndex]
    return segList


def addCycleSketch(name, fcDoc, cycleSegIndList, lineSegments):
    ''' Add a sketch of a cycle to a FC document.
    '''
    if (fcDoc.getObject(name) != None):  # this name already exists
        raise ValueError("Error: sketch " + name + " already exists.")
    obj = fcDoc.addObject('Sketcher::SketchObject', name)
    vec = FreeCAD.Vector
    # obj.MapMode = 'FlatFace'
    obj = fcDoc.getObject(name)
    cnt = 0
    for segIndex in cycleSegIndList:
        startPoint = lineSegments[segIndex, 0, :]
        endPoint = lineSegments[segIndex, 1, :]
        obj.addGeometry(Part.LineSegment(vec(tuple(startPoint)), vec(tuple(endPoint))))
        cnt += 1
        if cnt <= 1:
            continue
        obj.addConstraint(Sketcher.Constraint('Coincident', cnt - 2, 2, cnt - 1, 1))
    obj.addConstraint(Sketcher.Constraint('Coincident', cnt - 1, 2, 0, 1))
    fcDoc.recompute()
    return obj


def addPolyLineSketch(name, fcDoc, segmentOrder, lineSegments):
    ''' Add a sketch given segment order and line segments
    '''
    if (fcDoc.getObject(name) != None):  # this name already exists
        raise ValueError("Error: sketch " + name + " already exists.")
    obj = fcDoc.addObject('Sketcher::SketchObject', name)
    for segIndex, segment in enumerate(lineSegments):
        startPoint = segment[0, :]
        endPoint = segment[1, :]
        obj.addGeometry(Part.LineSegment(FreeCAD.Vector(tuple(startPoint)), FreeCAD.Vector(tuple(endPoint))))
    for i in range(len(lineSegments)):
        connectIndex = segmentOrder[i]
        if connectIndex < len(lineSegments):
            obj.addConstraint(Sketcher.Constraint('Coincident', i, 2, connectIndex, 1))
    fcDoc.recompute()
    return obj


def findEdgeCycles(sketch):
    """Find the list of edges in a sketch and separate them into cycles."""
    lineSegments = findSegments(sketch)
    # Next, detect cycles:
    availSegIDs = range(lineSegments.shape[0])
    cycles = []
    for i in range(len(availSegIDs)):
        if len(availSegIDs) > 0:
            startingIndex = availSegIDs[0]
            newCycle = findCycle(lineSegments, startingIndex, availSegIDs)
            cycles += [newCycle]
            availSegIDs = [item for item in availSegIDs if item not in newCycle]
    return lineSegments, cycles


def splitSketch(sketch):
    '''Splits a sketch into several, returning a list of names of the new sketches.
    '''
    lineSegments, cycles = findEdgeCycles(sketch)
    # Finally, add new sketches based on the cycles:
    myDoc = FreeCAD.ActiveDocument
    currentSketchName = sketch.Name
    cycleObjList = []
    for i, cycle in enumerate(cycles):
        cycleObj = addCycleSketch(currentSketchName + '_' + str(i),
                                  myDoc, cycle, lineSegments)
        cycleObjList += [cycleObj]
    return cycleObjList


def extendSketch(sketch, d):
    ''' For a disconnected polyline, extends the last points of the sketch by 
    a distance d. 
    '''
    doc = FreeCAD.ActiveDocument
    segments = findSegments(sketch)
    connections = []
    for i in range(len(segments)):
        try:
            connecting = nextSegment(segments, i)
        except:
            connecting = len(segments)
        connections += [connecting]
    # Find the first and last segments:
    seg0Index = [i for i in range(len(segments)) if i not in connections][0]
    seg1Index = connections.index(len(segments))
    segIndices = [seg0Index, seg1Index]

    # Since we automatically reorder these, we know the orientation. 
    seg0 = segments[seg0Index]
    x0, y0, z0 = seg0[0];
    x1, y1, z1 = seg0[1]
    dx = x1 - x0;
    dy = y1 - y0
    alpha = np.abs(np.arctan(dy / dx))
    if x0 < x1:
        x0p = x0 - np.cos(alpha) * d
    else:
        x0p = x0 + np.cos(alpha) * d
    if y0 < y1:
        y0p = y0 - np.sin(alpha) * d
    else:
        y0p = y0 + np.sin(alpha) * d
    segments[seg0Index][0][0] = x0p
    segments[seg0Index][0][1] = y0p

    seg1 = segments[seg1Index]
    x0, y0, z0 = seg1[0];
    x1, y1, z1 = seg1[1]
    dx = x1 - x0;
    dy = y1 - y0
    alpha = np.abs(np.arctan(dy / dx))
    if x1 < x0:
        x1p = x1 - np.cos(alpha) * d
    else:
        x1p = x1 + np.cos(alpha) * d
    if y1 < y0:
        y1p = y1 - np.sin(alpha) * d
    else:
        y1p = y1 + np.sin(alpha) * d
    segments[seg1Index][1][0] = x1p
    segments[seg1Index][1][1] = y1p

    myNewLine = addPolyLineSketch(sketch.Name + '_extension', doc, connections, segments)
    return myNewLine


def makeIntoSketch(inputObj, sketchName=None):
    ''' Turn a 2D generic object like a polyline into a sketch.
    '''
    if sketchName is None:
        sketchName = inputObj.Name + '_sketch'
    returnSketch = Draft.makeSketch(inputObj, autoconstraints=True, name=sketchName)
    deepRemove(obj=inputObj)
    FreeCAD.ActiveDocument.recompute()
    return returnSketch

def draftOffset(inputSketch,t):
    ''' Attempt to offset the draft figure by a thickness t. Positive t is an
    inflation, while negative t is a deflation.
    '''
    from qmt.freecad import extrude,copy, delete

    if t == 0.:
        return copy(inputSketch)
    deltaT = np.abs(t)
    offsetVec1 =FreeCAD.Vector(-deltaT,-deltaT,0.)
    offsetVec2 = FreeCAD.Vector(deltaT,deltaT,0.)
    
    offset0 = copy(inputSketch)
    offset1 = Draft.offset(inputSketch,offsetVec1,copy=True)
    offset2 = Draft.offset(inputSketch,offsetVec2,copy=True)

    solid0 = extrude(offset0,10.0)
    solid1 = extrude(offset1,10.0)
    solid2 = extrude(offset2,10.0)

    # Compute the volumes of these solids:
    V0 = solid0.Shape.Volume
    try:
        V1 = solid1.Shape.Volume
    except:
        V1 = None
    try:
        V2 = solid2.Shape.Volume
    except:
        V2 = None

    # If everything worked properly, these should either be ordered as
    # V1<V0<V2 or V2<V0<V1:
    if V2>V0 and V0>V1:
        bigSketch = offset2; littleSketch = offset1
    elif V1>V0 and V0>V2:
        bigSketch = offset1; littleSketch = offset2
    elif V2>V1 and V1>V0:
        bigSketch = offset2; littleSketch = None
    # If we aren't in correct case, we still might be able to salvage things
    # for certain values of t:
    elif V1>V2 and V2>V0:
        bigSketch = offset1; littleSketch = None
    elif V2<V1 and V1<V0:
        bigSketch = None; littleSketch = offset2
    elif V1<V2 and V2<V0:
        bigSketch = None; littleSketch = offset1
    else:
        bigSketch = None; littleSketch = None
    delete(solid0)
    delete(solid1)
    delete(solid2)
    if t<0 and littleSketch is not None:
        returnSketch = copy(littleSketch)
    elif t>0 and bigSketch is not None:
        returnSketch = copy(bigSketch)
    else:
        raise ValueError('Failed to offset the sketch '+str(inputSketch.Name)+' by amount '+str(t))
    
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
    #         returnSketch = copy(offset1)
    #     else:
    #         returnSketch = copy(offset2)
    # elif t<0:
    #     if positiveOffsetIndex == 1:
    #         returnSketch = copy(offset2)
    #     else:
    #         returnSketch = copy(offset1)
    delete(offset0)
    delete(offset1)
    delete(offset2)
    return returnSketch

