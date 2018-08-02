#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
import qmt.task_framework as qtf
from shapely.geometry import Polygon
import qmt.basic_tasks as qbt

#tag1 = qtf.SweepTag('s1')
#tag2 = qtf.SweepTag('v1')   

wireLength = 50.

geo_dict = {'parts' : {}, 'edges' : {}}
geo_dict['parts']['wire'] = Polygon([(-wireLength/2., 0.), (0., wireLength/np.sqrt(2.)), (wireLength/2.,0.)])
geo_task = qbt.Geometry2D(options=geo_dict)

sweeps = [{}]

sweep_man = qtf.SweepManager(sweeps)

result = sweep_man.run(geo_task)
print(geo_task.reduce())

