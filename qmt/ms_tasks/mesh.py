# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

from qmt.task_framework import Task
from qmt.basic_tasks import Geometry1D, Geometry2D, Geometry3D


class Mesh(Task):
    def __init__(self, geo_task, options=None, name='mesh_task'):
        """
        Constructs a Mesh Task

        :param geo_task: Dependent GeoTask
        :param options: Dict containing information on the meshing of the object. This should be of the form...
        :param name: Name of the task
        """
        super(Mesh, self).__init__([geo_task], options, name)

    def _solve_instance(self, input_result_list, current_options):
        geo_result_instance = input_result_list[0]
        return geo_result_instance


class MeshTask1D(Mesh):
    def __init__(self, geo_task, options=None, name='mesh_3D_task'):
        super(MeshTask1D, self).__init__([geo_task], options, name)
        assert type(geo_task) is Geometry1D


class MeshTask2D(Mesh):
    def __init__(self, geo_task, options=None, name='mesh_3D_task'):
        super(MeshTask2D, self).__init__([geo_task], options, name)
        assert type(geo_task) is Geometry2D


class MeshTask3D(Mesh):
    def __init__(self, geo_task, options=None, name='mesh_3D_task'):
        super(MeshTask3D, self).__init__([geo_task], options, name)
        assert type(geo_task) is Geometry3D
