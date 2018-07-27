import h5py
import dask

def save_relevant_data(generic_task, filename, dask_client, get_relevant_data, plot_type):
    #get_relevant_data is function that gets the bands
    sweep_holder = generic_task.computed_result #sweepholder containing list of futures
    data = map(lambda x: dask.delayed(get_relevant_data)(x),sweep_holder.futures)
    data = map(lambda x: dask_client.compute(x), data) #list of futures pointing to relevant data
    with h5py.File(filename,'w') as data_file:
        data_file.create_dataset('list_of_tags', data = map(lambda x: x.__str__(),sweep_holder.sweep.list_of_tags))
        points = []
        for point in sweep_holder.sweep.tagged_value_list:
            points += [[point[k] for k in sweep_holder.sweep.list_of_tags]]
        data_file.create_dataset('tagged_value_list', data = points)
        data_file.create_dataset('plot_type', data = plot_type)
        #loop through data, write data as it comes in
        job_finished = [False]*len(data)
        while not all(job_finished):
            for index, future in enumerate(data):
                if future.status == 'finished' and not job_finished[index]:
                    for k in future.result().keys():
                        data_file.create_dataset(str(index)+'_'+k, data = future.result()[k])
                    job_finished[index] = True
