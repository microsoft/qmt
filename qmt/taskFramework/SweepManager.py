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

    def run_task(self,task):
        def set_sweep_manager(current_task):
            current_task.sweep_manager = self
            for child_task in current_task.previous_tasks:
                set_sweep_manager(child_task)
        
        set_sweep_manager(task)
        task.run()
