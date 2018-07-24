# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

from qmt.basic_tasks import geo

class _Mesh(Task):

    def __init__(self, geo_task, options=None, name='poisson_task'):
        super(PoissonTask, self).__init__([geo_task], options, name)
        assert isinstance(geo_task, GeometryTask)

    def _solve_instance(self, input_result_list, current_options):
        materials_result_instance = input_result_list[0]
        geo_result_instance = input_result_list[1]
        output = ''
        for part in geo_result_instance.keys():
            output += ' part: ' + part
            output += ', side length: ' + str(geo_result_instance[part]['side length'])
            output += ', material: ' + materials_result_instance[part]['material']
            output += ', voltage: ' + str(current_options[part]['voltage'])
        return output