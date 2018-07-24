from qmt.task_framework import Task
import qmt.geometry.freecad as cad
import copy

class GeometryTask(Task):

    def __init__(self,options=None,name='geometry_task'):
        super(GeometryTask, self).__init__([], options, name)

    def _solve_instance(self,input_result_list,current_options):
        return current_options


class FreeCADTask(GeometryTask):

    def __init__(self, options=None, name='freecad_task'):
        super(FreeCADTask, self).__init__(options, name)

    def _solve_instance(self, input_result_list, current_options):

        doc = cad.FreeCAD.newDocument('instance')
        if 'parts' in current_options:  # TODO: parts = dict{ 'part1': 3DPart, ... }
            pass

        if 'filepath' in current_options:
            doc.load(current_options['filepath'])
        elif 'document' in current_options:
            for obj in current_options['document'].Objects:
                print("+ " + obj.Name)
                doc.copyObject(obj, False)  # don't deep copy dependencies
        else:
            raise ValueError("No FreeCAD document available in FreeCADTask")

        # extend params dictionary to generic parts schema
        fcdict = {key:(value, 'freeCAD') for (key,value) in current_options['params'].items()}

        cad.fileIO.updateParams(doc, fcdict)
        return doc
