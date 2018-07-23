import dask

class SweepManager(object):

    def __init__(self, sweep_list):
        self.sweep_list = sweep_list
        assert isinstance(self.sweep_list,list) and \
                isinstance(self.sweep_list[0],dict),\
                'sweep_list must be a list of dicts.'
        assert all([set(sweep_list[0].keys()) == \
                set(x.keys()) for x in sweep_list]),\
                'All dicts in sweep_list must have same keys.'

    @staticmethod
    def construct_cartesian_product(params_to_product):
        assert type(params_to_product) == type({}),\
                'params_to_product must be a dict of lists.'
        def merge_two_dicts(x, y):
            z = x.copy()   # start with x's keys and values
            z.update(y)    # modifies z with y's keys and values & returns None
            return z
        result = [{}]
        for key in params_to_product:
            pool = params_to_product[key]
            result = [merge_two_dicts(x,{key:y}) for x in result for y in pool]
        return SweepManager(result)

    def run(self,task):
        def set_sweep_manager(current_task):
            current_task.sweep_manager = self
            for child_task in current_task.previous_tasks:
                set_sweep_manager(child_task)
        
        set_sweep_manager(task)
        task.run()

class SweepHolder(object):

    def __init__(self,sweep_manager,list_of_tags):

        self.list_of_tags = list_of_tags
        self.sweep_list = sweep_manager.sweep_list
        tagged_value_list = []
        index_in_sweep = []
        #The following nested for-loops could probably be made more
        #elegant, but it works for now
        for i, sweep_point in enumerate(self.sweep_list):
            new_point = True
            point_small_index = None
            for j, small_sweep_point in enumerate(tagged_value_list):
                if small_sweep_point.viewitems() <= sweep_point.viewitems():
                    new_point = False
                    point_small_index = j
            if new_point:
                tagged_value_list += [dict((tag, sweep_point[tag]) for tag in list_of_tags)]
                index_in_sweep += [[i]]
            else:
                index_in_sweep[point_small_index] += [i]

        self.tagged_value_list = tagged_value_list
        self.index_in_sweep = index_in_sweep
        self.object_list = [None]*len(self.index_in_sweep)
        
    def __str__(self):
        return str(self.object_list)
    
    def get_object(self,total_index):
        small_index = [total_index in sublist for sublist in self.index_in_sweep].index(True)
        return self.object_list[small_index]

    def add(self,item,object_list_index):
        self.object_list[object_list_index] = item

    def compute(self):
         #self.object_list = map(lambda x: x.compute(),self.object_list)
         #print self.object_list
         #self.object_list[0] = self.object_list[0].compute()
         self.object_list = dask.compute(*self.object_list)
         
class SweepTag(object):

    def __init__(self,tag_name):
        self.tag_name = tag_name
    
    def __str__(self):
        return self.tag_name
    
    def __repr__(self):
        return self.tag_name
    
    def __eq__(self,other):
        if isinstance(other,SweepTag):
            return self.tag_name == other.tag_name
        return False
    
    def __ne__(self,other):
        return not self.__eq__(other)

def gen_tag_extract(var):
    if hasattr(var,'iteritems'):
        for k, v in var.iteritems():
            if isinstance(v,SweepTag):
                yield v
            if isinstance(v, dict):
                for result in gen_tag_extract(v):
                    yield result

def replace_tag_with_value(var,tag,value):
    var_copy = {}
    if hasattr(var,'iteritems'):
        for k, v in var.iteritems():
            if v == tag:
                var_copy[k] = value
            elif isinstance(v, dict):
                var_copy[k] = replace_tag_with_value(v,tag,value)
            else:
                var_copy[k] = v
    return var_copy
         