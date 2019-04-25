# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

from ._version import __version__

del _version

import os
import sys

# make FreeCAD importable if installed via conda and when using an environment
# remove when https://github.com/conda-forge/freecad-feedstock/issues/21) is fixed
if "CONDA_PREFIX" in os.environ:
    sys.path.append(os.path.join(os.environ["CONDA_PREFIX"], "lib"))

from .physics_constants import units, constants, parse_unit, to_float
from .materials import Materials
