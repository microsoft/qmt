#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
import qmt.task_framework as qtf
import qmt.basic_tasks as qbt
import qms.tasks as qmst

wireLength = qtf.SweepTag('wire length')
gateVoltage = qtf.SweepTag('gate voltage')

geo_dict = {'parts' : {}, 'edges' : {}}
geo_dict['parts']['wire'] = [[-wireLength/2., 0.], [0., wireLength/np.sqrt(2.)], [wireLength/2.,0.]]
geo_dict['edges']['gate'] = [[-wireLength/2., 0.], [0., wireLength/np.sqrt(2.)], [wireLength/2.,0.]]
geo_task = qbt.Geometry2D(options=geo_dict)

mesh_dict = {'mesh_type' : 'finite difference','grid' : {'x' : {'step_size' : 0.1}, 'y' : {'step_size' : 0.1}}}

mesh_task = qmst.Mesh2D(geo_task, options = mesh_dict)

poisson_dict = {}
poisson_dict['materials'] = {'wire' : 'InAs'}
poisson_dict['voltages'] = {'gate' : gateVoltage}

poisson_task = qmst.PoissonTask2D(geo_task, mesh_task, poisson_dict)

sweeps = [{wireLength : l, gateVoltage : v} for l in np.linspace(50.,150.,3) for v in np.linspace(0.,1.,3)]

sweep_man = qtf.SweepManager(sweeps)

result = sweep_man.run(poisson_task)
print(poisson_task.reduce())

