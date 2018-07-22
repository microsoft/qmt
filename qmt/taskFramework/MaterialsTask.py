from Task import Task
from GeometryTask import GeometryTask

class MaterialsTask(Task):

    def __init__(self,geo_task,options=None,name='materials_task',inheret_tags_from = None):
        super(self.__class__, self).__init__(**Task.remove_self_argument(locals()))
        assert isinstance(geo_task,GeometryTask)
        self.input_task_list = [geo_task]

    def _check_part_names(self):
        #TODO: write this function
        #checks to see if the parts in my options
        #are the same as in geo_task's options
        return True
    
    def _solve_instance(self,input_result_list,current_options):
        return current_options
        
