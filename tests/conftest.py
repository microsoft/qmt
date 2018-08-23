# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

"""Fixtures for QMT unit tests."""

import os

import pytest

import qmt


@pytest.fixture(scope='session')
def fix_testDir():
    '''Return the test directory path.'''
    rootPath = os.path.join(os.path.dirname(qmt.__file__), os.pardir)
    return os.path.join(rootPath, 'tests')


@pytest.fixture(scope='session')
def fix_exampleDir():
    '''Return the example directory path.'''
    rootPath = os.path.join(os.path.dirname(qmt.__file__), os.pardir)
    return os.path.join(rootPath, 'examples')


@pytest.fixture(scope='function')
def fix_FCDoc():
    '''Set up and tear down a FreeCAD document.'''
    from qmt.geometry.freecad import FreeCAD
    doc = FreeCAD.newDocument('testDoc')
    yield doc
    FreeCAD.closeDocument('testDoc')


################################################################################
# Sketches


@pytest.fixture(scope='function')
def fix_two_cycle_sketch():
    '''Return two-cycle sketch function object.'''

    def aux_two_cycle_sketch(a=(20, 20, 0), b=(-30, 20, 0), c=(-30, -10, 0), d=(20, -10, 0),
                             e=(50, 50, 0), f=(60, 50, 0), g=(55, 60, 0)):
        '''Helper function to drop a simple multi-cycle sketch.
           The segments are ordered into one rectangle and one triangle.
        '''
        # Note: the z-component is zero, as sketches are plane objects.
        #       Adjust orientation with Sketch.Placement(Normal, Rotation)
        import Part
        from qmt.geometry.freecad import FreeCAD
        vec = FreeCAD.Vector
        lseg = Part.LineSegment

        doc = FreeCAD.ActiveDocument
        sketch = doc.addObject('Sketcher::SketchObject', 'Sketch')
        sketch.addGeometry(lseg(vec(*a), vec(*b)), False)
        sketch.addGeometry(lseg(vec(*b), vec(*c)), False)
        sketch.addGeometry(lseg(vec(*c), vec(*d)), False)
        sketch.addGeometry(lseg(vec(*d), vec(*a)), False)

        sketch.addGeometry(lseg(vec(*e), vec(*f)), False)
        sketch.addGeometry(lseg(vec(*f), vec(*g)), False)
        sketch.addGeometry(lseg(vec(*g), vec(*e)), False)
        doc.recompute()
        return sketch

    return aux_two_cycle_sketch


@pytest.fixture(scope='function')
def fix_unit_square_sketch():
    '''Return unit square sketch function object.'''

    def aux_unit_square_sketch():
        '''Helper function to drop a simple unit square sketch.
           The segments are carefully ordered.
        '''
        from qmt.geometry.freecad import FreeCAD
        import Part
        vec = FreeCAD.Vector
        lseg = Part.LineSegment

        a = (0, 0, 0)
        b = (1, 0, 0)
        c = (1, 1, 0)
        d = (0, 1, 0)

        doc = FreeCAD.ActiveDocument
        sketch = doc.addObject('Sketcher::SketchObject', 'Sketch')
        sketch.addGeometry(lseg(vec(*a), vec(*b)), False)
        sketch.addGeometry(lseg(vec(*b), vec(*c)), False)
        sketch.addGeometry(lseg(vec(*c), vec(*d)), False)
        sketch.addGeometry(lseg(vec(*d), vec(*a)), False)
        doc.recompute()
        return sketch

    return aux_unit_square_sketch


@pytest.fixture(scope='function')
def fix_hexagon_sketch():
    '''Return hexagon sketch function object.'''

    def aux_hexagon_sketch(r=1):
        '''Helper function to drop a hexagonal sketch.'''
        from qmt.geometry.freecad import FreeCAD
        import ProfileLib.RegularPolygon
        vec = FreeCAD.Vector
        doc = FreeCAD.ActiveDocument
        sketch = doc.addObject('Sketcher::SketchObject', 'HexSketch')
        ProfileLib.RegularPolygon.makeRegularPolygon('HexSketch', 6, vec(10,10,0), vec(20,20,0), False)
        doc.recompute()
        return sketch

    return aux_hexagon_sketch
