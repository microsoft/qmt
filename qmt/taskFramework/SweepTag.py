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
                for result in gen_dict_extract(v):
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
