from dask import delayed
from Task import Task
from SweepHolder import SweepHolder
from SweepTag import gen_tag_extract,replace_tag_with_value

class GeometryTask(Task):

    def __init__(self,part_dict={},name='geometry_task'):
        super(self.__class__, self).__init__(**Task.remove_self_argument(locals()))
    
    def _solve_instance(self,tag_values):
        current_part_dict = self.part_dict
        for i,tag in enumerate(self.list_of_tags):
            current_part_dict = replace_tag_with_value(current_part_dict,tag,tag_values[tag])
        return current_part_dict


    def _populate_result(self):
        if self.sweep_manager is None:
            self.result = self.part_dict
        else:
            sweep_holder = SweepHolder(self.sweep_manager,self.list_of_tags)
            for sweep_holder_index,tag_values in enumerate(sweep_holder.tagged_value_list):
                current_part_dict = delayed(self._solve_instance)(tag_values)
                sweep_holder.add(current_part_dict,sweep_holder_index)
            self.result = sweep_holder


