from qmt.task_framework import Task
from qmt.basic_tasks import Geometry1D


class PoissonTask(Task):

    def __init__(self, geo_task, options=None, name='poisson_task'):
        super(PoissonTask, self).__init__([geo_task], options, name)
        assert isinstance(geo_task, Geometry1D)

    def _solve_instance(self, input_result_list, current_options):
        geo_result_instance = input_result_list[0]
        output = ''
        for part in geo_result_instance.keys():
            output += ' part: ' + part
            output += ', side length: ' + str(geo_result_instance[part]['side length'])
            output += ', voltage: ' + str(current_options[part]['voltage'])
        return output
