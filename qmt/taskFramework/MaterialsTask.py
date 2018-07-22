from dask import delayed
from Task import Task
from GeometryTask import GeometryTask
from SweepHolder import SweepHolder
from SweepTag import replace_tag_with_value

class MaterialsTask(Task):

    def __init__(self,geo_task,part_dict={},name='materials_task',inheret_tags_from = None):
        super(self.__class__, self).__init__(**Task.remove_self_argument(locals()))
        assert isinstance(geo_task,GeometryTask)
        self.geo_task = geo_task

    def _check_part_names(self,completed=True):
        #TODO: write this function
        #checks to see if the parts in my part_dict
        #are the same as in geo_task's part_dict
        return True
    
    def _solve_instance(self,tag_values):
        current_part_dict = self.part_dict
        for i,tag in enumerate(self.list_of_tags):
            current_part_dict = replace_tag_with_value(current_part_dict,tag,tag_values[tag])
        return current_part_dict

    #TODO: need to run _check_part_names!
    def _populate_result(self,completed=True):
        if self.sweep_manager is None:
            self.result = delayed(self._solve_instance)(None)
        else:
            sweep_holder = SweepHolder(self.sweep_manager,self.list_of_tags)
            for sweep_holder_index,tag_values in enumerate(sweep_holder.tagged_value_list):
                current_part_dict = delayed(self._solve_instance)(tag_values)
                sweep_holder.add(current_part_dict,sweep_holder_index)
            self.result = sweep_holder
        return True
        
