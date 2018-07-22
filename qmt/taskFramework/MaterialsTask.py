from dask import delayed
from Task import Task
from SweepTag import gen_tag_extract,replace_tag_with_value

class MaterialsTask(Task):

    def __init__(self,geo_task,part_dict={},name='materials_task'):
        super(self.__class__, self).__init__(**Task.remove_self_argument(locals()))
        #geo_task is type GeometryTask
        self.geo_task = geo_task
        self.part_dict = part_dict

    def _check_part_names(self,completed=True):
        #TODO: write this function
        #checks to see if the parts in my part_dict
        #are the same as in geo_task's part_dict
        return True
    
    def _make_current_part_dict(self,tag_values):
        current_part_dict = self.part_dict
        for i,tag in enumerate(list_of_tags):
            current_part_dict = replace_tag_with_value(current_part_dict,tag,tag_values[tag])
        return current_part_dict


    def _generate_output(self,completed=True):
        if self.sweep_manager is None:
            self.result = self.part_dict
        else:
            list_of_tags = [result for result in gen_tag_extract(self.part_dict)]
            sweep_holder = SweepHolder(self.sweep_manager,list_of_tags)
            for sweep_holder_index,tag_values in enumerate(self.sweep_holder.tag_value_list):
                current_part_dict = delayed(_make_current_part_dict)(tag_values)
                sweep_holder.add(current_part_dict,sweep_holder_index)
            self.result = sweep_holder
        return True

    def compile(self):
        completed = self.geo_task.compile()
        completed = delayed(self._check_part_names)(completed)
        return delayed(self._generate_output)(completed)
        
