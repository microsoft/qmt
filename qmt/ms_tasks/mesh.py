# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

from qmt.task_framework import Task


class Mesh(Task):
    def __init__(self, geo_task, options=None, name='mesh_task'):
        """
        Constructs a Mesh Task

        :param geo_task: Dependent GeoTask
        :param options: Dict containing information on the meshing of the object. This should be of the form...
        :param name: Name of the task
        """
        super(Mesh, self).__init__([geo_task], options, name)


class Mesh1D(Mesh):
    def __init__(self, geo_task, options=None, name='mesh_1D_task'):
        """
        Constructs a 1D Mesh from a 1D geometry.
        :param Geometry1D geo_task: The 1D geometry task that feeds this mesh task.
        :param options: Dict containing information on the meshing of the object. This should be of the form...
        :param name: Name of the task
        """
        super(Mesh, self).__init__([geo_task], options, name)

    def _solve_instance(self, input_result_list, current_options):
        """
        :param list input_result_list: Single element list with a Geo1DData element.
        :param dict current_options: Dict from above.
        :return Mesh1DData mesh_1d: Output mesh
        """
        geo_result_instance = input_result_list[0]
        return geo_result_instance


class Mesh2D(Mesh):
    def __init__(self, geo_task, options=None, name='mesh_2D_task'):
        """
        Constructs a 2D Mesh from a 2D geometry.
        :param Geometry2D geo_task: The 2D geometry task that feeds this mesh task.
        :param options: Dict containing information on the meshing of the object. This should be of the form...
        :param name: Name of the task
        """
        super(Mesh, self).__init__([geo_task], options, name)
        # assert type(geo_task) is Geometry2D
    def _solve_instance(self, input_result_list, current_options):
        """
        :param list input_result_list: Singleton list with a Geo1DData element.
        :param dict current_options: Dict from above.
        :return Mesh2DData mesh_2d: Output mesh
        """
        from qms.meshing import Mesh2dData
        geo_result_instance = input_result_list[0]
        mesh_2d = Mesh2dData(geo_result_instance.parts)
        if current_options['mesh_type'] == 'difference':
            mesh_2d.construct_difference()
        elif current_options['mesh_type'] == 'element':
            mesh_2d.construct_element()
        else:
            raise ValueError('Unrecognized meshing type: '+str(current_options['mesh_type']))
        return mesh_2d


class Mesh3D(Mesh):
    def __init__(self, geo_task, options=None, name='mesh_3D_task'):
        """
        Constructs a 3D Mesh from a 3D geometry.
        :param Geometry3D geo_task: The 3D geometry task that feeds this mesh task.
        :param options: Dict containing information on the meshing of the object. This should be of the form...
        :param name: Name of the task
        """
        super(Mesh, self).__init__([geo_task], options, name)
        # assert type(geo_task) is Geometry3D
    def _solve_instance(self, input_result_list, current_options):
        """
        :param list input_result_list: Singleton list with a Geo1DData element.
        :param dict current_options: Dict from above.
        :return Mesh3DData mesh_1d: Output mesh
        """
        geo_result_instance = input_result_list[0]
        return geo_result_instance
