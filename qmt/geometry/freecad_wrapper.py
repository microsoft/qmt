# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

"""Wrapping FreeCAD calls within a Python 3 environment."""


import os
import subprocess
import pickle

import qmt


def pywrapper(pyenv, instruction, input_result_list, current_options):
    """The one and only wrapper function."""

    qmtPath = os.path.join(os.path.dirname(qmt.__file__))
    runPath = os.path.join(qmtPath, 'geometry', 'freecad', 'run.py')
    data = pickle.dumps({'input_result_list': input_result_list,
                         'current_options': current_options})

    proc = subprocess.Popen([pyenv, runPath, instruction],
                            stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output = proc.communicate(data)
    if proc.returncode != 0 or output[1] != '':
        raise ValueError('pywrapper error ' + str(proc.returncode) + ' (' + output[1] + ')')

    try:
        return pickle.loads(''.join(output[0]))
    except:
        return output[0]
