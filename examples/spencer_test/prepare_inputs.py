from __future__ import division

import numpy as np

from qmt.data import Part3DData
from qmt.tasks import Geometry3D
from qms.tasks import Mesh3D, Poisson3D, RegionMapFunction, ThomasFermi3D, ThomasFermi3DFake
import math

from qms.fem.fenics_expressions import make_permittivity_expression

volume_source = {"volume": {"sphere": 1 / ((4/3) * math.pi * 3**3)}}


simdomain = Part3DData('simdomain', 'Box', '3d_shape', 'dielectric',
                material='InSb', mesh_max_size=5)

sphere = Part3DData('sphere', 'Sphere', '3d_shape', 'dielectric',
                material='InSb', mesh_max_size=1)

cube = Part3DData('cube', 'Box001', '3d_shape', 'dielectric',
                material='InSb', mesh_max_size=1, boundary_condition = {"voltage": 100.0})


# Specify options for the different tasks
freecad_dict = {
    'pyenv': '/home/t-sppete/miniconda2/envs/qmsFresh/bin/python', # TODO
    'file_path': '/home/t-sppete/notebooks/Tasks/quote_unquote_realistic_setup.FCStd',
    'params': {},
    'input_parts': [simdomain, sphere, cube]
}
mesh_dict = {
    'scratch_dir':'tmp',
    'comsol_path':'/gscratch/opt/comsol53a/multiphysics/bin/comsol',
    'num_cores' : 4
}
rmf_dict = {'pyenv': '/home/t-sppete/miniconda2/envs/qmsFresh/bin/python'}

poisson_dict = {
    "exterior_boundary_condition": {"neumann": 0.0},
    'elements': { 'type': 'P', 'degree': 1},
    "source_charge_info": volume_source
}

geo_task = Geometry3D(options=freecad_dict)
mesh_task = Mesh3D(geo_task,mesh_dict)
rmf_task = RegionMapFunction(mesh_task,rmf_dict)

poisson_task = ThomasFermi3D(rmf_task, poisson_dict)

poisson_task.run_daskless()

si = poisson_task.inputs

expr = make_permittivity_expression(si)