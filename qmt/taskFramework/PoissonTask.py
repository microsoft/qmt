from dask import delayed
from Task import Task
from GeometryTask import GeometryTask
from MaterialsTask import MaterialsTask
from SweepHolder import SweepHolder
from SweepTag import replace_tag_with_value

class PoissonTask(Task):

    def __init__(self,geo_task,mat_task,part_dict={},name='poisson_task'):
        super(self.__class__, self).__init__(**Task.remove_self_argument(locals()))
        assert isinstance(mat_task,MaterialsTask)
        self.mat_task = mat_task
        assert isinstance(geo_task,GeometryTask)
        self.geo_task = geo_task
    
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


    def _populate_result(self,mat_completed=True,geo_completed=True):
        if self.sweep_manager is None:
            self.result = delayed(self._solve_instance)(self.mat_task.result,self.geo_task.result,self.part_dict)
        else:
            sweep_holder = SweepHolder(self.sweep_manager,self.list_of_tags)
            for sweep_holder_index,tag_values in enumerate(sweep_holder.tagged_value_list):
                current_part_dict = self._make_current_part_dict(tag_values)
                total_index = sweep_holder.index_in_sweep[sweep_holder_index][0]
                materials_result_instance = self.mat_task.result.get_object(total_index)
                geo_result_instance = self.geo_task.result.get_object(total_index)
                output = delayed(self._solve_instance)(materials_result_instance,geo_result_instance,current_part_dict)
                sweep_holder.add(output,sweep_holder_index)
            self.result = sweep_holder#.compute()
        return True

