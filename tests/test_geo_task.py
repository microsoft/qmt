# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

"""Testing the geometry task."""
import FreeCAD

def test_geo_task(datadir):
    """
    Tests the build geometry task. For now, just verifies that the build doesn't encounter errors.
    """
    from qmt.tasks import build_3d_geometry
    from qmt.data import Part3DData
    import numpy as np
    import os
    import tempfile

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
                      z0=0, layer_num=1, thickness=4, litho_base=[substrate])
    wrap2 = Part3DData('Second Layer', 'Sketch007', 'lithography', 'dielectric',
                       layer_num=2, thickness=1)
    input_file_path = os.path.join(datadir, 'geometry_test.fcstd')
    print(input_file_path)

    build_order = [block1, block2, sag, wire, shell, block3, substrate, wrap, wrap2]
    results = []
    for d1 in np.linspace(2., 7., 3):
        built_geo = build_3d_geometry(input_parts=build_order,input_file=input_file_path,
                                      params={'d1': d1})
        # Currently build_3d_geometry is stateful. Cleaing up
        FreeCAD.closeDocument('instance')
        results += [built_geo]
    

    # Investigate results
    with tempfile.TemporaryDirectory() as temp_dir_path:
        for i,result in enumerate(results):
            file_name = os.path.join(temp_dir_path, str(i) + '.fcstd')
            result.write_fcstd(file_name)
            # TODO: should find a meaningful test here
