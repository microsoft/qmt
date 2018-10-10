#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Example geometry sweeping."""

import os
import numpy as np

from qmt.data import Part3DData
from qmt.tasks.basic.geometry import Geometry3D
from qmt.tasks.sweep import SweepTag, SweepManager

# Set up geometry task
tag1 = SweepTag('d1 thickness')
block1 = Part3DData('Parametrised block', 'Sketch', 'extrude', 'dielectric',
                material='air', thickness=5.0, z0=-2.5)
block2 = Part3DData('Two blocks', 'Sketch001', 'extrude', 'metal_gate',
                material='Au', thickness=0.5)
sag = Part3DData('Garage', 'Sketch002', 'SAG', 'metal_gate',
                material='Au', z0=0, z_middle=5, thickness=6,
                t_in=2.5, t_out=0.5)
wire = Part3DData('Nanowire', 'Sketch003', 'wire', 'semiconductor',
                z0=0, thickness=0.5)
shell = Part3DData('Wire cover', 'Sketch004', 'wire_shell', 'metal_gate',
                depo_mode='depo', target_wire=wire, thickness=0.2, shell_verts=[1, 2])
block3 = Part3DData('Passthrough', 'Box', '3d_shape', 'metal_gate')
substrate = Part3DData('Substrate', 'Sketch005', 'extrude', 'dielectric',
                z0=-2, thickness=2)
wrap = Part3DData('First Layer', 'Sketch006', 'lithography', 'dielectric',
                z0=0, layer_num=1, thickness=0.4, litho_base=[substrate, wire])
wrap2 = Part3DData('Second Layer', 'Sketch007', 'lithography', 'dielectric',
                layer_num=2, thickness=1)

freecad_dict = {
    'pyenv': 'python2',
    'input_file': 'geometry_sweep_showcase.fcstd',
    'input_parts': [block1, block2, sag, wire, shell, block3, substrate, wrap, wrap2],
    'params': {'d1': tag1}
}
geo_task = Geometry3D(options=freecad_dict)

# Run sweeps
sweeps = [{tag1: val} for val in np.linspace(2, 7, 3)]
result = SweepManager(sweeps).run(geo_task)

# Investigate results
if not os.path.exists('tmp'):
    os.makedirs('tmp')
print("Writing in directory tmp:")

for i, future in enumerate(result.futures):
    geo = future.result()
    print('Writing instance ' + str(i) + ' to FreeCAD file.')
    geo.write_fcstd('tmp/' + str(i) + '.fcstd')
    for label, part in geo.parts.items():
        print(str(i) + ': ' + label +
              ' (' + part.fc_name + ' -> ' + part.built_fc_name + ') to STEP file.')
        part.write_stp('tmp/' + label + str(i) + '.stp')
