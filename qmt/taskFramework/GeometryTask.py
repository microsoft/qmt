from Task import Task

class GeometryTask(Task):

    def __init__(self,part_dict=None,name='geometry_task'):
        super(self.__class__, self).__init__(**Task.remove_self_argument(locals()))
        self.input_task_list = [] # no input tasks here

    def _solve_instance(self,input_result_list,current_part_dict):
        return current_part_dict



