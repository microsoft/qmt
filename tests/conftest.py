# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

"""Fixtures for QMT unit tests."""

import os
import sys
import pytest

import qmt


@pytest.fixture(scope='session')
def fix_testDir():
    '''Return the test directory path.'''
    rootPath = os.path.join(os.path.dirname(qmt.__file__), os.pardir)
    return os.path.abspath(os.path.join(rootPath, 'tests'))


@pytest.fixture(scope='session')
def fix_exampleDir():
    '''Return the example directory path.'''
    rootPath = os.path.join(os.path.dirname(qmt.__file__), os.pardir)
    return os.path.abspath(os.path.join(rootPath, 'examples'))


@pytest.fixture(scope='function')
def fix_FCDoc():
    '''Set up and tear down a FreeCAD document.'''
    import FreeCAD
    doc = FreeCAD.newDocument('testDoc')
    yield doc
    FreeCAD.closeDocument('testDoc')


@pytest.fixture(scope='session')
def fix_host_settings(fix_testDir):
    '''Host specific settings.'''
    schema = {
        'py2env': '/usr/local/envs/py27/bin/python'
        }

    import yaml
    settings_file = os.path.join(fix_testDir, 'host_settings.yml')
    if not os.path.exists(settings_file):
        with open(settings_file, 'a') as f:
            yaml.dump(schema, f, default_flow_style=False)
    with open(settings_file) as f:
        data = yaml.load(f)
    data['settings_file'] = settings_file
    return data


@pytest.fixture(scope='session')
def fix_py2env(fix_host_settings):
    '''Host setting for python2.7 environment.'''
    py2env = fix_host_settings['py2env']
    try:
        import subprocess
        p = subprocess.Popen([py2env, '-c', 'import sys; print sys.version_info'],
                             stdout=subprocess.PIPE)
        assert 'sys.version_info(major=2, minor=7' in p.communicate()[0].decode()
    except:
        raise RuntimeError('Invalid path to Python 2.7 environment (' + str(py2env) +
                           ') in ' + fix_host_settings['settings_file'] + '. ' +
                           'Please edit this file.')
    return py2env


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
        import FreeCAD
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
        import FreeCAD
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
        import FreeCAD
        import ProfileLib.RegularPolygon
        vec = FreeCAD.Vector
        doc = FreeCAD.ActiveDocument
        sketch = doc.addObject('Sketcher::SketchObject', 'HexSketch')
        ProfileLib.RegularPolygon.makeRegularPolygon('HexSketch', 6, vec(1, 1, 0), vec(1 + r, 1, 0),
                                                     False)
        doc.recompute()
        return sketch

    return aux_hexagon_sketch


################################################################################
# Tasks environment

@pytest.fixture(scope='function')
def fix_task_env():
    """
    Set up a testing environment for tasks.
    """
    import numpy as np

    def input_task_example(parts_dict):
        """Simple example task. This is the first task in the chain.

        :param dict parts_dict: Dictionary specifying the input parts. It should be of the form
        {"part":list_of_points}.
        """
        for key_val in parts_dict:
            print(str(key_val) + ' ' + str(parts_dict[key_val]))
        return parts_dict

    def gathered_task_example(input_data_list, num_points):
        """Takes the example task and does some work on it. This is a gathered task, which means
        that all the previous work is gathered up and worked on together.

        :param list input_data_list: List of dictionaries from several input tasks.
        :param list num_points: List of ints specifying the number of grid points for a given
        geometry.
        """
        return_list = []
        for i, geom in enumerate(input_data_list):
            geometry_obj = input_data_list[i]
            mesh = {}
            for part in geometry_obj:
                mesh[part] = np.linspace(0.0, 1.0, num_points[i])
            return_list += [mesh]
        return return_list

    def post_processing_task_example(input_data, gathered_data, prefactor):
        """Takes input from the gathered task and does some more work in parallel.

        :param dict input_data: An input geometry.
        :param dict gathered_data: One of the meshes produced from gathered_task_example.
        :param float prefactor: Prefactor used to scale the output
        """
        result = 0.0
        for part in input_data:
            result += prefactor * np.sum(input_data[part]) * np.sum(gathered_data[part])
        return result

    return input_task_example, gathered_task_example, post_processing_task_example
