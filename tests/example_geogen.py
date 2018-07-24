#!/usr/bin/env python
# -*- coding: utf-8 -*-

from qmt.basic_tasks import FreeCADTask
import qmt.task_framework as qtf
import qmt.geometry.freecad as cad
import ProfileLib.RegularPolygon
import numpy as np
import os

# Craft some geometry
# ~ vec = cad.FreeCAD.Vector
# ~ doc = cad.FreeCAD.newDocument('template')
# ~ doc.addObject('Spreadsheet::Sheet','modelParams')
# ~ sketch = doc.addObject('Sketcher::SketchObject', 'Sketch')
# ~ ProfileLib.RegularPolygon.makeRegularPolygon('Sketch', 6, vec(10,10,0), vec(120,120,0), False)
# ~ sketch.addConstraint(cad.sketchUtils.Sketcher.Constraint('Distance',2,1.))
# ~ sketch.setExpression('Constraints['+str(len(sketch.Constraints)-1)+']', u'modelParams.d1')

# Set up geometry task
tag_d1 = qtf.SweepTag('thickness')
# ~ freecad_dict = { 'document': doc, 'params': {'d1': tag_d1} }
freecad_dict = { 'filepath': 'example_geogen.fcstd', 'params': {'d1': tag1} }
geo_task = FreeCADTask(options=freecad_dict)

# Run sweeps
sweeps = [ {tag1:val} for val in np.arange(2,10,2) ]
qtf.SweepManager(sweeps).run(geo_task)

# Investigate results
if not os.path.exists('tmp'):
    os.mkdir('tmp')
for res in geo_task.result:
    for o in res.Objects:
        print o.Name + " for " + str(res.modelParams.d1)
    # ~ res.saveAs("tmp/example_geogen_"+str(res.modelParams.d1)+".fcstd")
    draft = cad.sketchUtils.Draft.makeShape2DView(res.Sketch)
    import importSVG
    importSVG.export([draft],u"tmp/example_geogen_"+str(res.modelParams.d1)+".svg")
