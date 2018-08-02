# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

"""Wrapping FreeCAD calls within a Python 3 environment."""


import os
import subprocess
import pickle

import qmt


def fcwrapper(pyenv='python2', instruction=None, data=None):
    """Wrapper to isolate FreeCAD Python 2.7 calls from the Python 3 code base.

    :param str pyenv:       Python interpreter, defaults to 'python2'.
    :param str instruction: A registered instruction for the QMT FreeCAD module.
    :param     data:        Any data type serialisable through pickle.
    """

    qmtPath = os.path.join(os.path.dirname(qmt.__file__))
    runPath = os.path.join(qmtPath, 'geometry', 'freecad', 'run.py')
    serial_data = pickle.dumps(data,protocol=2)
    proc = subprocess.Popen([pyenv, runPath, instruction],
                            stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output = proc.communicate(serial_data)
    # output[1] not checked because stderr is used for mere warnings too often
    if proc.returncode != 0:
        raise ValueError('pywrapper error ' + str(proc.returncode) + ' (' + str(output[1]) + ')')

    # The data should be passed out as a byte stream. The initial stuff written by freeCAD is
    # in position 0, then the seperateor string "MAGICTQMTRANSFERBYTES" is used to mark the start
    # of the serialized data stream to send back:
    serial_data = output[0].decode().split('MAGICTQMTRANSFERBYTES')[-1].encode()
    return pickle.loads(serial_data)

    # try:
    #     serial_data = ''.join(output[0]).split('MAGICTQMTRANSFERBYTES')[-1]
    #     return pickle.loads(serial_data)
    # except:
    #     return output[0]
