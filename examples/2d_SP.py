#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
import qmt.task_framework as qtf
from shapely.geometry import Polygon
import qmt.basic_tasks as qbt
import qmt.ms_tasks as qmm

wireLength = qtf.SweepTag('wire length')
#tag2 = qtf.SweepTag('v1')   

#wireLength = 50.

geo_dict = {'parts' : {}, 'edges' : {}}
geo_dict['parts']['wire'] = [(-wireLength/2., 0.), (0., wireLength/np.sqrt(2.)), (wireLength/2.,0.)]
geo_task = qbt.Geometry2D(options=geo_dict)

mesh_dict = {'mesh_type' : 'difference'}

mesh_task = qmm.Mesh2D(geo_task, options = mesh_dict)

sweeps = [{wireLength : l} for l in np.linspace(50.,150.,3)]

sweep_man = qtf.SweepManager(sweeps)

result = sweep_man.run(mesh_task)
print(mesh_task.reduce())

