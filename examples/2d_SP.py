#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
from qmt.tasks import SweepTag, SweepManager
from qmt.tasks.basic import Geometry2D
from qms.tasks.mesh import Mesh2D
from qms.tasks.poisson import Poisson2D
from qms.tasks.thomas_fermi import ThomasFermi2D
from qmt.visualization.density_2d_plot import generate_2d_density_plot

triangleLeg = SweepTag('triangle leg length')
gateVoltage = SweepTag('gate voltage')

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
#points += [[0.,0.]]
#points += [[deviceWidth,0.]]
#points += [[deviceWidth,deviceHeight]]
#points += [[0.,deviceHeight]]
#geo_dict['parts']['background'] = points

points = []
points += [[0.,0.]]
points += [[deviceWidth,0.]]
points += [[deviceWidth,substrateHeight]]
points += [[0.,substrateHeight]]
geo_dict['parts']['substrate_layer'] = points

points = []
triangleHeight = np.sqrt(3.)/2.*triangleLeg
points += [[deviceWidth/2.-triangleLeg/2.,substrateHeight]]
points += [[deviceWidth/2.+triangleLeg/2.,substrateHeight]]
points += [[deviceWidth/2.+triangleLeg/2.-bufferHeight/np.sqrt(3.),substrateHeight+bufferHeight]]
points += [[deviceWidth/2.-triangleLeg/2.+bufferHeight/np.sqrt(3.),substrateHeight+bufferHeight]]
geo_dict['parts']['buffer_layer'] = points

points = []
points += [[deviceWidth/2.+triangleLeg/2.-bufferHeight/np.sqrt(3.),substrateHeight+bufferHeight]]
points += [[deviceWidth/2.-triangleLeg/2.+bufferHeight/np.sqrt(3.),substrateHeight+bufferHeight]]
points += [[deviceWidth/2,substrateHeight+triangleHeight]]
geo_dict['parts']['wire_layer'] = points

points = []
points += [[deviceWidth/2.-triangleLeg/2.,substrateHeight]]
points += [[deviceWidth/2,substrateHeight+triangleHeight]]
points += [[deviceWidth/2-AlThickness/2.,substrateHeight+triangleHeight+AlThickness*np.sqrt(3.)/2.]]
points += [[deviceWidth/2.-triangleLeg/2.-AlThickness/np.sqrt(3.)*2.,substrateHeight]]
geo_dict['parts']['aluminum_layer'] = points

backGateHeight = 0.

points = []
points += [[0.,backGateHeight]]
points += [[deviceWidth,backGateHeight]]
geo_dict['edges']['back_gate'] = points

points = []
points += [[deviceWidth,substrateHeight]]
points += [[deviceWidth,substrateHeight+oxideHeight]]
points += [[deviceWidth/2.+triangleLeg/2.+oxideHeight/np.sqrt(3.),substrateHeight+oxideHeight]]
points += [[deviceWidth/2-AlThickness/2.,substrateHeight+triangleHeight+AlThickness*np.sqrt(3.)/2.+oxideHeight*np.sqrt(3.)]]
points += [[deviceWidth/2.-triangleLeg/2.-AlThickness/np.sqrt(3.)*2.-oxideHeight/np.sqrt(3.),substrateHeight+oxideHeight]]
points += [[0.,substrateHeight+oxideHeight]]
points += [[0.,substrateHeight]]
points += [[deviceWidth/2.-triangleLeg/2.-AlThickness/np.sqrt(3.)*2.,substrateHeight]]
points += [[deviceWidth/2-AlThickness/2.,substrateHeight+triangleHeight+AlThickness*np.sqrt(3.)/2.]]
points += [[deviceWidth/2.+triangleLeg/2.,substrateHeight]]
geo_dict['parts']['oxide_layer'] = points

points = []
points += [[deviceWidth,substrateHeight+oxideHeight]]
points += [[deviceWidth/2.+triangleLeg/2.+oxideHeight/np.sqrt(3.),substrateHeight+oxideHeight]]
points += [[deviceWidth/2-AlThickness/2.,substrateHeight+triangleHeight+AlThickness*np.sqrt(3.)/2.+oxideHeight*np.sqrt(3.)]]
points += [[deviceWidth/2.-triangleLeg/2.-AlThickness/np.sqrt(3.)*2.-oxideHeight/np.sqrt(3.),substrateHeight+oxideHeight]]
points += [[0.,substrateHeight+oxideHeight]]
geo_dict['edges']['top_gate'] = points

geo_task = Geometry2D(options=geo_dict)

mesh_dict = {'mesh_type' : 'finite difference','grid' : {'x' : {'step_size' : 1.e0}, 'y' : {'step_size' : 1.e0}}}

mesh_task = Mesh2D(geo_task, options = mesh_dict)

tf_dict = {}
tf_dict['materials'] = {'background' : 'HfO2', 'substrate_layer' : 'InP', 'buffer_layer' : 'InP', 'wire_layer' : 'InAs', 'aluminum_layer' : 'Al', 'oxide_layer' : 'HfO2'}
tf_dict['voltages'] = {'top_gate' : gateVoltage, 'back_gate' : gateVoltage, 'aluminum_layer' : 0.}
tf_dict['material_properties'] = {}

Al_WF = 4280.
InSb_EA = 4590.
InSb_BG = 235.
InAs_VBO = -590.
InAs_BG = 417.
Al_WF_level = 0.0-(Al_WF)
InAs_CB_level = 0.0-InSb_EA-InSb_BG+InAs_VBO+InAs_BG
WF_shift = 150.-(Al_WF_level-InAs_CB_level)

tf_dict['material_properties']['Al'] = {'workFunction' : Al_WF- WF_shift}

tf_task = ThomasFermi2D(geo_task, mesh_task, tf_dict)

sweeps = [{triangleLeg : l, gateVoltage : v} for l in np.linspace(50.,150.,1) for v in np.linspace(0.,-1.,5)]
#sweeps = [{gateVoltage : 1.}]

sweep_man = SweepManager(sweeps)

result = sweep_man.run(tf_task)

#print(result.result())

generate_2d_density_plot(tf_task, 'tf_density_test.h5')

