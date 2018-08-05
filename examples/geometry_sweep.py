#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Example geometry sweeping."""


import os
import numpy as np

from qmt.task_framework import SweepTag, SweepManager
from qmt.geometry.parts import Part3D
from qmt.basic_tasks.geometry import Geometry3D


# Set up geometry task
tag = SweepTag('thickness')
simdomain = Part3D('simdomain', 'Sketch001', 'extrude', 'dielectric',
                   material='air', thickness=1.0, z0=-0.5)
gate = Part3D('gate', 'Sketch', 'extrude', 'metal_gate',
              material='Au', thickness=0.1)
wire = Part3D('wire', 'Sketch002', 'SAG', 'metal_gate',
              material='Au', z0=-1, z_middle=0.1, thickness=1.5,
              t_in=0.1, t_out=0.3)
freecad_dict = {
    'pyenv': 'python2',
    'file_path': 'geometry_sweep_3objs.fcstd',
    'params': {'d1': tag},
    'input_parts': [simdomain,gate,wire]
}
geo_task = Geometry3D(options=freecad_dict)

# Run sweeps
sweeps = [{tag: val} for val in np.arange(2, 10, 2)]
result = SweepManager(sweeps).run(geo_task)

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
