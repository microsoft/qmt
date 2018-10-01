# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

"""Utility functions for dealing with data."""

import os
import uuid
import codecs
import h5py
import time
import dask
import dask.delayed


def serialised_file(path):
    '''Return a serialised blob of the contents of a given file path.'''
    with open(path, 'rb') as f:
        serial_data = codecs.encode(f.read(), 'base64').decode()
    return serial_data


def write_deserialised(serial_obj, path):
    '''Write a deserialised file from a serialised blob to a given file path.'''
    data = codecs.decode(serial_obj.encode(), 'base64')
    with open(path, 'wb') as f:
        f.write(data)


def store_serial(obj, save_fct, ext_format, scratch_dir=None):
    '''
    Return a serialised representation of
    save_fct(obj, scratch_dir/temporary_file.ext_format).
    The temporary file has a unique name.
    The parameter ext_format can be used for format distinction in some save_fct.
    '''
    if not scratch_dir:
        scratch_dir = os.curdir
    tmp_path = os.path.join(scratch_dir, uuid.uuid4().hex + '.' + ext_format)
    save_fct(obj, tmp_path)
    serial_data = serialised_file(tmp_path)
    os.remove(tmp_path)
    return serial_data


def load_serial(serial_obj, load_fct, ext_format=None, scratch_dir=None):
    '''
    Return the original object stored with store_serial.
    The load_fct must be a correct complement of the previously used store_fct.
    '''
    if not ext_format:
        ext_format = 'tmpdata'
    if not scratch_dir:
        scratch_dir = os.curdir
    tmp_path = os.path.join(scratch_dir, uuid.uuid4().hex + '.' + ext_format)
    write_deserialised(serial_obj, tmp_path)
    obj = load_fct(tmp_path)
    os.remove(tmp_path)
    return obj


def reduce_data(reduce_function, task, dask_client):
    """
    Given a task that has or will be been run, apply a reduce function to all of its outputs in
    dask. By specifying a custom reduce_function, the user is returning exactly what they want from
    a given run.
    :param function reduce_function: A function that takes the output data type of the supplied
    task and returns a dictionary of objects that can be stored in hdf5.
    :param Task task: The task that we would like to work on. Note that this function doesn't run
    the task, but this can be set up either before or after running.
    :param dask_client: The client we are using for the calculation
    :return sweep_vals,extracted_data: Returns a list of the sweep tags and a list of the futures
    corresponding to the data objects.
    """
    sweep_holder = task.computed_result  # List of futures that resolve to the data
    sweep_vals = task.computed_result.sweep.sweep_list  # List of the tag values
    # First, map the get_data method as a delayed function over the futures:
    mappped_futures = list(map(lambda x: dask.delayed(
        reduce_function)(x), sweep_holder.futures))
    # Next, send these futures to the client to perform the reduction remotely:
    # list of futures pointing to processed data
    extracted_data = list(
        map(lambda x: dask_client.compute(x), mappped_futures))
    return sweep_vals, extracted_data


def retrieve_data(extracted_data, dask_client):
    """
    Retrieves all of the data stored in a list of futures.
    :param extracted_data: List of futures we ant to retrieve.
    :param dask_client: Dask client we are using for the calculation.
    :return retrieved_data: The retrieved data in a list.
    """
    retrieved_data = dask_client.gather(extracted_data)
    return retrieved_data


def stream_data_to_file(extracted_data, filename, dask_client, sweep_vals=None):
    """
    Instead of simply retrieving all the data, we can stream it to a file on disk as the runs
    complete. The data are stored in an hdf5 file with a single level. Data entries are given by
    kesy of the form "index_paramval", where index is the numerical index of the result in the
    extracted_data list and paramval is the descriptive key for the datum of interest.
    :param extracted_data: List of futures we ant to retrieve.
    :param filename: File name for the local data store.
    :param dask_client: The client we are using for the calculation
    :param sweep_vals: Sweep point values to store along with the data. If None, then just uses
    an integer list.
    """
    from tqdm import tqdm
    if sweep_vals is None:
        sweep_vals = range(len(extracted_data))
    with h5py.File(filename, 'w') as data_file:
        # loop through data, write data as it comes in
        job_finished = [False]*len(extracted_data)
        pbar = tqdm(total=len(extracted_data))
        while not all(job_finished):
            time.sleep(1.)
            for index, future in enumerate(extracted_data):
                if future.status == 'finished' and not job_finished[index]:
                    for k in future.result().keys():
                        data_file.create_dataset(
                            str(index)+'_'+k, data=future.result()[k])
                    for k in sweep_vals[index].keys():
                        data_file.create_dataset(
                            str(index)+'_'+str(k), data=sweep_vals[index][k])
                    job_finished[index] = True
                    pbar.update(1)
