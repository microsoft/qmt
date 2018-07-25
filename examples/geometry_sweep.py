#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Example geometry sweeping."""

import os
import numpy as np

import qmt.task_framework as qtf
from qmt.basic_tasks import GeoFreeCAD

# Set up geometry task
tag = qtf.SweepTag('thickness')
freecad_dict = {'filepath': 'geometry_sweep.fcstd', 'params': {'d1': tag}}
geo_task = GeoFreeCAD(options=freecad_dict)

# Run sweeps
sweeps = [{tag: 8}, {tag: 2}, {tag: 5}]
sman = qtf.SweepManager(sweeps)
sman.run(geo_task)

# Investigate results
if not os.path.exists('tmp'):
    os.mkdir('tmp')
for res in geo_task.result:
    # ~ print(res.modelParams.d1)
    res.saveAs("tmp/example_geogen_" + str(res.modelParams.d1) + ".fcstd")
