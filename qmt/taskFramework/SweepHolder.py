class SweepHolder(object):

    def __init__(self,sweep_manager,list_of_tags):

        self.list_of_tags = list_of_tags
        self.sweep_list = sweep_manager.sweep_list
        tagged_value_list = []
        index_in_sweep = []
        #The following nested for-loops could probably be made more
        #elegant, but it works for now
        for i, sweep_point in enumerate(sweep_list):
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
        
    
    def get_object(self,total_index):
        small_index = [total_index in sublist in self.index_in_sweep].index(True)
        return self.object_list[small_index]

    def add(self,item,object_list_index):
        self.object_list[object_list_index] = item
