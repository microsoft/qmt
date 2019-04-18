# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

"""Sketch manipulation."""

from copy import deepcopy

import FreeCAD
import Draft
import Part
import Sketcher
import numpy as np

from .auxiliary import *

vec = FreeCAD.Vector


def findSegments(sketch):
    """Return the line segments in a sketch as a numpy array.

    Parameters
    ----------
    sketch :


    Returns
    -------
    A `np.ndarray` of line segments from `sketch`.

    Notes
    -----
    In FC0.17 sketches contain wires by default.
    """
    lineSegments = []
    for wire in sketch.Shape.Wires:
        for edge in wire.Edges:
            lineSegments.append(
                [tuple(edge.Vertexes[0].Point), tuple(edge.Vertexes[1].Point)]
            )
    return np.array(lineSegments)


def nextSegment(lineSegments, segIndex, tol=1e-8, fixOrder=True):
    """Return the next line segment index in a collection of tuples defining
    several cycles. WARNING: this will by default fixOrder, i.e. side effects on
    the caller.

    Parameters
    ----------
    lineSegments :
        ndarray with [lineSegmentIndex,start/end point,coordinate]
    segIndex :
        the index to consider
    tol :
        repair tolerance for matching (Default value = 1e-8)
    fixOrder :
        whether the order lineSegments should be repaired on the fly (Default value = True)

    Returns
    -------
    Line segment.

    """
    # initial end point - all other segment starts
    diffList0 = np.sum(
        np.abs(lineSegments[segIndex, 1, :] - lineSegments[:, 0, :]), axis=1
    )
    # initial end point - all other segment ends
    diffList1 = np.sum(
        np.abs(lineSegments[segIndex, 1, :] - lineSegments[:, 1, :]), axis=1
    )

    diffList0[segIndex] = 1000.0
    diffList1[segIndex] = 1000.0
    nextList0 = np.where(diffList0 <= tol)[0]
    nextList1 = np.where(diffList1 <= tol)[0]
    if len(nextList0) + len(nextList1) > 1:
        raise ValueError(
            "Multiple possible paths found while parsing cycles in sketch."
        )
    elif len(nextList0) + len(nextList1) < 1:
        raise ValueError("No paths found while parsing cycles in sketch.")
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
    """Find a cycle in a collection of line segments given a starting index.

    Parameters
    ----------
    lineSegments :

    startingIndex :

    availSegIDs :


    Returns
    -------


    """
    currentIndex = startingIndex
    segList = [startingIndex]
    for i in availSegIDs:
        currentIndex = nextSegment(
            lineSegments, currentIndex
        )  # throws eventually if not in cycle
        if currentIndex in segList:
            break
        else:
            segList += [currentIndex]
    return segList


# ~ def findCycle2(sketch, lineSegments, idx):
# ~ '''Find a cycle in a collection of line segments given a starting index.
# ~ Return the list of indices in the cycle.
# ~ '''
# ~ # Find wire to which the indexed segment belongs
# ~ # return lineSegment indices of all edges in this wire
# ~ for wire in sketch.Shape.Wires:
# ~ for edge in wire.Edges:
# ~ if idx in wire


def addCycleSketch(name, wire):
    """Add a sketch of a cycle (closed wire) to a FC document.

    Parameters
    ----------
    name :

    wire :


    Returns
    -------


    """
    assert wire.isClosed()
    doc = FreeCAD.ActiveDocument
    if doc.getObject(name) is not None:
        raise ValueError(f"Sketch with name '{name}' already exists.")

    # makeSketch() could handle constraints itself and does recompute() well,
    # but sometimes we may have invalid wires, which it handles badly (fixsometime)
    # ~ return Draft.makeSketch([wire], name=name, autoconstraints=True)

    sketch = doc.addObject("Sketcher::SketchObject", name)
    for i, edge in enumerate(wire.Edges):
        v0 = vec(tuple(edge.Vertexes[0].Point))
        v1 = vec(tuple(edge.Vertexes[1].Point))
        if i > 0:
            if (v0 - old_v1).Length > 1e-5:  # fix invalid wire segments
                v1 = vec(tuple(edge.Vertexes[0].Point))
                v0 = vec(tuple(edge.Vertexes[1].Point))
        old_v1 = v1
        sketch.addGeometry(Part.LineSegment(v0, v1))
        if i > 0:
            sketch.addConstraint(Sketcher.Constraint("Coincident", i - 1, 2, i, 1))
    sketch.addConstraint(Sketcher.Constraint("Coincident", i, 2, 0, 1))
    doc.recompute()
    return sketch


