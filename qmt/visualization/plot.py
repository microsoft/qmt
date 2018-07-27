import h5py
from .1d_denisty_plot import _plot_1d_density
import dask


def plot(filename):
    with h5py.File(filename, 'r') as data_file:
        file_type = data_file['plot_type']
    if file_type == '1d_density_plot':
        _plot_1d_density(filename)
    else:
        raise NameError('Plot type not recognized: '+str(file_type))



def _save_relevant_data(generic_task, filename, dask_client, _get_relevant_data, plot_type):
    #get_relevant_data is function that gets the bands
    sweep_holder = generic_task.computed_result #sweepholder containing list of futures
    data = map(lambda x: dask.delayed(get_relevant_data)(x),sweep_holder.object_list)
    data = dask_client.persist(*data) #list of futures pointing to relevant data
    with h5py.File(filename,'w') as data_file:
        data_file.create_dataset('list_of_tags', data = sweep_holder.list_of_tags)
        data_file.create_dataset('tagged_value_list', data = sweep_holder.tagged_value_list)
        data_file.create_dataset('plot_type', data = plot_type)
        #loop through data, write data as it comes in
        job_finished = [False]*len(data)
        while not all(job_finished):
            for index, future in enumerate(data):
                if future.status == 'finished' and not already_done[index]:
                    data_file.create_dataset(str(index), data = future.result())
                    already_done[index] = True