#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Example geometry sweeping."""

import os
import numpy as np

from qmt.data import Part3DData
from qmt.tasks import build_3d_geometry

# Set up geometry task

substrate = Part3DData(
    "Substrate", "Sketch027", "extrude", "dielectric", z0=-2, thickness=2
)

gate1 = Part3DData(
    "Gate 1", "Sketch", "extrude", "metal_gate", material="Au", z0=0, thickness=10
)
gate2 = Part3DData(
    "Gate 2", "Sketch003", "extrude", "metal_gate", material="Au", z0=0, thickness=10
)
gate3 = Part3DData(
    "Gate 3", "Sketch006", "extrude", "metal_gate", material="Au", z0=0, thickness=10
)
gate4 = Part3DData(
    "Gate 4", "Sketch011", "extrude", "metal_gate", material="Au", z0=0, thickness=10
)


wrap1 = Part3DData(
    "First Wrap",
    "Sketch028",
    "lithography",
    "dielectric",
    z0=0.0,
    layer_num=1,
    thickness=2,
    litho_base=[substrate, gate1, gate2, gate3, gate4],
)

layer2 = Part3DData(
    "Layer 2",
    "Sketch025",
    "lithography",
    "metal_gate",
    material="Au",
    z0=0,
    thickness=10.0,
    layer_num=2,
)

wrap2 = Part3DData(
    "Second Wrap",
    "Sketch029",
    "lithography",
    "dielectric",
    z0=0.0,
    layer_num=3,
    thickness=2,
)

layer3 = Part3DData(
    "Layer 3", "Sketch026", "extrude", "metal_gate", material="Au", z0=0, thickness=30
)

# Parameters for geometry building
input_file = "qd_device_parts.fcstd"
input_parts = [substrate, gate1, gate2, gate3, gate4, wrap1, layer2, wrap2, layer3]

# Compute parametrised geometries in parallel with dask
geo = build_3d_geometry(input_parts=input_parts, input_file=input_file)

# Create a local temporary directory to investigate results
if not os.path.exists("tmp"):
    os.makedirs("tmp")
print("Writing in directory tmp:")

print("Writing parametrised instance to FreeCAD file.")
geo.write_fcstd(os.path.join("tmp.fcstd"))
for label, part in geo.parts.items():
    print(f'"{label}" ({part.fc_name} -> {part.built_fc_name}) to STL file.')
    part.write_stl(os.path.join("tmp", label + ".stl"))
