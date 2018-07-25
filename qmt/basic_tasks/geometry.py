# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

from qmt.task_framework import Task


class Geometry1D(Task):
    def __init__(self, options=None, name='geometry_1d_task'):
        """
        Builds a geometry in 1D.
        :param dict options: The dictionary specifying parts, of the form {"part_name":(start_coord,stop_coord)}
        :param str name: The name of this task.
        """
        super(Geometry1D, self).__init__([], options, name)

    def _solve_instance(self, input_result_list, current_options):
        """
        :param list input_result_list: This is an empty list.
        :param dict current_options: The dictionary specifying parts from above.
        :return geo_1d: A Geo1DData object.
        """
        return current_options


class Geometry2D(Task):
    def __init__(self, options=None, name='geometry_2d_task'):
        """
        Builds a geometry in 2D.
        :param dict options: The dictionary specifying parts, of the form {"part_name":Part3D}
        :param str name: The name of this task.
        """
        super(Geometry2D, self).__init__([], options, name)
        # for part_name in options:
        #     assert type(options[part_name]) is Part2D

    def _solve_instance(self, input_result_list, current_options):
        """
        :param list input_result_list: This is an empty list.
        :param dict current_options: The dictionary specifying parts from above.
        :return: geo_2d: A Geo2DData object.
        """
        return current_options


class Geometry3D(Task):
    def __init__(self, options=None, name='geometry_3d_task'):
        """
        Builds a geometry in 3D.
        :param dict options: The dictionary specifying parts and and FreeCAD infromation. It should be of the form
        {"fcname":path_to_freeCAD_file,"parts_dict":parts_dict}, where parts_dict is a dictionary of the form
        {part_name:Part3D}.
        :param str name: The name of this task.
        """
        super(Geometry3D, self).__init__([], options, name)
        # assert type(options["fcname"]) is str
        # assert type(options["parts_dict"]) is dict
        # for partDirective in options["part_dict"]:
        #     assert type(options["part_dict"][partDirective]) is Part3D

    def _solve_instance(self, input_result_list, current_options):
        """
        :param list input_result_list: This is an empty list.
        :param dict current_options: The dictionary specifying parts from above.
        :return geo_3d: A Geo3DData object.
        """
        return current_options


# ~ class GeoFreeCAD(Geometry3D):  # needs adjustments
class GeoFreeCAD(Task):

    def __init__(self, options=None, name='freecad_task'):
        super(GeoFreeCAD, self).__init__([], options, name)

    def _solve_instance(self, input_result_list, current_options):

        print(current_options)

        # TODO: write a sub2.7 subprocess wrapper
        # at current sweep point:
        # - updateParams
        # - object construction
        # - litography
        # - point region map

        
        import qmt.geometry.freecad as cad
        cad.auxiliary.pywrapper(input_result_list, current_options, 'updateParams')

        if 'parts' in current_options:  # TODO: parts = dict{ 'part1': 3DPart, ... }
            pass

        doc = cad.FreeCAD.newDocument('instance')
        cad.FreeCAD.setActiveDocument('instance')

        if 'filepath' in current_options:
            doc.load(current_options['filepath'])
        elif 'document' in current_options:
            for obj in current_options['document'].Objects:
                doc.copyObject(obj, False)  # don't deep copy dependencies
        else:
            raise ValueError("No FreeCAD document available")

        # extend params dictionary to generic parts schema
        fcdict = {key:(value, 'freeCAD') for (key,value) in current_options['params'].items()}

        cad.fileIO.updateParams(doc, fcdict)
        return doc
