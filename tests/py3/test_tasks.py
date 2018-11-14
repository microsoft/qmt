# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

"""Testing Task framework."""


def test_task_init(fix_task_env):
    input_task_example, gathered_task_example, post_processing_task_example = fix_task_env
    parts = {'a': [0., 1., 2.], 'b': [-3., 10., 2.], 'c': [20.]}
    input_data = input_task_example(parts)
    assert input_data == parts


def test_run_task_chain(fix_task_env):
    import numpy as np
    input_task_example, gathered_task_example, post_processing_task_example = fix_task_env
    parts = {'a': [0., 1., 2.], 'b': [-3., 10., 2.], 'c': [20.]}
    numpoints = 20
    prefactor = 0.1
    input_data = input_task_example(parts)
    gathered_data = gathered_task_example([input_data], [numpoints])[0]
    post_proc_data = post_processing_task_example(input_data, gathered_data, prefactor)

    assert input_data == parts
    gather_results = {}
    for part in parts:
        gather_results[part] = np.linspace(0.0, 1.0, numpoints)
    for part in gather_results:
        assert np.all(gathered_data[part] == gather_results[part])
    post_proc_results = 0.0
    for part in parts:
        post_proc_results += prefactor * np.sum(input_data[part]) * \
                             np.sum(gather_results[part])
    assert (post_proc_data == post_proc_results)


def test_run_dask(fix_task_env):
    import numpy as np
    from dask import delayed as dl
    from dask.distributed import Client
    dc = Client(processes=False)

    input_task_example, gathered_task_example, post_processing_task_example = fix_task_env
    parts = {'a': [0., 1., 2.], 'b': [-3., 10., 2.], 'c': [20.]}
    numpoints = 20
    prefactor = 0.1

    input_delayed = dl(input_task_example)(parts)
    gathered_delayed = dl(gathered_task_example, nout=1)([input_delayed], [numpoints])[0]
    post_proc_delayed = dl(post_processing_task_example)(input_delayed, gathered_delayed, prefactor)
    input_future = dc.compute(input_delayed)
    gathered_future = dc.compute(gathered_delayed)
    post_proc_future = dc.compute(post_proc_delayed)
    input_data = input_future.result()
    gathered_data = gathered_future.result()
    post_proc_data = post_proc_future.result()

    assert input_data == parts
    gather_results = {}
    for part in parts:
        gather_results[part] = np.linspace(0.0, 1.0, numpoints)
    for part in gather_results:
        assert np.all(gathered_data[part] == gather_results[part])
    post_proc_results = 0.0
    for part in parts:
        post_proc_results += prefactor * np.sum(input_data[part]) * \
                             np.sum(gather_results[part])
    assert (post_proc_data == post_proc_results)


def test_sweep(fix_task_env):
    import numpy as np
    input_task_example, gathered_task_example, post_processing_task_example = fix_task_env

    results = []
    collected_inputs = []
    for tag1 in np.linspace(0., 10., 5):
        parts = {'a': [tag1, 1., 2.], 'b': [-3., 10., 2.], 'c': [20.]}
        collected_inputs += [input_task_example(parts)]
    for tag2 in range(2, 20):
        num_grid_vec = tag2 * np.ones((len(collected_inputs),), dtype=np.int)
        collected_outputs = gathered_task_example(collected_inputs, num_grid_vec)
        for i, output in enumerate(collected_outputs):
            input_data = collected_inputs[i]
            for tag3 in np.linspace(-1.0, 1., 7):
                results += [post_processing_task_example(input_data, output, tag3)]

    assert len(results) == 630 and results[3] == 0.0


def test_docker_sweep(fix_task_env):
    import subprocess
    from dask import delayed as dl
    from dask.distributed import Client
    import numpy as np

    # First, set up the docker + dask cluster, which for now is just one scheduler and one worker
    scheduler_command = ['dask-scheduler',
                         '--port', '8781',
                         '--bokeh-port', '8780']
    worker_command = ['dask-worker',
                      '--nthreads', '1',
                      '--nprocs', '1',
                      'localhost:8781']
    docker_command = ['/usr/bin/docker', 'run', '-d', '--network', 'host', 'qmt_base:8d10817583210a43dcff368a910494058423383b']
    containers = []
    try:
        containers.append(
            subprocess.check_output(docker_command + scheduler_command).splitlines()[0])
        containers.append(subprocess.check_output(docker_command + worker_command).splitlines()[0])
        client = Client('localhost:8781')

        # Next, perform the same sweep as before:
        input_task_example, gathered_task_example, post_processing_task_example = fix_task_env

        delayeds = []
        collected_inputs = []
        for tag1 in np.linspace(0., 10., 3):
            parts = {'a': [tag1, 1., 2.], 'b': [-3., 10., 2.], 'c': [20.]}
            collected_inputs += [dl(input_task_example)(parts)]
        for tag2 in range(1, 3):
            num_grid_vec = tag2 * np.ones((len(collected_inputs),), dtype=np.int)
            collected_outputs = dl(gathered_task_example, nout=3)(collected_inputs, num_grid_vec)
            for i, output in enumerate(collected_outputs):
                input_data = collected_inputs[i]
                for tag3 in np.linspace(-1.0, 1., 4):
                    delayeds += [dl(post_processing_task_example)(input_data, output, tag3)]
        results = []
        for obj in delayeds:
            results += [client.compute(obj).result()]
        assert len(results) == 24 and results[3] == 0.0
    finally:
        # Clean up the docker containers
        for c in containers:
            subprocess.check_output(['docker', 'kill', c])
