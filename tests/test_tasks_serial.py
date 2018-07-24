from qmt.basic_tasks import GeometryTask, MaterialsTask
from qmt.ms_tasks import PoissonTask

geo_dict = {'part1':{'side length':5.},'part2':{'side length': 10.}}
geo_task = GeometryTask(options=geo_dict)

mat_dict = {'part1':{'material':'InAs'},'part2':{'material': 'InP'}}
mat_task = MaterialsTask(options=mat_dict)

poisson_dict = {'part1':{'voltage':2.},'part2':{'voltage': 1.}}
poisson_task = PoissonTask(geo_task,mat_task,options=poisson_dict)

poisson_task.run()
print poisson_task.result
