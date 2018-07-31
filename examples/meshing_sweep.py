#!/usr/bin/env python
# -*- coding: utf-8 -*-

import qmt.task_framework as qtf
from qmt.task_framework import Task
import time

class GeometryTaskExample(Task):

    def __init__(self,options=None,name='geometry_task'):
        super(GeometryTaskExample, self).__init__([], options, name)
        self.input_task_list = [] # no input tasks here

    def _solve_instance(self,input_result_list,current_options):
        print('running geom')
        return current_options

class MeshingTaskExample(Task):
    
    def __init__(self, geo_task, options=None, name='meshing_task', gather=True):
        super(MeshingTaskExample, self).__init__([geo_task], options, name, gather=gather)
        self.input_task_lit = [geo_task]

    def _solve_gathered(self, list_of_input_result_lists, list_of_options):
        print(list_of_input_result_lists)
        reduced_sweep = qtf.ReducedSweep.create_from_manager_and_tags(self.sweep_manager, self.list_of_tags)
        new_delayed_result = qtf.ReducedSweepDelayed.create_from_reduced_sweep_and_manager(reduced_sweep,
                                                                                       self.sweep_manager)
        for sweep_holder_index, tag_values in enumerate(new_delayed_result.tagged_value_list):
            current_options = list_of_options[sweep_holder_index]
            input_result_lists = list_of_input_result_lists[sweep_holder_index]
            output = current_options.copy()
            for key in current_options.keys():
                output[key].update(input_result_lists[0][key])
            print(output)
            new_delayed_result.add(output, sweep_holder_index)
        return new_delayed_result

class PoissonTaskExample(Task):

    def __init__(self, mesh_task, options=None, name='poisson_task'):
        super(PoissonTaskExample, self).__init__([mesh_task], options, name)
        self.input_task_list = [mesh_task]

    def _solve_instance(self, input_result_list, current_options):
        mesh_result_instance = input_result_list[0]
        print(mesh_result_instance)
        time.sleep(2)
        output = ''
        for part in mesh_result_instance.keys():
            output += ' part: ' + part
            output += ', min size: ' + str(mesh_result_instance[part]['min_size'])
            output += ', voltage: ' + str(current_options[part]['voltage'])
        return output

tag1 = qtf.SweepTag('s1')
tag2 = qtf.SweepTag('m1')
tag3 = qtf.SweepTag('v1')   

geo_dict = {'part1': {'side length': tag1}, 'part2': {'side length': 3.}}
geo_task = GeometryTaskExample(options=geo_dict)

mesh_dict = {'part1': {'min_size':1.}, 'part2': {'min_size':tag2}}
mesh_task = MeshingTaskExample(geo_task, options=mesh_dict)

poisson_dict = {'part1':{'voltage':tag3},'part2':{'voltage': 1.}}
poisson_task = PoissonTaskExample(mesh_task, options=poisson_dict)

sweeps = [{tag1: 1., tag2: 10., tag3 : 1.}, {tag1: 2., tag2: 10., tag3 : 1.}, {tag1: 1., tag2: 5., tag3 : 1.}, {tag1: 4., tag2: 3., tag3 : 2.}]

sweep_man = qtf.SweepManager(sweeps)
#result = sweep_man.run(mesh_task)

#print(mesh_task.reduce())
result = sweep_man.run(poisson_task)
print(poisson_task.reduce())

#print(geo_task.reduce())

#print(map(dask.result,result.futures))
