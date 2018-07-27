# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

"""Wrapping FreeCAD calls within a Python 3 environment."""


import os
import subprocess
import pickle

import qmt


def fcwrapper(pyenv, instruction, data):
    """The one and only wrapper function."""

    qmtPath = os.path.join(os.path.dirname(qmt.__file__))
    runPath = os.path.join(qmtPath, 'geometry', 'freecad', 'run.py')
    serial_data = pickle.dumps(data)

    proc = subprocess.Popen([pyenv, runPath, instruction],
                            stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output = proc.communicate(serial_data)
    # output[1] not checked because stderr is used for mere warnings too often
    if proc.returncode != 0:
        raise ValueError('pywrapper error ' + str(proc.returncode) + ' (' + output[1] + ')')

    try:
        return pickle.loads(''.join(output[0]))
    except:
        return output[0]
