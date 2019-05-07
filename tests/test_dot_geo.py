# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

"""Testing a simplified version of the 'quantum_dot_device' example."""


import numpy as np
import os
import tempfile
from qmt.geometry import part_3d, build_3d_geometry


def test_dot_geo(datadir):
    """
    Tests building a simplified version of the example 'quantum_dot_device.'
    The syntax of this example should match the corresponding example.
    ANY CHANGES MADE TO THIS TEST SHOULD ALSO BE MADE IN CORRESPONDING EXAMPLE.
    """

    substrate = part_3d.ExtrudePart("Substrate", "Sketch027", z0=-2, thickness=2.0)

    gate1 = part_3d.ExtrudePart("Gate 1", "Sketch003", z0=0, thickness=10)

    wrap1 = part_3d.LithographyPart(
        "Wrap 1",
        "Sketch028",
        z0=0,
        thickness=2,
        layer_num=1,
        litho_base=[substrate, gate1],
    )

    layer2 = part_3d.LithographyPart(
        "Layer 2", "Sketch002", z0=0, thickness=10, layer_num=2
    )

    wrap2 = part_3d.LithographyPart(
        "Wrap 2", "Sketch029", z0=0, thickness=2, layer_num=3
    )

    layer3 = part_3d.ExtrudePart("Layer 3", "Sketch023", z0=0, thickness=30)

    # Parameters for geometry building
    input_file = os.path.join(datadir, "qd_device_parts.fcstd")
    input_parts = [substrate, gate1, wrap1, layer2, wrap2, layer3]

    # Compute parametrised geometries in parallel with dask
    geo = build_3d_geometry(input_parts=input_parts, input_file=input_file)

    # Create a local temporary directory to investigate results
    with tempfile.TemporaryDirectory() as temp_dir_path:
        geo.write_fcstd(os.path.join(temp_dir_path, "tmp.fcstd"))
        for label, part in geo.parts.items():
            part.write_stl(os.path.join(temp_dir_path, label + ".stl"))
