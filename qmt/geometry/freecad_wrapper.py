# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

"""Wrapping FreeCAD calls within a Python 3 environment."""


def pywrapper(input_result_list, current_options, instruction):
    # ~ cmd = os.path.join('freecad', 'run.py')
    # ~ subprocess.call([cmd, ])
    print(instruction)

        # TODO: write a sub2.7 subprocess wrapper
        # at current sweep point:
        # - updateParams
        # - object construction & litography
        # - point region map
