# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

"""Testing Task framework."""


def test_task_init(fix_task_env):
    input_task_example, gathered_task_example, post_processing_task_example = fix_task_env
    parts = {'a': [0., 1., 2.], 'b': [-3., 10., 2.], 'c': [20.]}
    input_data = input_task_example(parts)
    assert input_data == parts



# def test_run_daskless(fix_task_env):
#     import numpy as np
#
#     InputTaskExample, GatheredTaskExample, PostProcessingTaskExample = fix_task_env
#     input_opts = {'a': [0., 1., 2.], 'b': [-3., 10., 2.], 'c': [20.]}
#     gather_opts = {'numpoints': 20}
#     post_proc_opts = {'prefactor': 0.1}
#     input_task = InputTaskExample(options=input_opts)
#     gathered_task = GatheredTaskExample(input_task, options=gather_opts)
#     post_proc_task = PostProcessingTaskExample(input_task, gathered_task, options=post_proc_opts)
#     post_proc_task.run_daskless()
#
#     assert input_task.daskless_result == input_opts
#     gather_results = {}
#     for part in input_opts:
#         gather_results[part] = np.linspace(0.0, 1.0, gather_opts['numpoints'])
#     for part in gather_results:
#         assert np.all(gathered_task.daskless_result[part] == gather_results[part])
#     post_proc_results = 0.0
#     for part in input_opts:
#         post_proc_results += post_proc_opts['prefactor']*np.sum(input_opts[part])*\
#                                np.sum(gather_results[part])
#     assert(post_proc_task.daskless_result == post_proc_results)
#
#
# def test_run_dask(fix_task_env):
#     import numpy as np
#
#     InputTaskExample, GatheredTaskExample, PostProcessingTaskExample = fix_task_env
#     input_opts = {'a': [0., 1., 2.], 'b': [-3., 10., 2.], 'c': [20.]}
#     gather_opts = {'numpoints': 20}
#     post_proc_opts = {'prefactor': 0.1}
#     input_task = InputTaskExample(options=input_opts)
#     gathered_task = GatheredTaskExample(input_task, options=gather_opts)
#     post_proc_task = PostProcessingTaskExample(input_task, gathered_task, options=post_proc_opts)
#     sm = SweepManager.create_empty_sweep()
#     sm.run(post_proc_task)
#
#     dask_results_inputs = input_task.computed_result.get_completed_result(0)
#     dask_results_gathered = gathered_task.computed_result.result().get_result(0)
#     dask_results_post = post_proc_task.computed_result.get_completed_result(0)
#
#     assert dask_results_inputs == input_opts
#     gather_results = {}
#     for part in input_opts:
#         gather_results[part] = np.linspace(0.0, 1.0, gather_opts['numpoints'])
#     for part in gather_results:
#         assert np.all(dask_results_gathered[part] == gather_results[part])
#     post_proc_results = 0.0
#     for part in input_opts:
#         post_proc_results += post_proc_opts['prefactor']*np.sum(input_opts[part])*\
#                                np.sum(gather_results[part])
#     assert(dask_results_post == post_proc_results)
#
#
# def test_sweep(fix_task_env):
#     import numpy as np
#     from qmt.tasks import SweepTag, SweepManager
#
#     InputTaskExample, GatheredTaskExample, PostProcessingTaskExample = fix_task_env
#
#     tag1 = SweepTag('tag1')
#     tag2 = SweepTag('tag2')
#     tag3 = SweepTag('tag3')
#
#     input_opts = {'a': [tag1, 1., 2.], 'b': [-3., 10., 2.], 'c': [20.]}
#     gather_opts = {'numpoints': tag2}
#     post_proc_opts = {'prefactor': tag3}
#     input_task = InputTaskExample(options=input_opts)
#     gathered_task = GatheredTaskExample(input_task, options=gather_opts)
#     post_proc_task = PostProcessingTaskExample(input_task, gathered_task, options=post_proc_opts)
#
#     sm = SweepManager.construct_cartesian_product({tag1: np.linspace(0., 10., 5),
#                                                    tag2: range(2, 20),
#                                                    tag3: np.linspace(-1.0, 1., 7)
#                                                    })
#     sm.run(post_proc_task)
#     results = post_proc_task.computed_result.calculate_completed_results()
#     assert len(results) == 630 and results.get_result(3) == 0.0
#
#
# def test_docker_sweep(fix_task_env, fix_setup_docker):
#     import subprocess
#     from dask.distributed import Client
#     from qmt.tasks import SweepManager, SweepTag
#     import numpy as np
#
#     # First, set up the docker + dask cluster, which for now is just one scheduler and one worker
#     scheduler_command = ['dask-scheduler',
#                          '--port', '8781',
#                          '--bokeh-port', '8780']
#     worker_command = ['dask-worker',
#                       '--nthreads', '1',
#                       '--nprocs', '1',
#                       'localhost:8781']
#     docker_command = ['docker', 'run', '-d', '--network', 'host', 'qmt:master']
#     containers = []
#     try:
#         containers.append(subprocess.check_output(docker_command+scheduler_command).splitlines()[0])
#         containers.append(subprocess.check_output(docker_command+worker_command).splitlines()[0])
#         client = Client('localhost:8781')
#
#         # Next, perform the same sweep as before:
#         InputTaskExample, GatheredTaskExample, PostProcessingTaskExample = fix_task_env
#         tag1 = SweepTag('tag1')
#         tag2 = SweepTag('tag2')
#         tag3 = SweepTag('tag3')
#         input_opts = {'a': [tag1, 1., 2.], 'b': [-3., 10., 2.], 'c': [20.]}
#         gather_opts = {'numpoints': tag2}
#         post_proc_opts = {'prefactor': tag3}
#         input_task = InputTaskExample(options=input_opts)
#         gathered_task = GatheredTaskExample(input_task, options=gather_opts)
#         post_proc_task = PostProcessingTaskExample(input_task, gathered_task, options=post_proc_opts)
#
#         sm = SweepManager.construct_cartesian_product({tag1: np.linspace(0., 10., 3),
#                                                        tag2: range(1, 3),
#                                                        tag3: np.linspace(-1.0, 1., 4)
#                                                        }, dask_client=client)
#         sm.run(post_proc_task)
#         results = post_proc_task.computed_result.calculate_completed_results()
#         assert len(results) == 24 and results.get_result(3) == 0.0
#     finally:
#         # Clean up the docker containers
#         for c in containers:
#             subprocess.check_output(['docker', 'kill', c])
