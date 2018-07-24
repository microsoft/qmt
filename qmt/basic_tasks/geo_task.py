from qmt.task_framework import Task

class GeometryTask(Task):

    def __init__(self,options=None,name='geometry_task'):
        super(GeometryTask, self).__init__([], options, name)

    def _solve_instance(self,input_result_list,current_options):
        return current_options


class FreeCADTask(GeometryTask):

    def __init__(self, filepath, options=None, name='geometry_task'):
        super(GeometryTask, self).__init__(**Task.remove_self_argument(locals()))
        self.input_task_list = []  # no input tasks here

    def _solve_instance(self, input_result_list, current_options):
        return current_options
