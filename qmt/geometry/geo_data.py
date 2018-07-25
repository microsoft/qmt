class Geo1DData:
    def __init__(self):
        """
        Class for holding a 1D gemetry specification.
        """
        self.parts = {}

    def add_part(self, part_name, start_point, end_point, overwrite=False):
        """
        Add a part to this geometry.
        :param str part_name: Name of the part to create
        :param float start_point: Position of the start of the part
        :param float end_point: Position of the end of the part
        :param bool overwrite (False): Should we allow this to overwrite?
        """
        start, end = sorted([start_point, end_point])
        if (part_name in self.parts) and (not overwrite):
            raise ValueError("Attempted to overwrite then part "+part_name+".")
        else:
            self.parts[part_name] = (start_point, end_point)

    def remove_part(self,part_name,ignore_if_absent=False):
        """
        Remove a part from this geometry.
        :param str part_name: Name of part to remove
        :param bool ignore_if_absent (False): Should we ignore an attempted removal if the part name is not found?
        """
        if part_name in self.parts:
            del self.parts[part_name]
        else:
            if not ignore_if_absent:
                raise ValueError("Attempted to remove the part "+part_name+", which doesn't exist.")
            else:
                pass

