#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Example geometry sweeping."""

import os
import numpy as np

from qmt.geometry import part_3d, build_3d_geometry

# Set up geometry task

block1 = part_3d.ExtrudePart("Parametrised block", "Sketch", thickness=5.0, z0=2.5)

block2 = part_3d.ExtrudePart("Two blocks", "Sketch001", thickness=0.5)

sag = part_3d.SAGPart(
    "Garage", "Sketch002", thickness=6, z_middle=5, t_in=2.5, t_out=0.5, z0=0
)

wire = part_3d.WirePart("Nanowire", "Sketch003", z0=0, thickness=0.5)

shell = part_3d.WireShellPart(
    "Wire cover",
    "Sketch004",
    thickness=0.2,
    target_wire=wire,
    shell_verts=[1, 2],
    depo_mode="depo",
)

substrate = part_3d.ExtrudePart("Substrate", "Sketch005", thickness=2, z0=-2)

wrap = part_3d.LithographyPart(
    "First layer",
    "Sketch006",
    thickness=0.4,
    layer_num=1,
    z0=0,
    litho_base=[substrate, wire, shell],
)

wrap2 = part_3d.LithographyPart("Second Layer", "Sketch007", thickness=0.1, layer_num=2)

virt = part_3d.ExtrudePart("Virtual Domain", "Sketch008", thickness=5.5, virtual=True)

# Parameters for geometry building
input_file = "geometry_sweep_showcase.fcstd"  # contains a model parameter 'd1'
input_parts = [block1, block2, sag, virt, wire, shell, substrate, wrap, wrap2]

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
        print(f'{i}: "{label}" ({part.fc_name} -> {part.built_fc_name}) to STEP file.')
        part.write_stp(os.path.join("tmp", str(i) + "_" + label + ".stp"))
        print(f'{i}: "{label}" ({part.fc_name} -> {part.built_fc_name}) to STL file.')
        part.write_stl(os.path.join("tmp", str(i) + "_" + label + ".stl"))
