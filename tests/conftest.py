# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

"""Fixtures for QMT unit tests."""


import os
import sys
import pytest

import qmt


@pytest.fixture(scope='session')
def fix_py2env():
    '''Change this to your python2.7 environment.'''

    py2env = 'python2'

    not_found_error = FileNotFoundError if sys.version_info[0] >= 3 else OSError
    try:
        import subprocess
        p = subprocess.Popen([py2env, '--version'])
        p.terminate()
    except not_found_error:
        raise ValueError('Invalid Python 2.7 environment in py2env fixture. ' +
                         'Please edit this in ' + __file__)
    return py2env


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
    import FreeCAD
    doc = FreeCAD.newDocument('testDoc')
    yield doc
    FreeCAD.closeDocument('testDoc')


@pytest.fixture(scope='function')
def fix_setup_docker():
    '''Build the docker image to run tests'''
    import subprocess
    subprocess.check_call(['docker', 'pull', 'johnkgamble/qmt_base'])
    build_path = os.path.join(os.path.dirname(qmt.__file__), '..')
    subprocess.check_call(['docker', 'build', '-t', 'qmt:master', '.'], cwd=build_path)


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
        ProfileLib.RegularPolygon.makeRegularPolygon('HexSketch', 6, vec(1, 1, 0), vec(1+r, 1, 0), False)
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
    from qmt.tasks import Task
    import numpy as np

    class InputTaskExample(Task):
        """Simple example task. This is the first task in the chain.

        :param dict options: Dictionary specifying the input parts. It should be of the form
        {"part":list_of_points}.
        :param str name: Name of the task.
        """
        def __init__(self, options=None, name='input_task'):
            super(InputTaskExample, self).__init__([], options, name)

        @staticmethod
        def _solve_instance(input_result_list, current_options):
            for key_val in input_result_list:
                print(key_val) + ' ' + str(input_result_list[key_val])
            return current_options

    class GatheredTaskExample(Task):
        """Takes the example task and does some work on it. This is a gathered task, which means
        that all the previous work is gathered up and worked on together.

        :param dict options: Dictionary specifying the desired number of grid points. It should
        be of the form {"numpoints":int}.
        :param str name: Name of the task.
        """
        def __init__(self, input_task, options=None, name='gathered_task', gather=True):
            super(GatheredTaskExample, self).__init__([input_task], options, name, gather=gather)

        @staticmethod
        def _solve_gathered(list_of_input_result_lists, list_of_options, result_sweep):
            for sweep_holder_index, tag_values in enumerate(result_sweep.tagged_value_list):
                geometry_obj = list_of_input_result_lists[sweep_holder_index][0]
                mesh = {}
                for part in geometry_obj:
                    mesh[part] = np.linspace(0.0, 1.0,
                                             list_of_options[sweep_holder_index]['numpoints'])
                result_sweep.add(mesh, sweep_holder_index)
            return result_sweep

    class PostProcessingTaskExample(Task):
        """Takes input from the gathered task and does some more work in parallel.

        :param dict options: Dictionary specifying the desired number of grid points. It should
        be of the form {"prefactor":float}.
        :param str name: Name of the task.
        """
        def __init__(self, input_task, gathered_task, options=None, name='post_proc_task'):
            super(PostProcessingTaskExample, self).__init__([input_task, gathered_task], options, name)

        @staticmethod
        def _solve_instance(input_result_list, current_options):
            input_task_result = input_result_list[0]
            gathered_task_result = input_result_list[1]
            result = 0.0
            for part in input_task_result:
                result += (current_options['prefactor'] * np.sum(input_task_result[part]) *
                           np.sum(gathered_task_result[part]))
            return result

    return InputTaskExample, GatheredTaskExample, PostProcessingTaskExample
