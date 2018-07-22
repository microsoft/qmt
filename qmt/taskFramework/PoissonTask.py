from dask import delayed
from SweepTag import gen_tag_extract,replace_tag_with_value

class PoissonTask(Task):

    def __init__(self,geo_task,mat_task,part_dict={},name='poisson_task'):
        super(self.__class__, self).__init__(**Task.remove_self_argument(locals()))
        self.mat_task = mat_task
        self.geo_task = geo_task
        self.part_dict = part_dict
    
    def _make_current_part_dict(tag_values):
        current_part_dict = self.part_dict
        for i,tag in enumerate(list_of_tags):
            current_part_dict = replace_tag_with_value(current_part_dict,tag,tag_values[tag])
        return current_part_dict

    def _solve_instance(materials_result_instance,geo_result_instance,current_part_dict):
        output = ''
        for part in geo_result_instance.keys():
            output += 'part: ' + part
            output += ', side length: ' + geo_result_instance[part]['side length']
            output += ', material: ' + materials_result_instance[part]['material']
            output += ', voltage: ' + str(current_part_dict[part]['voltage'])
        return output


    def _generate_output(completed=True):
        if self.sweep_manager is None:
            self.result = _solve_instance(self.mat_task.result,self.geo_task.result,self.part_dict)
        else:
            list_of_tags = [result for result in gen_tag_extract(self.part_dict)]
            list_of_tags += [self.mat_task.result.list_of_tags]
            list_of_tags += [self.geo_task.result.list_of_tags]
            sweep_holder = SweepHolder(self.sweep_manager,list_of_tags)
            for sweep_holder_index,tag_values in enumerate(self.sweep_holder.tag_value_list):
                current_part_dict = delayed(_make_current_part_dict)(tag_values)
                total_index = delayed(sweep_holder.index_in_sweep[sweep_holder_index][0])
                materials_result_instance = delayed(self.mat_task.result.get_object)(total_index)
                geo_result_instance = delayed(self.geo_task.result.get_object)(total_index)
                output = delayed(_solve_instance)(materials_result_instance,geo_result_instance,current_part_dict)
                sweep_holder.add(output,sweep_holder_index)
            delayed(self.result = sweep_holder)
        return True

    def run(self):
        mat_completed = delayed(self.mat_task.run)()
        geo_completed = delayed(self.geo_task.run)()
        completed = delayed(mat_completed and geo_completed)
        return delayed(self._generate_output)(completed)