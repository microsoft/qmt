#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Example geometry sweeping for electrostatically-gated quantum dot device.
NOTE: The syntax of this example should match the test test_geo_task.
      If it does not, this example needs to be updated.
"""

import os
import numpy as np

from qmt.geometry import part_3d, build_3d_geometry

# Set up geometry task

substrate = part_3d.ExtrudePart("Substrate", "Sketch027", z0=-2, thickness=2.0)

gate1 = part_3d.ExtrudePart("Gate 1", "Sketch", z0=0, thickness=10)

gate2 = part_3d.ExtrudePart("Gate 2", "Sketch003", z0=0, thickness=10)

gate3 = part_3d.ExtrudePart("Gate 3", "Sketch006", z0=0, thickness=10)

gate4 = part_3d.ExtrudePart("Gate 4", "Sketch011", z0=0, thickness=10)

wrap1 = part_3d.LithographyPart(
    "Wrap 1",
    "Sketch028",
    z0=0,
    thickness=2,
    layer_num=1,
    litho_base=[substrate, gate1, gate2, gate3, gate4],
)

layer2 = part_3d.LithographyPart(
    "Layer 2", "Sketch025", z0=0, thickness=10, layer_num=2
)

wrap2 = part_3d.LithographyPart("Wrap 2", "Sketch029", z0=0, thickness=2, layer_num=3)

layer3 = part_3d.ExtrudePart("Layer 3", "Sketch026", z0=0, thickness=30)

# Parameters for geometry building
input_file = "qd_device_parts.fcstd"
input_parts = [substrate, gate1, gate2, gate3, gate4, wrap1, layer2, wrap2, layer3]

# Compute parametrised geometries in parallel with dask
geo = build_3d_geometry(input_parts=input_parts, input_file=input_file)

# Create a local temporary directory to investigate results
os.makedirs("tmp", exist_ok=True)

print("Writing in directory tmp:")

print("Writing parametrised instance to FreeCAD file.")
geo.write_fcstd(os.path.join("tmp", "tmp.fcstd"))
for label, part in geo.parts.items():
    print(f'"{label}" ({part.fc_name} -> {part.built_fc_name}) to STL file.')
    part.write_stl(os.path.join("tmp", label + ".stl"))
