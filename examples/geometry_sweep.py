#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Example geometry sweeping."""


import numpy as np

import qmt.task_framework as qtf
from qmt.basic_tasks.geometry import GeometryParams


# Set up geometry task
tag = qtf.SweepTag('thickness')
freecad_dict = {'filepath': 'geometry_sweep.fcstd', 'params': {'d1': tag}}
geo_task = GeometryParams(options=freecad_dict)

# Run sweeps
sweeps = [{tag: val} for val in np.arange(2, 10, 2)]
result = qtf.SweepManager(sweeps).run(geo_task)

# Investigate results
for future in result.futures:
    print(future.result())
for result in geo_task.reduce()[1]:
    print(result)
