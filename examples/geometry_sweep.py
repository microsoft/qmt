#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Example geometry sweeping."""


import os
import numpy as np

from qmt.task_framework import SweepTag, SweepManager
from qmt.geometry.parts import Part3D
from qmt.basic_tasks.geometry import Geometry3D


# Set up geometry task
tag1 = SweepTag('d1 thickness')
simdomain = Part3D('simdomain', 'Sketch001', 'extrude', 'dielectric',
                   material='air', thickness=1.0, z0=-0.5)
gate = Part3D('gate', 'Sketch', 'extrude', 'metal_gate',
              material='Au', thickness=0.1)
sag = Part3D('shroom', 'Sketch002', 'SAG', 'metal_gate',
              material='Au', z0=0, z_middle=0.9, thickness=1.2,
              t_in=0.1, t_out=0.3)
wire = Part3D('nanowire', 'Line', 'wire', 'semiconductor',
              z0=0, thickness=0.4)
freecad_dict = {
    'pyenv': 'python2',
    'file_path': 'geometry_sweep_playground.fcstd',
    'params': {'d1': tag1},
    'input_parts': [simdomain, gate, sag]
}
geo_task = Geometry3D(options=freecad_dict)

# Run sweeps
sweeps = [{tag1: val} for val in np.arange(2, 8.1, 2)]
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
        # ~ print(len(geo.parts[label].serial_stp))
        geo.parts[label].write_stp('tmp/' + label + str(i) + '.stp')
