import dask
import dask.distributed


class SweepManager(object):
    """
    Represents a sweep over simulation input values.

    More precisely, represents a subset of the cartesian product of the input domains.

    Attributes:
        sweep_list: The sweep elements represented by this

    """

    # Abstraction function:
    # Each entry in the list self.sweep_list is an element in the product of input domains.
    # Each entry has the form {tag1: value1, ... tagN: valueN}
    # mapping SweepTag objects to values in each of the input domains.

    def __init__(self, sweep_list, dask_client=None):
        """
        Constructs a new SweepManager directly from sweep entries.
        :param sweep_list: a list representing values in the cartesian
        product of input domains. Each entry has the form {tag1: value1, ... tagN: valueN}
        :param dask_client: the dask client to run the sweep on. Defaults to
        a client on the local machine.
        """
        self.sweep_list = sweep_list
        assert isinstance(self.sweep_list, list) and \
               isinstance(self.sweep_list[0], dict), \
            'sweep_list must be a list of dicts.'
        assert all([set(sweep_list[0].keys()) == \
                    set(x.keys()) for x in sweep_list]), \
            'All dicts in sweep_list must have same keys.'

        if dask_client is None:
            dask_client = dask.distributed.Client(processes=False)  # client on the local machine

        self.dask_client = dask_client

        self.results = None

    # TODO test
    def createEmptySweep(self, dask_client=None):
        return SweepManager([{}], dask_client)

    @staticmethod
    def construct_cartesian_product(params_to_product):
        """
        Constructs a new SweepManager from data values for each input.
        :param params_to_product: a dictionary mapping tags to lists of input values
        :return: a SweepManager over the cartesian product of the
        input values in each input list
        """
        assert type(params_to_product) == type({}), \
            'params_to_product must be a dict of lists.'

        def merge_two_dicts(x, y):
            """
            Creates a new dictionary which contains both the mapping
            in x and the mapping in y, overwriting keys in y if necessary.
            :param x: the first dict to merge
            :param y: the second dict to merge
            :return: a union of x and y
            """
            z = x.copy()  # start with x's keys and values
            z.update(y)  # modifies z with y's keys and values & returns None
            return z

        result = [{}]
        for key in params_to_product:
            pool = params_to_product[key]
            result = [merge_two_dicts(x, {key: y}) for x in result for y in pool]
        return SweepManager(result)

    def run(self, task):
        """
        Runs the sweep represented by this.

        :param task: the top level task to run
        :return: the ReducedSweepFutures representing the result
        """

        def set_sweep_manager(current_task):
            current_task.sweep_manager = self
            for child_task in current_task.previous_tasks:
                set_sweep_manager(child_task)

        set_sweep_manager(task)
        return task.run()

    def __str__(self):
        return "<SweepManager with " + str(len(self.sweep_list)) + " entries>"

class ReducedSweepFutures(object):
    """
    Contains sweep information and results in the form of Dask futures.
    """
    def __init__(self, sweep, futures):
        self.sweep = sweep
        self.futures = futures

    @staticmethod
    def get_each_element_function(self):
        return self.sweep, [future.result() for future in self.futures]

    def __iter__(self):
        return iter(self.futures)

    def __str__(self):
        return str(self.futures)


# TODO
class ReducedSweepDelayed(object):
    def __init__(self, sweep, dask_client):
        self.sweep = sweep
        self.dask_client = dask_client
        self.delayed_results = [None]*len(self.sweep)

    @staticmethod
    def create_from_reduced_sweep_and_manager(sweep, manager):
        sweep = sweep
        dask_client = manager.dask_client
    # contains a ReducedSweep and forwards its methods
    # needs to take the dask client as well
    # has methods for producing the list of delayed objects
    # and reducing over itself using an arbitrary function.
    # This reduction can then be used in conjunction with the ReducedSweep
    # contained in this.
        return ReducedSweepDelayed(sweep, dask_client)

    def add(self, item, object_list_index):
        """
        Adds the result item to the results of this restricted sweep.
        :param item: the result to add
        :param object_list_index: the index of the result IN THE RESTRICTED SWEEP
        """
        self.delayed_results[object_list_index] = item

    def calculate_futures(self):
        """
        Triggers the execution of the sweep.
        """

        assert self.delayed_results[0] is not None
        futures = []
        for delayed_result in self.delayed_results:
            futures.append(self.dask_client.compute(delayed_result))

        return ReducedSweepFutures(self.sweep, futures)

    def visualize_entire_sweep(self, filename=None):
        delayed_proxy = dask.delayed(id)(self.delayed_results)
        delayed_proxy.visualize(filename=filename)
        return delayed_proxy.visualize()

    def visualize_single_sweep_element(self, filename=None):
        self.delayed_results[0].visualize(filename=filename)
        return self.delayed_results[0].visualize()

