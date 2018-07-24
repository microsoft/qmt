# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

from qmt.task_framework import Task
from qmt.geometry import Part2D, Part3D


class Geometry1D(Task):
    def __init__(self, options=None, name='geometry_1d_task'):
        """
        Builds a geometry in 1D.
        :param options: The dictionary specifying parts, of the form {"part_name":(start_coord,stop_coord)}
        :param name: The name of this task.
        """
        super(Geometry1D, self).__init__([], options, name)

    def _solve_instance(self, input_result_list, current_options):
        """
        Renders a geometry in 1D.
        :param input_result_list: This is an empty list.
        :param current_options: The dictionary specifying parts from above.
        :return:
        """
        return current_options


class Geometry2D(Task):
    def __init__(self, options=None, name='geometry_2d_task'):
        """
        Builds a geometry in 2D.
        :param options: The dictionary specifying parts, of the form {"part_name":Part3D}
        :param name: The name of this task.
        """
        super(Geometry2D, self).__init__([], options, name)
        for part_name in options:
            assert type(options[part_name]) is Part2D

    def _solve_instance(self, input_result_list, current_options):
        """
        Renders a geometry in 1D.
        :param input_result_list: This is an empty list.
        :param current_options: The dictionary specifying parts from above.
        :return:
        """
        return current_options


class Geometry3D(Task):
    def __init__(self, options=None, name='geometry_3d_task'):
        """
        Builds a geometry in 3D.
        :param options: The dictionary specifying parts and and FreeCAD infromation. It should be of the form
        {"fcname":path_to_freeCAD_file,"parts_dict":parts_dict}, where parts_dict is a dictionary of the form
        {part_name:Part3D}.
        :param name: The name of this task.
        """
        super(Geometry3D, self).__init__([], options, name)
        assert type(options["fcname"]) is str
        assert type(options["parts_dict"]) is dict
        for partDirective in options["part_dict"]:
            assert type(options["part_dict"][partDirective]) is Part3D

    def _solve_instance(self, input_result_list, current_options):
        """
        Renders a geometry in 1D.
        :param input_result_list: This is an empty list.
        :param current_options: The dictionary specifying parts from above.
        :return:
        """
        return current_options
