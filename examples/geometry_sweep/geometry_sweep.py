#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Example geometry sweeping."""

import os
import numpy as np

from qmt.data import Part3DData
from qmt.tasks import build_3d_geometry

# Set up geometry task
block1 = Part3DData(
    "Parametrised block",
    "Sketch",
    "extrude",
    "dielectric",
    material="air",
    thickness=5.0,
    z0=-2.5,
)
block2 = Part3DData(
    "Two blocks", "Sketch001", "extrude", "metal_gate", material="Au", thickness=0.5
)
sag = Part3DData(
    "Garage",
    "Sketch002",
    "SAG",
    "metal_gate",
    material="Au",
    z0=0,
    z_middle=5,
    thickness=6,
    t_in=2.5,
    t_out=0.5,
)
wire = Part3DData("Nanowire", "Sketch003", "wire", "semiconductor", z0=0, thickness=0.5)
shell = Part3DData(
    "Wire cover",
    "Sketch004",
    "wire_shell",
    "metal_gate",
    depo_mode="depo",
    target_wire=wire,
    thickness=0.2,
    shell_verts=[1, 2],
)
block3 = Part3DData("Passthrough", "Box", "3d_shape", "metal_gate")
substrate = Part3DData(
    "Substrate", "Sketch005", "extrude", "dielectric", z0=-2, thickness=2
)
wrap = Part3DData(
    "First Layer",
    "Sketch006",
    "lithography",
    "dielectric",
    z0=0,
    layer_num=1,
    thickness=0.4,
    litho_base=[substrate, wire, shell],
)
wrap2 = Part3DData(
    "Second Layer", "Sketch007", "lithography", "dielectric", layer_num=2, thickness=0.1
)
virt = Part3DData("Virtual Domain", "Sketch008", "extrude", "virtual", thickness=5.5)

# Parameters for geometry building
input_file = "geometry_sweep_showcase.fcstd"  # contains a model parameter 'd1'
input_parts = [block1, block2, sag, virt, wire, shell, block3, substrate, wrap, wrap2]

# Compute parametrised geometries in parallel with dask
geometries = []
for d1 in np.linspace(2.0, 7.0, 3):
    geometries.append(
        build_3d_geometry(
            input_parts=input_parts, input_file=input_file, params={"d1": d1}
        )
    )

# Create a local temporary directory to investigate results
if not os.path.exists("tmp"):
    os.makedirs("tmp")
print("Writing in directory tmp:")

for i, geo in enumerate(geometries):
    print("Writing parametrised instance " + str(i) + " to FreeCAD file.")
    geo.write_fcstd(os.path.join("tmp", str(i) + ".fcstd"))
    for label, part in geo.parts.items():
        print(
            str(i)
            + ': "'
            + label
            + '" ('
            + part.fc_name
            + " -> "
            + part.built_fc_name
            + ") to STEP file."
        )
        part.write_stp(os.path.join("tmp", str(i) + "_" + label + ".stp"))
        print(
            str(i)
            + ': "'
            + label
            + '" ('
            + part.fc_name
            + " -> "
            + part.built_fc_name
            + ") to STL file."
        )
        part.write_stl(os.path.join("tmp", str(i) + "_" + label + ".stl"))
