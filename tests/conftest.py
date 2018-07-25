# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

"""Fixtures for QMT unit tests."""

import os
import pytest

import qmt
import FreeCAD


@pytest.fixture(scope='session')
def fix_testDir():
    '''Return the test directory path.'''
    rootPath = os.path.join(os.path.dirname(qmt.__file__), os.pardir)
    return os.path.join(rootPath, 'tests')


# ~ @pytest.fixture(scope='session')
# ~ def fix_modelPath():
    # ~ '''Return the model path.'''
    # ~ return os.path.join(fix_testDir(), 'testModel.json')


# ~ @pytest.fixture(scope='function')
# ~ def fix_model():
    # ~ '''Return a fresh QMT model instance.'''
    # ~ return qmt.Model()


@pytest.fixture(scope='function')
def fix_FCDoc():
    '''Set up and tear down a FreeCAD document.'''
    doc = FreeCAD.newDocument('testDoc')
    yield doc
    FreeCAD.closeDocument('testDoc')
