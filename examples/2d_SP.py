#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
import qmt.task_framework as qtf
import qmt.basic_tasks as qbt
import qms.tasks as qmst
from qms.tasks.combine_for_fem.poisson import PoissonTask2D
from qms.tasks.combine_for_fem.thomas_fermi import ThomasFermi2D

triangleLeg = 50.#qtf.SweepTag('triangle leg length')
gateVoltage = qtf.SweepTag('gate voltage')

geo_dict = {'parts' : {}, 'edges' : {}}

bufferHeight = 0.5
substrateHeight =30.
deviceWidth=triangleLeg+50.
deviceHeight = np.sqrt(3.)/2.*triangleLeg+30.
bufferHeight = bufferHeight*np.sqrt(3.)/2.*triangleLeg
triangleHeight = np.sqrt(3.)/2.*triangleLeg
oxideHeight = 6.
AlThickness = 10.
deviceHeight = substrateHeight+triangleHeight+AlThickness*np.sqrt(3.)/2.+oxideHeight*np.sqrt(3.)

#points = []
#points += [map(lambda x: x*1.e0,[0.,0.])]
#points += [map(lambda x: x*1.e0,[deviceWidth,0.])]
#points += [map(lambda x: x*1.e0,[deviceWidth,deviceHeight])]
#points += [map(lambda x: x*1.e0,[0.,deviceHeight])]
#geo_dict['parts']['background'] = points

points = []
points += [map(lambda x: x*1.e0,[0.,0.])]
points += [map(lambda x: x*1.e0,[deviceWidth,0.])]
points += [map(lambda x: x*1.e0,[deviceWidth,substrateHeight])]
points += [map(lambda x: x*1.e0,[0.,substrateHeight])]
geo_dict['parts']['substrate_layer'] = points

points = []
triangleHeight = np.sqrt(3.)/2.*triangleLeg
points += [map(lambda x: x*1.e0,[deviceWidth/2.-triangleLeg/2.,substrateHeight])]
points += [map(lambda x: x*1.e0,[deviceWidth/2.+triangleLeg/2.,substrateHeight])]
points += [map(lambda x: x*1.e0,[deviceWidth/2.+triangleLeg/2.-bufferHeight/np.sqrt(3.),substrateHeight+bufferHeight])]
points += [map(lambda x: x*1.e0,[deviceWidth/2.-triangleLeg/2.+bufferHeight/np.sqrt(3.),substrateHeight+bufferHeight])]
geo_dict['parts']['buffer_layer'] = points

points = []
points += [map(lambda x: x*1.e0,[deviceWidth/2.+triangleLeg/2.-bufferHeight/np.sqrt(3.),substrateHeight+bufferHeight])]
points += [map(lambda x: x*1.e0,[deviceWidth/2.-triangleLeg/2.+bufferHeight/np.sqrt(3.),substrateHeight+bufferHeight])]
points += [map(lambda x: x*1.e0,[deviceWidth/2,substrateHeight+triangleHeight])]
geo_dict['parts']['wire_layer'] = points

points = []
points += [map(lambda x: x*1.e0,[deviceWidth/2.-triangleLeg/2.,substrateHeight])]
points += [map(lambda x: x*1.e0,[deviceWidth/2,substrateHeight+triangleHeight])]
points += [map(lambda x: x*1.e0,[deviceWidth/2-AlThickness/2.,substrateHeight+triangleHeight+AlThickness*np.sqrt(3.)/2.])]
points += [map(lambda x: x*1.e0,[deviceWidth/2.-triangleLeg/2.-AlThickness/np.sqrt(3.)*2.,substrateHeight])]
geo_dict['parts']['aluminum_layer'] = points

backGateHeight = 1.
points = []
points += [map(lambda x: x*1.e0,[0.,backGateHeight])]
points += [map(lambda x: x*1.e0,[deviceWidth,backGateHeight])]
geo_dict['edges']['back_gate'] = points

