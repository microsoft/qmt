#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Example geometry sweeping in-memory."""

import os

import ProfileLib.RegularPolygon
import numpy as np
import qmt.task_framework as qtf
from qmt.basic_tasks import GeoFreeCAD

import qmt.geometry.freecad as cad

# Craft some geometry
vec = cad.FreeCAD.Vector
doc = cad.FreeCAD.newDocument('template')
doc.addObject('Spreadsheet::Sheet','modelParams')
sketch = doc.addObject('Sketcher::SketchObject', 'Sketch')
ProfileLib.RegularPolygon.makeRegularPolygon('Sketch', 6, vec(10,10,0), vec(120,120,0), False)
sketch.addConstraint(cad.sketchUtils.Sketcher.Constraint('Distance',2,1.))
sketch.setExpression('Constraints['+str(len(sketch.Constraints)-1)+']', u'modelParams.thickness_wire')

# Set up geometry task
tag_al = qtf.SweepTag('Al thickness')
tag_wire = qtf.SweepTag('Wire diameter')
freecad_dict = { 'document': doc, 'params': {'thickness_al': tag_al, 'thickness_wire': tag_wire} }
geo_task = GeoFreeCAD(options=freecad_dict)

sweeps = [ {tag_al: 1., tag_wire: val} for val in np.arange(2,10,2) ]
# ~ sweeps = [ {tag_al: val1, tag_wire: val2}
           # ~ for val1 in np.arange(2,10,2) for val2 in [5.,6.] ]
# ~ sweep_man = qtf.SweepManager.construct_cartesian_product({})
qtf.SweepManager(sweeps).run(geo_task)

# Investigate results
if not os.path.exists('tmp'):
    os.mkdir('tmp')
for res in geo_task.result:
    # ~ res.saveAs("example_geogen_"+str(res.modelParams.d1)+".fcstd")
    draft = cad.sketchUtils.Draft.makeShape2DView(res.Sketch)
    import importSVG
    importSVG.export([draft],u"tmp/example_geogen_"+str(res.modelParams.thickness_wire)+".svg")
