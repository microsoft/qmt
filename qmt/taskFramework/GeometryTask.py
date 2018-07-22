from dask import delayed
from Task import Task
from SweepHolder import SweepHolder

class GeometryTask(Task):

    def __init__(self,part_dict={},name='geometry_task'):
        super(self.__class__, self).__init__(**Task.remove_self_argument(locals()))
    
    def _solve_instance(self,current_part_dict):
        return current_part_dict

    def _populate_result(self):
        if self.sweep_manager is None:
            self.result = delayed(self._solve_instance)(self.part_dict)
        else:
            sweep_holder = SweepHolder(self.sweep_manager,self.list_of_tags)
            for sweep_holder_index,tag_values in enumerate(sweep_holder.tagged_value_list):
                current_part_dict = self._make_current_part_dict(tag_values)
                output = delayed(self._solve_instance)(current_part_dict)
                sweep_holder.add(output,sweep_holder_index)
            self.result = sweep_holder


