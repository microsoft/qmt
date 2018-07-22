from dask import delayed
from Task import Task
from SweepHolder import SweepHolder
from SweepTag import gen_tag_extract,replace_tag_with_value

class PoissonTask(Task):

    def __init__(self,geo_task,mat_task,part_dict={},name='poisson_task'):
        super(self.__class__, self).__init__(**Task.remove_self_argument(locals()))
        self.mat_task = mat_task
        self.geo_task = geo_task
        self.part_dict = part_dict
    
    def _make_current_part_dict(self,tag_values):
        current_part_dict = self.part_dict
        for i,tag in enumerate(self.list_of_tags):
            current_part_dict = replace_tag_with_value(current_part_dict,tag,tag_values[tag])
        return current_part_dict

    def _solve_instance(self,materials_result_instance,geo_result_instance,current_part_dict):
        output = ''
        for part in geo_result_instance.keys():
            output += ' part: ' + part
            output += ', side length: ' + str(geo_result_instance[part]['side length'])
            output += ', material: ' + materials_result_instance[part]['material']
            output += ', voltage: ' + str(current_part_dict[part]['voltage'])
        return output


    def _generate_output(self,mat_completed=True,geo_completed=True):
        if self.sweep_manager is None:
            self.result = self._solve_instance(self.mat_task.result,self.geo_task.result,self.part_dict)
        else:
            self.list_of_tags = [result for result in gen_tag_extract(self.part_dict)]
            self.list_of_tags += self.mat_task.list_of_tags
            self.list_of_tags += self.geo_task.list_of_tags
            sweep_holder = SweepHolder(self.sweep_manager,self.list_of_tags)
            for sweep_holder_index,tag_values in enumerate(sweep_holder.tagged_value_list):
                current_part_dict = self._make_current_part_dict(tag_values)
                total_index = sweep_holder.index_in_sweep[sweep_holder_index][0]
                materials_result_instance = self.mat_task.result.get_object(total_index)
                geo_result_instance = self.geo_task.result.get_object(total_index)
                output = delayed(self._solve_instance)(materials_result_instance,geo_result_instance,current_part_dict)
                #current_part_dict = self._make_current_part_dict(tag_values)
                #total_index = sweep_holder.index_in_sweep[sweep_holder_index][0]
                #materials_result_instance = self.mat_task.result.get_object(total_index)
                #geo_result_instance = self.geo_task.result.get_object(total_index)
                #output = self._solve_instance(materials_result_instance,geo_result_instance,current_part_dict)
                sweep_holder.add(output,sweep_holder_index)
            self.result = sweep_holder#.compute()
        return True

    def compile(self):
        mat_completed = self.mat_task.compile()
        geo_completed = self.geo_task.compile()
        self._generate_output()
        return self.result
        #return delayed(self._generate_output)(mat_completed,geo_completed)

