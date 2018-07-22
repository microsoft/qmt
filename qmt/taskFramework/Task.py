import dask
from collections import OrderedDict
import json
from TaskMetaclass import TaskMetaclass
from SweepTag import gen_tag_extract,replace_tag_with_value
from SweepHolder import SweepHolder
from dask import delayed

# todo base import then factories


class Task(object):
    __metaclass__ = TaskMetaclass
    current_instance_id = 0

    def __init__(self, *args, **kwargs):

        if "name" not in kwargs:
            raise AttributeError("All subclasses of Task must have a 'name' keyword argument")

        self.name = kwargs["name"]
        if "#" not in self.name:
            self.name += "#" + str(Task.current_instance_id)
            Task.current_instance_id += 1

        self.argumentDictionary = kwargs
        self.argumentDictionary.pop("name", None)

        if 'options' in kwargs:
            self.options = kwargs['options']

        self.sweep_manager = None

        previous_tasks = []
        for kwarg in kwargs.values():
            if isinstance(kwarg,Task):
                previous_tasks += [kwarg]
        self.previous_tasks = previous_tasks

        self.list_of_tags = [result for result in gen_tag_extract(self.options)]
        if 'inheret_tags_from' not in kwargs:
            inheret_from = self.previous_tasks
        elif kwargs['inheret_tags_from'] is None:
            inheret_from = self.previous_tasks
        else:
            inheret_from = kwargs['inheret_tags_from']
        for task in inheret_from:
            self.list_of_tags += task.list_of_tags

        self.result = None
        self.input_task_list = None

    def to_dict(self):
        result = OrderedDict()
        result_data = OrderedDict()
        result_data['class'] = self.__class__.__name__
        result_data['argumentDictionary'] = self.dependencies_dict()
        result[self.name] = result_data
        return result

    @staticmethod
    def from_dict(dict_representation):
        taskName, data = dict_representation.items()[0]
        className = data['class']
        target_class = TaskMetaclass.class_registry[className]
        kwargs = {}
        for argName, argValue in data['argumentDictionary'].items():
            if Task.isTaskRepresentation(argValue):
                kwargs[argName] = Task.from_dict(argValue)
            else:
                kwargs[argName] = argValue
        print(target_class)
        return target_class(name=taskName, **kwargs)

    def save(self, file_name):
        with open(file_name, 'w') as jsonFile:
            json.dump(self.to_dict(), jsonFile)

    def dependencies_dict(self):
        result = {}
        for argName, argValue in self.argumentDictionary.items():
            if isinstance(argValue, Task):
                result[argName] = argValue.to_dict()
            else:
                result[argName] = argValue

        return result

    def compile(self):
        for task in self.previous_tasks:
            task.compile()
        if self.result is None:
            self._populate_result()
    
    def _make_current_options(self,tag_values):
        current_options = self.options
        for i,tag in enumerate(self.list_of_tags):
            current_options = replace_tag_with_value(current_options,tag,tag_values[tag])
        return current_options

    def _solve_instance(self):
        raise NotImplementedError("Task is missing the _solve_instance method!")

    def _populate_result(self):
        if self.input_task_list is None:
            raise ValueError("self.input_task_list must be set in init!")
        if self.sweep_manager is None:
            input_result_list = [task.result for task in self.input_task_list]
            self.result = delayed(self._solve_instance)(input_result_list,self.options)
        else:
            sweep_holder = SweepHolder(self.sweep_manager,self.list_of_tags)
            for sweep_holder_index,tag_values in enumerate(sweep_holder.tagged_value_list):
                current_options = self._make_current_options(tag_values)
                total_index = sweep_holder.index_in_sweep[sweep_holder_index][0]
                input_result_list = [task.result.get_object(total_index) for task in self.input_task_list]
                output = delayed(self._solve_instance)(input_result_list,current_options)
                sweep_holder.add(output,sweep_holder_index)
            self.result = sweep_holder

    def visualize(self,filename=None):
        return self.compile().visualize(filename=filename)

    def run(self):
        if self.result is None:
            self.compile()
        if self.sweep_manager is None:
            self.result = self.result.compute()
        else:
            self.result.compute()

    @staticmethod
    def remove_self_argument(init_arguments):
        init_arguments.pop('self', None)
        return init_arguments

    @staticmethod
    def isTaskRepresentation(argValue):
        # check if it has form {name:otherDict}
        hasSingleItem = isinstance(argValue, dict) and len(argValue.items()) == 1
        # check if it has the class to reconstitute the task from
        return hasSingleItem and "class" in argValue.values()[0]
