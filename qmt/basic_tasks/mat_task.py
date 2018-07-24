from qmt.task_framework import Task
from geo_task import GeometryTask

class MaterialsTask(Task):

    def __init__(self,options=None,name='materials_task'):
        super(self.__class__, self).__init__([], options, name)

    def _check_part_names(self):
        #TODO: write this function
        #checks to see if the parts in my options
        #are the same as in geo_task's options
        return True
    
    def _solve_instance(self,input_result_list,current_options):
        return current_options

