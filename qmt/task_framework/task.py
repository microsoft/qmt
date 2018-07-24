"""
Core module of the Task framework. Contains the base Task class,
from which all special purpose tasks are subclassed.

How to use, in a nutshell:
    To create a new task, subclass Task.
    The constructor for the subclass must call the superclass constructor with
        task_list=list of all dependent tasks,
        options=dictionary containing all other inputs to the subclass task,
        and optionally name=arbitrary name.
    These should also, in most cases, be the arguments to the subclass constructor--
    any arguments that the subclass constructor needs that are not dependent tasks should
    be placed into the options argument.
        See ms_tasks/poisson_task.py for an example.

    The actual work done by your Task subclass will be done in the _solve_instance callback,
    which you must implement.
    The _solve_instance callback expects two parameters:
    input_result_list and current_options.
    The input_result_list stores the outputs of the dependent tasks in the same order these tasks
    were given in the constructor, and current_options stores the options to the current task.
    The reason this latter has to be provided is that both the input results and options
    may be dependent on an automatically-handled sweep. Your _solve_instance does not have to know about this--
    it just has to compute its result dependent on the outputs of dependent tasks and its options,
    and return this result.

    Finally, to run a task, use the run() method,
    and extract the results (over a sweep) from the .result field as an iterable SweepHolder.
    (If there is no sweep, the .result field will simply contain the result as returned by _solve_instance.)

    For an example of how to set up a sweep, see ./tests/test_tasks_sweep.py and refer
    to the documentation of the sweeping classes in sweep.py.

Classes:
    Task
    TaskMetaclass
"""

from sweep import SweepHolder, gen_tag_extract, replace_tag_with_value
from dask import delayed


class TaskMetaclass(type):
    """
    Registers the class of each Task subclass for serialization.
    Might be deprecated soon.
    """
    class_registry = {}

    def __new__(mcs, name, bases, class_dict):
        cls = type.__new__(mcs, name, bases, class_dict)

        TaskMetaclass.register_class(cls)

        return cls

    @staticmethod
    def register_class(class_to_register):
        TaskMetaclass.class_registry[class_to_register.__name__] = class_to_register


class Task(object):
    """
    Abstract class for general simulation tasks run within the Dask framework.

    Translates the dependencies between Task instances reflected in their constructors
    into a Dask task graph and provides facilities for examining and evaluating this graph.

    Class attributes:
        current_instance_id: unique id for each task for serialization.
        Might be deprecated soon.

    Attributes:
        task_list: The tasks that this depends on.
        options: Additional options that control the operation of this.
        name: The name of the task.

    Notes for subclassing:

    """
    __metaclass__ = TaskMetaclass
    current_instance_id = 0

    def __init__(self, task_list, options, name):
        """
        Constructs a new Task.
        :param task_list: the tasks that this depends on.
        :param options: The additional options this requires.
        :param name: The name of this.
        """
        self.name = name
        if "#" not in self.name:
            self.name += "#" + str(Task.current_instance_id)
            Task.current_instance_id += 1

        self.options = options

        self.sweep_manager = None

        self.previous_tasks = task_list

        self.list_of_tags = [result for result in gen_tag_extract(self.options)]

        for task in self.previous_tasks:
            self.list_of_tags += task.list_of_tags

        self.result = None

    def compile(self):
        """
        Constructs the Dask task graph corresponding to this and its dependencies.
        """
        for task in self.previous_tasks:
            task.compile()
        if self.result is None:
            self._populate_result()

    def _make_current_options(self, tag_values):
        """
        Creates the concrete options of this corresponding to the current sweep iteration.

        Replaces each tag in the options of this with the values in the current sweep iteration.
        :param tag_values: a dict mapping each tag to its value in the current sweep iteration
        :return: the options needed by this task, with concrete values corresponding to the current sweep iteration.
        """
        current_options = self.options
        for i, tag in enumerate(self.list_of_tags):
            current_options = replace_tag_with_value(current_options, tag, tag_values[tag])
        return current_options

    def _solve_instance(self, input_result_list, current_options):
        """
        Does the actual computation of this.

        Note: Abstract method. Should be implemented by subclasses of Task.
        Note: This is a callback and should not be called directly.
        The parameters are automatically provided.
        :param input_result_list: The results produced by dependent tasks, in the order
        that the dependent tasks were given in the call to the Task base class constructor.
        :param current_options: The options of this corresponding to the current sweep iteration.
        """
        raise NotImplementedError("Task is missing the _solve_instance method!")

    def _populate_result(self):
        """
        Runs the sweep and populates self.result with dask.delayed objects.
        """
        if self.previous_tasks is None:
            raise ValueError("A list of dependent tasks must be passed to the constructor by subclasses!")
        if self.sweep_manager is None:
            # Treat the result as a single value to be computed
            input_result_list = [task.result for task in self.previous_tasks]
            self.result = delayed(self._solve_instance)(input_result_list, self.options, dask_key_name = self.name)
        else:
            # Make a SweepHolder to store results
            sweep_holder = SweepHolder(self.sweep_manager, self.list_of_tags)
            for sweep_holder_index, tag_values in enumerate(sweep_holder.tagged_value_list):
                current_options = self._make_current_options(tag_values)

                # Get the index in the total sweep
                total_index = sweep_holder.index_in_sweep[sweep_holder_index][0]

                # Use this index to get the appropriate results in dependent tasks
                input_result_list = [task.result.get_object(total_index) for task in self.previous_tasks]

                # Create a delayed object for this task's computation.
                output = delayed(self._solve_instance)(input_result_list, current_options, dask_key_name = self.name)
                sweep_holder.add(output, sweep_holder_index)
            self.result = sweep_holder


