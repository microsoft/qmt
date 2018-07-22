from dask import delayed
from Task import Task
from SweepTag import gen_tag_extract,replace_tag_with_value

class GeometryTask(Task):

    def __init__(self,part_dict={},name='geometry_task'):
        super(self.__class__, self).__init__(**Task.remove_self_argument(locals()))
        self.part_dict = part_dict
    
    def _make_current_part_dict(tag_values):
        current_part_dict = self.part_dict
        for i,tag in enumerate(list_of_tags):
            current_part_dict = replace_tag_with_value(current_part_dict,tag,tag_values[tag])
        return current_part_dict


    def _generate_output(completed=True):
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

    def run(self):
        return delayed(self._generate_output)(completed)
