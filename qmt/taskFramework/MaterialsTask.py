from dask import delayed
from Task import Task
from GeometryTask import GeometryTask
from SweepHolder import SweepHolder

class MaterialsTask(Task):

    def __init__(self,geo_task,part_dict={},name='materials_task',inheret_tags_from = None):
        super(self.__class__, self).__init__(**Task.remove_self_argument(locals()))
        assert isinstance(geo_task,GeometryTask)
        self.geo_task = geo_task

    def _check_part_names(self):
        #TODO: write this function
        #checks to see if the parts in my part_dict
        #are the same as in geo_task's part_dict
        return True
    
    def _solve_instance(self,current_part_dict):
        return current_part_dict

    def _populate_result(self,completed=True):
        self._check_part_names()
        if self.sweep_manager is None:
            self.result = delayed(self._solve_instance)(self.part_dict)
        else:
            sweep_holder = SweepHolder(self.sweep_manager,self.list_of_tags)
            for sweep_holder_index,tag_values in enumerate(sweep_holder.tagged_value_list):
                current_part_dict = self._make_current_part_dict(tag_values)
                output = delayed(self._solve_instance)(current_part_dict)
                sweep_holder.add(output,sweep_holder_index)
            self.result = sweep_holder
        
