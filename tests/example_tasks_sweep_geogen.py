import qmt.task_framework as qtf
from qmt.basic_tasks import FreeCADTask, MaterialsTask
from qmt.ms_tasks import PoissonTask
import qmt.geometry.freecad as fc
import numpy as np

tag1 = qtf.SweepTag('s1')
tag2 = qtf.SweepTag('v1')

geo_dict = {'part1':{'side length':tag1},'part2':{'side length': 10.}}
geo_task = FreeCADTask('example.FCStd', options=geo_dict)

mat_dict = {'part1':{'material':'InAs'},'part2':{'material': 'InP'}}
mat_task = MaterialsTask(options=mat_dict)

poisson_dict = {'part1':{'voltage':2.},'part2':{'voltage': tag2}}
poisson_task = PoissonTask(geo_task,mat_task,options=poisson_dict)

sweeps = [ {tag1:val,tag2:5.} for val in np.arange(2,10,2) ]
# ~ sweeps = [ {tag1:val1,tag2:val2} for val1 in np.arange(2,10,2) for val2 in [5.,6.] ]

sweep_man = qtf.SweepManager(sweeps)
# ~ sweep_man = qtf.SweepManager.construct_cartesian_product({})
sweep_man.run(poisson_task)

for res in poisson_task.result:
    print res
