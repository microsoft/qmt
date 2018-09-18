# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

"""Testing Task framework."""

def test_task_init(fix_task_env):
    InputTaskExample, GatheredTaskExample, PostProcessingTaskExample = fix_task_env
    input_opts = {'a':[0.,1.,2.],'b':[-3.,10.,2.],'c':[20.]}
    input_task = InputTaskExample(options=input_opts)
    assert len(input_task.previous_tasks) == 0
    assert len(input_task.options) == 3

def test_run_daskless(fix_task_env):
    import numpy as np

    InputTaskExample, GatheredTaskExample, PostProcessingTaskExample = fix_task_env
    input_opts = {'a':[0.,1.,2.],'b':[-3.,10.,2.],'c':[20.]}
    gather_opts = {'numpoints':20}
    post_proc_opts = {'prefactor':0.1}
    input_task = InputTaskExample(options=input_opts)
    gathered_task = GatheredTaskExample(input_task,options=gather_opts)
    post_proc_task = PostProcessingTaskExample(input_task,gathered_task,options=post_proc_opts)
    post_proc_task.run_daskless()

    assert input_task.daskless_result == input_opts
    gather_results = {}
    for part in input_opts:
        gather_results[part] = np.linspace(0.0,1.0,gather_opts['numpoints'])
    for part in gather_results:
        assert np.all(gathered_task.daskless_result[part] == gather_results[part])
    post_proc_results = 0.0
    for part in input_opts:
        post_proc_results += post_proc_opts['prefactor']*np.sum(input_opts[part])*\
                               np.sum(gather_results[part])
    assert(post_proc_task.daskless_result == post_proc_results)