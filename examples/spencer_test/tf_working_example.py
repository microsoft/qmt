from __future__ import division
from fenics import set_log_level, DEBUG, WARNING, File

set_log_level(DEBUG)

import numpy as np

from qmt.data import Part3DData
from qmt.tasks import Geometry3D
from qms.tasks import Mesh3D, Poisson3D, RegionMapFunction, RegionMapFunctionStub, ThomasFermi3D
import math

cd = 1 / ((4 / 3) * math.pi * 3 ** 3)
volume_source = {"volume": {"sphere": cd}}

# simdomain = Part3DData('simdomain', 'Box', '3d_shape', 'dielectric',
#                 material='InSb', mesh_max_size=5)

# sphere = Part3DData('sphere', 'Sphere', '3d_shape', 'dielectric',
#                 material='InSb', mesh_max_size=1)

# cube = Part3DData('cube', 'Box001', '3d_shape', 'dielectric',
#                 material='air', mesh_max_size=1, boundary_condition = {"voltage": 100.0})


# Specify options for the different tasks
# freecad_dict = {
#     'pyenv': '/home/t-sppete/miniconda2/envs/qmsFresh/bin/python', # TODO
#     'file_path': '/home/t-sppete/notebooks/Tasks/quote_unquote_realistic_setup.FCStd',
#     'params': {},
#     'input_parts': [simdomain, sphere, cube]
# }
# mesh_dict = {
#     'scratch_dir':'tmp',
#     'comsol_path':'/gscratch/opt/comsol53a/multiphysics/bin/comsol',
#     'num_cores' : 4
# }
# rmf_dict = {'pyenv': '/home/t-sppete/miniconda2/envs/qmsFresh/bin/python'}

rmf_dict = {"geo_filepath": "gd_tf_task.pkl"}

tf_dict = {
    "exterior_boundary_condition": {"neumann": 0.0},
    'elements': {'type': 'P', 'degree': 1},
    "source_charge_info": volume_source
}

# geo_task = Geometry3D(options=freecad_dict)
# mesh_task = Mesh3D(geo_task,mesh_dict)
rmf_task = RegionMapFunctionStub(rmf_dict)

tf_task = ThomasFermi3D(rmf_task, tf_dict)

tf_task.run_daskless()

si = tf_task.inputs

# import pickle
# with open("gd_tf_task.pkl", 'wb') as dumpfile:
#     pickle.dump(si.geo_3d_data, dumpfile)


phi = tf_task.daskless_result.evaluate_point_function

File("realistic_potential_by_hand.pvd") << phi

np.max(phi.vector().array())

np.min(phi.vector().array())

tf_task.check_consistency(phi)