class ReducedSweep(object):
    """
    Represents the output of a sweep, restricted to the relevant subset of the input tags.

    SweepHolder represents the restriction of a sweep over many parameters,
    to a sweep over a subset of these parameters that is the input for a particular task.

    Public Attributes:
        sweep_manager: The whole sweep being performed.
        list_of_tags: The tags corresponding to the part of the sweep that this
            SweepHolder is restricted to.
        delayed_object_list: the result objects corresponding to elements in the restricted sweep
    """

    def __init__(self, list_of_tags, sweep_list, tagged_value_list, index_in_sweep):
        self.list_of_tags = list_of_tags
        self.sweep_list = sweep_list
        self._tagged_value_list = tagged_value_list
        self._index_in_sweep = index_in_sweep

        # contains info about the sweep points in the reduced sweep
        # and the mapping of the reduced sweep to the total sweep

    @staticmethod
    def create_from_manager_and_tags(sweep_manager, list_of_tags):
        """
                Constructs the restriction of the sweep sweep_manager to the input tagged by list_of_tags.

                :param sweep_manager: The sweep to restrict
                :param list_of_tags: The tags to restrict the input to
                """

        sweep_list = sweep_manager.sweep_list

        tagged_value_list = []
        index_in_sweep = []
        # The following nested for-loops could probably be made more
        # elegant, but it works for now

        # For each point in the total sweep
        for i, sweep_point in enumerate(sweep_list):

            # Check whether it is a new point with respect to the restricted
            # list of tags in self.list_of_tags, or whether this combination
            # of the relevant tags has already been encountered in the sweep
            new_point = True
            point_small_index = None
            for j, small_sweep_point in enumerate(tagged_value_list):
                if small_sweep_point.viewitems() <= sweep_point.viewitems():
                    new_point = False
                    point_small_index = j

            # If the sweep point is a new point,
            # add the corresponding sweep element {tag1: value1, ... tagN: valueN}
            # to the list of values
            if new_point:
                tagged_value_list += [dict((tag, sweep_point[tag]) for tag in list_of_tags)]
                index_in_sweep += [[i]]
            else:
                index_in_sweep[point_small_index] += [i]

        index_in_sweep = index_in_sweep
        delayed_object_list = [None] * len(index_in_sweep)

        return ReducedSweep(list_of_tags, sweep_list, tagged_value_list, index_in_sweep)

    def convert_to_reduced_index(self, total_index):
        """
        Converts the index of a sweep element in the total sweep to the corresponding index in the reduced sweep.
        :param total_index: index of a sweep element in the total sweep
        :return: corresponding index in the reduced sweep
        """
        reduced_index = [total_index in sublist for sublist in self._index_in_sweep].index(True)
        return reduced_index

    def convert_to_total_indices(self, reduced_index):
        """
        Gets a list of indices in the total sweep corresponding to the index of an element in the reduced sweep.

        :param reduced_index: index of an element in the reduced sweep
        :return: list of corresponding indices in the total sweep
        """
        total_index = self._index_in_sweep[reduced_index]

    def __len__(self):
        return len(self._index_in_sweep)


# TODO refactor the creation of sweeps and sweepTags to make script less noisy
class SweepTag(object):
    """
    Unique tag for id'ing parameters in the sweep.
    """

    def __init__(self, tag_name):
        self.tag_name = tag_name

    def __str__(self):
        return self.tag_name

    def __repr__(self):
        return self.tag_name

    def __eq__(self, other):
        if isinstance(other, SweepTag):
            return self.tag_name == other.tag_name
        return False

    def __ne__(self, other):
        return not self.__eq__(other)


def gen_tag_extract(nested_dictionary_of_tags):
    """
    Extract all tags from nested dictionary that may have tags
    as values at any level
    :param nested_dictionary_of_tags: exactly what it sounds like
    :return: a generator that yields all the tags in the dictionary
    """
    if hasattr(nested_dictionary_of_tags, 'iteritems'):
        for k, v in nested_dictionary_of_tags.iteritems():
            if isinstance(v, SweepTag):
                yield v
            if isinstance(v, dict):
                for result in gen_tag_extract(v):
                    yield result


def replace_tag_with_value(name_to_tag_mapping, tag, new_value):
    """
    Returns a copy of name_to_tag_mapping with values of tag replaced with new_value.
    :param name_to_tag_mapping: Dictionary mapping parameter names to SweepTags.
    :param tag: The SweepTag to replace.
    :param new_value: the value to replace it with.
    :return: a copy of name_to_tag_mapping with values of tag replaced with new_value
    """
    var_copy = {}
    if hasattr(name_to_tag_mapping, 'iteritems'):
        for k, v in name_to_tag_mapping.iteritems():
            if v == tag:
                var_copy[k] = new_value
            elif isinstance(v, dict):
                var_copy[k] = replace_tag_with_value(v, tag, new_value)
            else:
                var_copy[k] = v
    return var_copy
