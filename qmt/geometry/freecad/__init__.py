# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

"""FreeCAD routines running in a Python 2.7 environment."""

import logging

logging.basicConfig(level=logging.ERROR,
                    format='%(levelname)s(%(name)s) %(funcName)s:%(lineno)d  %(message)s')
# ~ logging.getLogger().setLevel(logging.DEBUG)  # toggle debug logging for this module
