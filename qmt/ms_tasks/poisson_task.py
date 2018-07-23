from qmt.task_framework import Task
from qmt.basic_tasks import GeometryTask, MaterialsTask


class PoissonTask(Task):

    def __init__(self, geo_task, mat_task, options=None, name='poisson_task'):
        super(self.__class__, self).__init__(**Task.remove_self_argument(locals()))
        assert isinstance(mat_task, MaterialsTask)
        assert isinstance(geo_task, GeometryTask)
        self.input_task_list = [mat_task, geo_task]

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
