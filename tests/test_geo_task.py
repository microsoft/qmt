# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

"""Testing the geometry task."""


import numpy as np
import os
import tempfile
from qmt.geometry import part_3d, build_3d_geometry


def test_geo_task(datadir):
    """
    Tests the build geometry task. For now, just verifies that the build doesn't encounter errors.
    """

    block1 = part_3d.ExtrudeData("Parametrised block", "Sketch", thickness=5.0, z0=-2.5)
    block2 = part_3d.ExtrudeData("Two blocks", "Sketch001", thickness=0.5)
    sag = part_3d.SAGData(
        "Garage", "Sketch002", z0=0, z_middle=5, thickness=6, t_in=2.5, t_out=0.5
    )
    wire = part_3d.WireData("Nanowire", "Sketch003", z0=0, thickness=0.5)
    shell = part_3d.WireShellData(
        "Wire cover",
        "Sketch004",
        depo_mode="depo",
        target_wire=wire,
        thickness=0.2,
        shell_verts=[1, 2],
    )
    block3 = part_3d.Part3DData("Passthrough", "Box")
    substrate = part_3d.ExtrudeData("Substrate", "Sketch005", z0=-2, thickness=2)
    wrap = part_3d.LithographyData(
        "First Layer",
        "Sketch006",
        z0=0,
        layer_num=1,
        thickness=4,
        litho_base=[substrate],
    )
    wrap2 = part_3d.LithographyData(
        "Second Layer", "Sketch007", layer_num=2, thickness=1
    )
    input_file_path = os.path.join(datadir, "geometry_test.fcstd")
    print(input_file_path)

    build_order = [block1, block2, sag, wire, shell, block3, substrate, wrap, wrap2]
    results = []
    for d1 in np.linspace(2.0, 7.0, 3):
        built_geo = build_3d_geometry(
            input_parts=build_order, input_file=input_file_path, params={"d1": d1}
        )
        results += [built_geo]

    # Investigate results
    with tempfile.TemporaryDirectory() as temp_dir_path:
        for i, result in enumerate(results):
            file_name = os.path.join(temp_dir_path, f"{i}.fcstd")
            result.write_fcstd(file_name)
            # TODO: should find a meaningful test here
