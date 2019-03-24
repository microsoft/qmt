#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
import qmt.task_framework as qtf
from qmt.ms_tasks import Density1D
from qmt.task_framework import Task

from qmt import units
from qmt.visualization import generate_1d_density_plot


class GeometryTaskExample(Task):
    def __init__(self, options=None, name="geometry_task"):
        super(GeometryTaskExample, self).__init__([], options, name)
        self.input_task_list = []  # no input tasks here

    def _solve_instance(self, input_result_list, current_options):
        print("running geom")
        return current_options


class PoissonTaskExample(Task):
    def __init__(self, geo_task, options=None, name="poisson_task"):
        super(PoissonTaskExample, self).__init__([geo_task], options, name)
        assert isinstance(geo_task, GeometryTaskExample)
        self.input_task_list = [geo_task]

    def _solve_instance(self, input_result_list, current_options):
        geo_result_instance = input_result_list[0]
        xs = np.arange(0.0, geo_result_instance["part1"]["side length"], 0.01)
        densities = [np.array([current_options["part1"]["voltage"]] * len(xs))] * 3
        bands = [np.array([current_options["part1"]["voltage"]] * len(xs))] * 3
        output = Density1D(densities, units.meV, bands, units.meV, xs, units.nm)
        return output


tag1 = qtf.SweepTag("s1")
tag2 = qtf.SweepTag("v1")

geo_dict = {"part1": {"side length": tag1}}
geo_task = GeometryTaskExample(options=geo_dict)

poisson_dict = {"part1": {"voltage": tag2}}
poisson_task = PoissonTaskExample(geo_task, options=poisson_dict)

sweeps = [
    {tag1: 1.0, tag2: 10.0},
    {tag1: 2.0, tag2: 10.0},
    {tag1: 1.0, tag2: 5.0},
    {tag1: 4.0, tag2: 3.0},
]

sweep_man = qtf.SweepManager(sweeps)

result = sweep_man.run(poisson_task)

generate_1d_density_plot(poisson_task, "density_test.h5")

# print(map(dask.result,result.futures))
