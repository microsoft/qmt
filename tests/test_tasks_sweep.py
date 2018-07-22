from qmt.taskFramework import *

tag1 = SweepTag('s1')
tag2 = SweepTag('v1')

geo_dict = {'part1':{'side length':tag1},'part2':{'side length': 10.}}
geo_task = GeometryTask(geo_dict)

mat_dict = {'part1':{'material':'InAs'},'part2':{'material': 'InP'}}
mat_task = MaterialsTask(geo_task,mat_dict,inheret_tags_from=[])

poisson_dict = {'part1':{'voltage':2.},'part2':{'voltage': tag2}}
poisson_task = PoissonTask(geo_task,mat_task,poisson_dict)


sweeps = [{tag1:1.,tag2:10.},{tag1:2.,tag2:10.},{tag1:1.,tag2:5.},{tag1:4.,tag2:3.}]

sweep_man = SweepManager(sweeps)

sweep_man.run(poisson_task)
print poisson_task.result

