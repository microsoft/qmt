import qmt.task_framework as qtf
from qmt.basic_tasks import Geometry1D
from qmt.ms_tasks import PoissonTask

tag1 = qtf.SweepTag('s1')
tag2 = qtf.SweepTag('v1')   

geo_dict = {'part1': {'side length': tag1}, 'part2': {'side length': 10.}}
geo_task = Geometry1D(options=geo_dict)

mat_dict = {'part1': {'material': 'InAs'}, 'part2': {'material': 'InP'}}

poisson_dict = {'part1':{'voltage':tag2},'part2':{'voltage': 1.}}
poisson_task = PoissonTask(geo_task, options=poisson_dict)

sweeps = [{tag1: 1., tag2: 10.}, {tag1: 2., tag2: 10.}, {tag1: 1., tag2: 5.}, {tag1: 4., tag2: 3.}]

sweep_man = qtf.SweepManager(sweeps)

result = sweep_man.run(poisson_task)
for future in result.futures:
     print(future.result())
#print(map(dask.result,result.futures))