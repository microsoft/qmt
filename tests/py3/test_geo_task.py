# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

"""Testing the geometry task."""


def test_geo_task(fix_py2env, fix_testDir):
    """
    Tests the build geometry task. For now, just verifies that the build doesn't encounter errors.
    """
    from qmt.tasks import build_3d_geometry
    from qmt.data import Part3DData
    import numpy as np
    import os
    import shutil

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
    print(os.path.join(fix_testDir, 'py3', 'data', 'geometry_test.fcstd'))
    input_file_path = os.path.join(fix_testDir, 'py3', 'data', 'geometry_test.fcstd')

    build_order = [block1, block2, sag, wire, shell, block3, substrate, wrap, wrap2]
    results = []
    for d1 in np.linspace(2., 7., 3):
        built_geo = build_3d_geometry(fix_py2env, input_file_path, build_order, {'d1': d1})
        results += [built_geo]

    # Investigate results
    if not os.path.exists('tmp'):
        os.makedirs('tmp')

    for i, result in enumerate(results):
        file_name = 'tmp/' + str(i) + '.fcstd'
        result.write_fcstd(file_name)
        # TODO: should find a meaningful test here

    shutil.rmtree('tmp')
