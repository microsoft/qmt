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

    There is also a _solve_gather callback for use in specialized situations.

    IMPORTANT: object references in both of these callback parameters must be treated as read-only
    or copied before modification,
    since they are shared across parameter sweeps.

    Both the input results and options
    may be dependent on an automatically-handled sweep. Your _solve_instance does not have to know about this--
    it just has to compute its result dependent on the outputs of dependent tasks and its options,
    and return this result.

    Finally, to run a task, use the run() method,
    which begins the actual calculation. run() returns immediately and stores pointers to the results undergoing
    computation in a SweepHolderFutures object in the .computed_result field of the task. This object
    associates sweep parameters with the results being computed. You can iterate over results being computed,
    wait for the results to be computed with calculate_completed_results(), or wait for any particular result
    with get_completed_result().

    For an example of how to set up a sweep, see ./tests/test_tasks_sweep.py and refer
    to the documentation of the sweeping classes in sweep.py.

Classes:
    Task
"""

import copy

import dask
from dask import delayed

from qmt.tasks.sweep import SweepManager, ReducedSweep, ReducedSweepDelayed, ReducedSweepResults, gen_tag_extract, replace_tag_with_value

class Task(object):
    """
    Abstract class for general simulation tasks run within the Dask framework.

    Translates the dependencies between Task instances reflected in their constructors
    into a Dask task graph and provides facilities for examining and evaluating this graph.

    Class attributes:
        current_instance_id: unique id for each task for serialization.

    Attributes:
        previous_tasks: The tasks that this depends on.
        options: Additional options that control the operation of this.
        resources: resources for the Dask client.
        gather: default False. If false, the task is assumed to have a _solve_instance method, and takes in
            one sweep point's worth of inputs. If true, the task is assumed to have a _solve_gathered method,
            and takes in inputs from every sweep point in its restricted sweep.
        name: The name of the task.
        list_of_tags: the list of sweep input tags that the sweep over this depends on
        delayed_result: the task graph rooted at this
        computed_result: SweepHolderFutures pointing at (possibly pending) results.
        daskless_result: result, if the task was run with run_daskless
    """
    current_instance_id = 0

    def __init__(self, task_list=None, options=None, name="Task", gather=False):
        """
        Constructs a new Task.
        :param task_list: the tasks that this depends on.
        :param options: The additional options this requires.
        Options should be a nested dictionary of immutable objects.
        :param name: The name of this.
        """
        self.name = name
        if "#" not in self.name:
            self.name += "#" + str(Task.current_instance_id)
            Task.current_instance_id += 1

        if task_list is None:
            task_list = []

        if options is None:
            options = {}

        self.options = options
        self.resources = None
        if 'resources' in options:
            self.resources = options['resources']
        self.gather = gather

        self.sweep_manager = None  # Set by an enclosing sweep manager

        self.previous_tasks = task_list

        self.list_of_tags = [result for result in gen_tag_extract(self.options)]

        for task in self.previous_tasks:
            self.list_of_tags += task.list_of_tags

        self.delayed_result = None
        self.computed_result = None

        self.daskless_result = None

    def _compile(self):
        """
        Constructs the Dask task graph corresponding to this and its dependencies.
        """
        for task in self.previous_tasks:
            task._compile()
        if self.delayed_result is None:
            self._populate_result()

    def _make_current_options(self, tag_values):
        """
        Creates the concrete options of this corresponding to the current sweep iteration.

        Replaces each tag in the options of this with the values in the current sweep iteration.
        :param tag_values: a dict mapping each tag to its value in the current sweep iteration
        :return: the options needed by this task, with concrete values corresponding to the current sweep iteration.
        """
        current_options = copy.deepcopy(self.options)
        for i, tag in enumerate(self.list_of_tags):
            current_options = replace_tag_with_value(current_options, tag, tag_values[tag])
        return current_options

    @staticmethod
    def _solve_instance(input_result_list, current_options):
        """
        Does the actual computation of this.

        Note: Abstract method. Should be implemented by subclasses of Task.
        Note: This is a callback and should not be called directly.
        The parameters are automatically provided.

        IMPORTANT: object references in both current_options and input_result_list
        must be treated as read-only or copied before modification, since they are shared across parameter sweeps.

        :param input_result_list: The results produced by dependent tasks, in the order
        that the dependent tasks were given in the call to the Task base class constructor.
        :param current_options: The options of this corresponding to the current sweep iteration.
        """
        raise NotImplementedError("Task is missing the _solve_instance method!")

    @staticmethod
    def _solve_gathered(list_of_input_result_lists, list_of_current_options, result_sweep):
        """
        Does the actual computation of a 'gathered' task (e.g. COMSOL meshing).

        Note: Abstract method. Should be implemented by subclasses of Task.
        Note: This is a callback and should not be called directly.
        The parameters are automatically provided.

        IMPORTANT: object references in both list_of_current_options and list_of_input_result_list
        must be treated as read-only or copied before modification, since they are shared across parameter sweeps.

        :param list_of_input_result_lists: The list of results produced by dependent tasks, in the order
        that the dependent tasks were given in the call to the Task base class constructor.
        :param list_of_current_options: The list of options of this corresponding to the current sweep iteration.
        :param result_sweep: Empty ReducedSweepResults object
        """
        raise NotImplementedError("Task is missing the _solve_gathered method!")

    def _populate_result(self):
        """
        Runs the sweep and populates self.delayed_result with dask.delayed objects.
        """
        if self.previous_tasks is None:
            raise ValueError("A list of dependent tasks must be passed to the constructor by subclasses!")
        else:
            reduced_sweep = ReducedSweep.create_from_manager_and_tags(self.sweep_manager, self.list_of_tags)

            self.delayed_result = ReducedSweepDelayed.create_from_reduced_sweep_and_manager(reduced_sweep,
                                                                                            self.sweep_manager)
            list_of_current_options = []
            list_of_input_result_lists = []
            for sweep_holder_index, tag_values in enumerate(self.delayed_result.tagged_value_list):
                current_options = self._make_current_options(tag_values)
                list_of_current_options += [current_options]
                # Get an index in the total sweep
                total_index = self.delayed_result.sweep.convert_to_total_indices(sweep_holder_index)[0]

                # Use this index to get the appropriate results in dependent tasks
                input_result_list = [task.delayed_result.get_datum(total_index) for task in self.previous_tasks]
                list_of_input_result_lists += [input_result_list]

                if not self.gather:
                    # Create a delayed object for this task's computation.
                    output = delayed(self.__class__._solve_instance)(input_result_list, current_options,
                                                           dask_key_name=self.name + '_' + str(sweep_holder_index))
                    self.delayed_result.add(output, sweep_holder_index)
            if self.gather:
                result_sweep = ReducedSweepResults.create_empty_from_manager_and_tags(self.sweep_manager, self.list_of_tags)
                self.delayed_result = delayed(self.__class__._solve_gathered)(list_of_input_result_lists, list_of_current_options,
                                                                    result_sweep, dask_key_name=self.name)

    def visualize_entire_sweep(self, filename=None):
        """
        Return a visualization of the entire task graph of the sweep rooted at this as an IPython image object.

        If filename is given, also exports the visualization to the given file.
        Supported

        :param filename: Optional file to export the visualization to
        :return: A visualization of he entire task graph of the sweep rooted at this as an IPython image object.
        """
        if self.delayed_result is None:
            self._compile()

        return self.delayed_result.visualize_entire_sweep(filename=filename)

    def visualize_single_sweep_element(self, filename=None):
        """
        Return a visualization of task graph of one element of the sweep rooted at this as an IPython image object.

        If filename is given, also exports the visualization to the given file.
        :param filename: Optional file to export the visualization to
        :return: a visualization of task graph of one element of the sweep rooted at this as an IPython image object.

        """
        if self.delayed_result is None:
            self._compile()

        return self.delayed_result.visualize_single_sweep_element(filename=filename)

    # TODO split off the gathered tasks and normal tasks into subclasses
    def _run(self):
        """
        Runs the task DAG graph whose root is this and returns the results.

        Replaces the delayed objects in this.delayed_result with actual results.
        :return:
        """
        if self.delayed_result is None:
            self._compile()

        if self.computed_result is None:
            for task in self.previous_tasks:
                task._run()
            if self.gather:
                self.computed_result = self.sweep_manager.dask_client.compute(self.delayed_result)
            else:
                self.computed_result = self.delayed_result.calculate_futures(resources=self.resources)

        return self.computed_result

    # Deprecated. See visualization/plot_helpers
    # def reduce(self, reduce_function=None):
    #     assert self.computed_result is not None
    #
    #     if reduce_function is None:
    #         reduce_function = Task.gather_futures
    #     if self.gather:
    #         return reduce_function([self.computed_result])
    #     else:
    #         return reduce_function(self.computed_result)

    # Precondition: there is no sweep (i.e. no tags in the options)
    def run_daskless(self):
        for task in self.previous_tasks:
            task.run_daskless()

        input_result_list = [task.daskless_result for task in self.previous_tasks]

        if self.gather:
            self.sweep_manager = SweepManager.create_empty_sweep(dask_client=None)
            self.daskless_result = self.__class__._solve_gathered([input_result_list], [self.options]).only()
        else:
            self.daskless_result = self.__class__._solve_instance(input_result_list, self.options)

        return self.daskless_result