def addPolyLineSketch(name, doc, segmentOrder, lineSegments):
    """Add a sketch given segment order and line segments.

    Parameters
    ----------
    name :

    doc :

    segmentOrder :

    lineSegments :


    Returns
    -------


    """
    if doc.getObject(name) is not None:
        raise ValueError(f"Sketch with name '{name}' already exists.")
    obj = doc.addObject("Sketcher::SketchObject", name)
    for segIndex, segment in enumerate(lineSegments):
        startPoint = segment[0, :]
        endPoint = segment[1, :]
        obj.addGeometry(Part.LineSegment(vec(tuple(startPoint)), vec(tuple(endPoint))))
    for i in range(len(lineSegments)):
        connectIndex = segmentOrder[i]
        if connectIndex < len(lineSegments):
            obj.addConstraint(Sketcher.Constraint("Coincident", i, 2, connectIndex, 1))
    doc.recompute()
    return obj


def findEdgeCycles(sketch):  # TODO: port objectConstruction crossection stuff
    """Find the list of edges in a sketch and separate them into cycles.

    Parameters
    ----------
    sketch :


    Returns
    -------


    """
    lineSegments = findSegments(sketch)
    # Next, detect cycles:
    availSegIDs = range(lineSegments.shape[0])
    cycles = []
    for _ in range(lineSegments.shape[0]):
        if len(availSegIDs) <= 0:
            break
        startingIndex = availSegIDs[0]
        newCycle = findCycle(lineSegments, startingIndex, availSegIDs)
        cycles += [newCycle]
        availSegIDs = [item for item in availSegIDs if item not in newCycle]
    return lineSegments, cycles


def findEdgeCycles2(sketch):
    """Find the list of edges in a sketch and separate them into cycles.

    Parameters
    ----------
    sketch :


    Returns
    -------


    """
    return sketch.Shape.Wires


def splitSketch(sketch):
    """Splits a sketch into several, returning a list of names of the new sketches.

    Parameters
    ----------
    sketch :


    Returns
    -------


    """
    if not sketch.Shape.Wires:
        raise ValueError("No wires in sketch.")
    return [
        addCycleSketch(f"{sketch.Name}_{i}", wire)
        for i, wire in enumerate(sketch.Shape.Wires)
    ]


def extendSketch(sketch, d):
    """For a disconnected polyline, extends the last points of the sketch by
    a distance d.

    Parameters
    ----------
    sketch :

    d :


    Returns
    -------


    """
    doc = FreeCAD.ActiveDocument
    segments = findSegments(sketch)
    connections = []
    for i in range(len(segments)):
        try:
            connecting = nextSegment(segments, i)
        except BaseException:
            connecting = len(segments)
        connections += [connecting]
    # Find the first and last segments:
    seg0Index = [i for i in range(len(segments)) if i not in connections][0]
    seg1Index = connections.index(len(segments))
    segIndices = [seg0Index, seg1Index]

    # Since we automatically reorder these, we know the orientation.
    seg0 = segments[seg0Index]
    x0, y0, z0 = seg0[0]
    x1, y1, z1 = seg0[1]
    dx = x1 - x0
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
    x0, y0, z0 = seg1[0]
    x1, y1, z1 = seg1[1]
    dx = x1 - x0
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

    myNewLine = addPolyLineSketch(
        sketch.Name + "_extension", doc, connections, segments
    )
    return myNewLine


def makeIntoSketch(inputObj, sketchName=None):
    """Turn a 2D generic object like a polyline into a sketch.

    Parameters
    ----------
    inputObj :

    sketchName :
        (Default value = None)

    Returns
    -------


    """
    if sketchName is None:
        sketchName = inputObj.Name + "_sketch"
    returnSketch = Draft.makeSketch(inputObj, autoconstraints=True, name=sketchName)
    deepRemove(obj=inputObj)
    FreeCAD.ActiveDocument.recompute()
    return returnSketch