def visualize(self, filename=None):
    """
    Visualizes the task graph of this.

    :param filename: File to export the visualization to.
    """
    self.compile().visualize(filename=filename)


def run(self):
    """
    Runs the task DAG graph whose root is this.

    Replaces the delayed objects in this.result with actual results.

    pre: this.compile() has been called to initialize the task graph.
    """
    if self.result is None:
        self.compile()
    if self.sweep_manager is None:
        self.result = self.result.compute()
    else:
        self.result.compute()

# DEPRECATED serialization
# @staticmethod
# def from_dict(dict_representation):
#     taskName, data = dict_representation.items()[0]
#     className = data['class']
#     target_class = TaskMetaclass.class_registry[className]
#     kwargs = {}
#     for argName, argValue in data['argumentDictionary'].items():
#         if Task.isTaskRepresentation(argValue):
#             kwargs[argName] = Task.from_dict(argValue)
#         else:
#             kwargs[argName] = argValue
#     print(target_class)
#     return target_class(name=taskName, **kwargs)
#
# def save(self, file_name):
#     raise NotImplementedError("json serialization not yet implemented")
#     # TODO add serialization

# def to_dict(self):
#     result = OrderedDict()
#     result_data = OrderedDict()
#     result_data['class'] = self.__class__.__name__
#     result_data['argumentDictionary'] = self.dependencies_dict()
#     result[self.name] = result_data
#     return result

# with open(file_name, 'w') as jsonFile:
#     json.dump(self.to_dict(), jsonFile)
#
# def dependencies_dict(self):
#     result = {}
#     for argName, argValue in self.argumentDictionary.items():
#         if isinstance(argValue, Task):
#             result[argName] = argValue.to_dict()
#         else:
#             result[argName] = argValue
#
#     return result

# @staticmethod
# def remove_self_argument(init_arguments):
#     init_arguments.pop('self', None)
#     return init_arguments
#
# @staticmethod
# def isTaskRepresentation(argValue):
#     # check if it has form {name:otherDict}
#     hasSingleItem = isinstance(argValue, dict) and len(argValue.items()) == 1
#     # check if it has the class to reconstitute the task from
#     return hasSingleItem and "class" in argValue.values()[0]
