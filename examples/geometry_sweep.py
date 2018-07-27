#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Example geometry sweeping."""


import os
import numpy as np

import qmt.task_framework as qtf
from qmt.geometry.parts import Part3D
from qmt.basic_tasks.geometry import Geometry3D


# Set up geometry task
tag = qtf.SweepTag('thickness')
myPart = Part3D('block_of_gold', 'Sketch', 'extrude', 'metalGate',
                material='Au', thickness=10)
freecad_dict = {
    'pyenv': 'python2',
    'file_path': 'geometry_sweep.fcstd',
    'params': {'d1': tag},
    'input_parts': [myPart]
}
geo_task = Geometry3D(options=freecad_dict)

# Run sweeps
sweeps = [{tag: val} for val in np.arange(2, 10, 2)]
result = qtf.SweepManager(sweeps).run(geo_task)

# Investigate results
if not os.path.exists('tmp'):
    os.mkdirs('tmp')
print("Writing in directory tmp:")
for i, future in enumerate(result.futures):
    geo = future.result()
    print('Writing instance ' + str(i) + ' to FreeCAD file.')
    geo.write_fcstd('tmp/' + str(i) + '.fcstd')
    for label in geo.parts:
        print('Writing instance ' + str(i) + ' of ' + label + ' to STEP file.')
        geo.parts[label].write_stp('tmp/' + label + str(i) + '.stp')
