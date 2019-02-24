#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time

import qmt.tasks as qtf
from qmt.tasks import Task


class GeometryTaskExample(Task):

    def __init__(self, options=None, name='geometry_task'):
        super(GeometryTaskExample, self).__init__([], options, name)
        self.input_task_list = []  # no input tasks here

    def _solve_instance(self, input_result_list, current_options):
        time.sleep(1.)
        return current_options


class PoissonTaskExample(Task):

    def __init__(self, geo_task, options=None, name='poisson_task'):
        super(PoissonTaskExample, self).__init__([geo_task], options, name)
        assert isinstance(geo_task, GeometryTaskExample)
        self.input_task_list = [geo_task]

    def _solve_instance(self, input_result_list, current_options):
        geo_result_instance = input_result_list[0]
        time.sleep(2)
        output = ''
        for part in geo_result_instance.keys():
            output += ' part: ' + part
            output += ', side length: ' + \
                str(geo_result_instance[part]['side length'])
            output += ', voltage: ' + str(current_options[part]['voltage'])
        return output


tag1 = qtf.SweepTag('s1')
tag2 = qtf.SweepTag('v1')

geo_dict = {'part1': {'side length': tag1}, 'part2': {'side length': 3.}}
geo_task = GeometryTaskExample(options=geo_dict)

mat_dict = {'part1': {'material': 'InAs'}, 'part2': {'material': 'InP'}}

poisson_dict = {'part1': {'voltage': tag2}, 'part2': {'voltage': 1.}}
poisson_task = PoissonTaskExample(geo_task, options=poisson_dict)

sweeps = [{tag1: 1., tag2: 10.}, {tag1: 2., tag2: 10.},
          {tag1: 1., tag2: 5.}, {tag1: 4., tag2: 3.}]

sweep_man = qtf.SweepManager(sweeps)

result = sweep_man.run(poisson_task)
# print(poisson_task.reduce())

# print(geo_task.reduce())

print(result.result())

# print(map(dask.result,result.futures))
