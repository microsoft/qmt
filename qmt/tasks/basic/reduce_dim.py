# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

from qmt.tasks import Task


class ReduceDim3D(Task):
    def __init__(self, geo_3d, options=None, name='reduce_dim_3d_task'):
        """
        Reduces a 3D geometry to a 2D geometry for use with 2D solvers.
        :param Geometry3D geo_3d: The input 3D geometry task
        :param dict options: Dictionary of the form {"axis":tup,"position":pos,"parts":[part1,part2,...]}, where axis
        is a 3-tuple defining the slice axis, position is the coordinate on the axis to take the cross-section, and
        parts is an optional list of parts. If it is included, only the part names listed will be included.
        :param str name: The name of this task.
        """
        super(ReduceDim3D, self).__init__([geo_3d], options, name)
        # assert type(geo_3d) is Geometry3D
        # for spec in options: assert (spec == "axis") or (spec == "position") or (spec == "parts")
        # assert type(options["axis"]) is tuple
        # assert len(options["axis"]) == 3
        # assert type(options["position"]) is float
        # if "parts" in options:
        #     for part in options["parts"]: assert type(part) is str

    def _solve_instance(input_result_list, current_options):
        """
        :param list input_result_list: This is a singleton list of a geo_3d object.
        :param dict current_options: The dictionary specifying parts from above.
        :return geo_2d: A Geo2DData object
        """
        geo_2d = current_options
        return geo_2d


class ReduceDim2D(Task):
    def __init__(self, geo_2d, options=None, name='reduce_dim_2d_task'):
        """
        Reduces a 2D geometry to a 1D geometry for use with 1D solvers.
        :param Geometry2D geo_2d: The input 2D geometry task
        :param dict options: Dictionary of the form {"axis":tup,"position":pos,"parts":[part1,part2,...]}, where axis
        is a 2-tuple defining the slice axis, position is the coordinate on the axis to take the cut, and
        parts is an optional list of parts. If it is included, only the part names listed will be included.
        :param str name: The name of this task.
        """
        super(ReduceDim2D, self).__init__([geo_2d], options, name)
        # assert type(geo_2d) is Geometry2D
        # for spec in options: assert (spec == "axis") or (spec == "position") or (spec == "parts")
        # assert type(options["axis"]) is tuple
        # assert len(options["axis"]) == 2
        # assert type(options["position"]) is float
        # if "parts" in options:
        #     for part in options["parts"]: assert type(part) is str

    def _solve_instance(input_result_list, current_options):
        """
        :param list input_result_list: This is a one-element list of a Geometry2D result.
        :param dict current_options: The dictionary specifying parts from above.
        :return geo_1d: A Geo1DData object
        """

        geo_1d = current_options
        return geo_1d