points = []
points += [map(lambda x: x*1.e0,[deviceWidth,substrateHeight])]
points += [map(lambda x: x*1.e0,[deviceWidth,substrateHeight+oxideHeight])]
points += [map(lambda x: x*1.e0,[deviceWidth/2.+triangleLeg/2.+oxideHeight/np.sqrt(3.),substrateHeight+oxideHeight])]
points += [map(lambda x: x*1.e0,[deviceWidth/2-AlThickness/2.,substrateHeight+triangleHeight+AlThickness*np.sqrt(3.)/2.+oxideHeight*np.sqrt(3.)])]
points += [map(lambda x: x*1.e0,[deviceWidth/2.-triangleLeg/2.-AlThickness/np.sqrt(3.)*2.-oxideHeight/np.sqrt(3.),substrateHeight+oxideHeight])]
points += [map(lambda x: x*1.e0,[0.,substrateHeight+oxideHeight])]
points += [map(lambda x: x*1.e0,[0.,substrateHeight])]
points += [map(lambda x: x*1.e0,[deviceWidth/2.-triangleLeg/2.-AlThickness/np.sqrt(3.)*2.,substrateHeight])]
points += [map(lambda x: x*1.e0,[deviceWidth/2-AlThickness/2.,substrateHeight+triangleHeight+AlThickness*np.sqrt(3.)/2.])]
points += [map(lambda x: x*1.e0,[deviceWidth/2.+triangleLeg/2.,substrateHeight])]
geo_dict['parts']['oxide_layer'] = points

points = []
points += [map(lambda x: x*1.e0,[deviceWidth,substrateHeight+oxideHeight])]
points += [map(lambda x: x*1.e0,[deviceWidth/2.+triangleLeg/2.+oxideHeight/np.sqrt(3.),substrateHeight+oxideHeight])]
points += [map(lambda x: x*1.e0,[deviceWidth/2-AlThickness/2.,substrateHeight+triangleHeight+AlThickness*np.sqrt(3.)/2.+oxideHeight*np.sqrt(3.)])]
points += [map(lambda x: x*1.e0,[deviceWidth/2.-triangleLeg/2.-AlThickness/np.sqrt(3.)*2.-oxideHeight/np.sqrt(3.),substrateHeight+oxideHeight])]
points += [map(lambda x: x*1.e0,[0.,substrateHeight+oxideHeight])]
geo_dict['edges']['top_gate'] = points

geo_task = qbt.Geometry2D(options=geo_dict)

mesh_dict = {'mesh_type' : 'finite difference','grid' : {'x' : {'step_size' : 1.e0}, 'y' : {'step_size' : 1.e0}}}

mesh_task = qmst.Mesh2D(geo_task, options = mesh_dict)

#poisson_dict = {}
#poisson_dict['materials'] = {'wire' : 'InAs'}
#poisson_dict['voltages'] = {'gate' : gateVoltage}

#poisson_task = PoissonTask2D(geo_task, mesh_task, poisson_dict)

tf_dict = {}
tf_dict['materials'] = {'background' : 'HfO2', 'substrate_layer' : 'InP', 'buffer_layer' : 'InP', 'wire_layer' : 'InAs', 'aluminum_layer' : 'Al', 'oxide_layer' : 'HfO2'}
tf_dict['voltages'] = {'top_gate' : gateVoltage, 'back_gate' : 0.}
tf_dict['material_properties'] = {}
tf_dict['material_properties']['Al'] = {'workFunction' : 4280.}

tf_task = ThomasFermi2D(geo_task, mesh_task, tf_dict)

#sweeps = [{triangleLeg : l, gateVoltage : v} for l in np.linspace(50.,150.,1) for v in np.linspace(1.,1.,1)]
sweeps = [{gateVoltage : 1.}]

sweep_man = qtf.SweepManager(sweeps)

result = sweep_man.run(tf_task)
print(tf_task.reduce())

