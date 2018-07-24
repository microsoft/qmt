import dask

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

    def __init__(self, sweep_list):
        """
        Constructs a new SweepManager directly from sweep entries.
        :param sweep_list: a list representing values in the cartesian
        product of input domains. Each entry has the form {tag1: value1, ... tagN: valueN}
        """
        self.sweep_list = sweep_list
        assert isinstance(self.sweep_list, list) and \
               isinstance(self.sweep_list[0], dict), \
            'sweep_list must be a list of dicts.'
        assert all([set(sweep_list[0].keys()) == \
                    set(x.keys()) for x in sweep_list]), \
            'All dicts in sweep_list must have same keys.'

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
        def set_sweep_manager(current_task):
            current_task.sweep_manager = self
            for child_task in current_task.previous_tasks:
                set_sweep_manager(child_task)

        set_sweep_manager(task)
        task.run()

    def __str__(self):
        return "<SweepManager with " + str(len(self.sweep_list)) + " entries>"


class SweepHolder(object):
    """
    Represents the output of a sweep, restricted to the relevant subset of the input tags.

    SweepHolder represents the restriction of a sweep over many parameters,
    to a sweep over a subset of these parameters that is the input for a particular task.
    It also stores the results of the restricted sweep

    Attributes:
        sweep_manager: The whole sweep being performed.
        list_of_tags: The tags corresponding to the part of the sweep that this
            SweepHolder is restricted to.
        object_list: the result objects corresponding to elements in the restricted sweep
    """

    def __init__(self, sweep_manager, list_of_tags):
        """
        Constructs the restriction of the sweep sweep_manager to the input tagged by list_of_tags.

        :param sweep_manager: The sweep to restrict
        :param list_of_tags: The tags to restrict the input to
        """

        self.list_of_tags = list_of_tags
        self.sweep_list = sweep_manager.sweep_list

        tagged_value_list = []
        index_in_sweep = []
        # The following nested for-loops could probably be made more
        # elegant, but it works for now

        # For each point in the total sweep
        for i, sweep_point in enumerate(self.sweep_list):

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

        self.tagged_value_list = tagged_value_list
        self.index_in_sweep = index_in_sweep
        self.object_list = [None] * len(self.index_in_sweep)

    def __str__(self):
        return str(self.object_list)

    def get_object(self, total_index):
        """
        Retrieves a result object by its index in the total sweep
        defined by self.sweep_list
        :param total_index: index in the total sweep
        :return: the result at index total_index in the total sweep
        """
        small_index = [total_index in sublist for sublist in self.index_in_sweep].index(True)
        return self.object_list[small_index]


    def add(self, item, object_list_index):
        """
        Adds the result item to the results of this restricted sweep.
        :param item: the result to add
        :param object_list_index: the index of the result IN THE RESTRICTED SWEEP
        """
        self.object_list[object_list_index] = item

    def compute(self):
        """
        Triggers the execution of the sweep.
        """
        # self.object_list = map(lambda x: x.compute(),self.object_list)
        # print self.object_list
        # self.object_list[0] = self.object_list[0].compute()
        self.object_list = dask.compute(*self.object_list)

    def __iter__(self):
        return iter(self.object_list)

    def visualize(self, filename):
        print(filename)
        dask.delayed(list)(*self.object_list).visualize(filename=filename)

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
