import h5py
import dask
import time

# TODO refactor this into a special case of a more general reduce method
def save_relevant_data(generic_task, filename, dask_client, get_relevant_data, plot_type):
    sweep_holder = generic_task.computed_result #sweepholder containing list of futures
    data = list(map(lambda x: dask.delayed(get_relevant_data)(x),sweep_holder.futures))
    data = list(map(lambda x: dask_client.compute(x), data)) #list of futures pointing to relevant data
    with h5py.File(filename,'w') as data_file:
        used = set()
        unique_tags = [x for x in sweep_holder.sweep.list_of_tags if x not in used and (used.add(x) or True)]  
        print(str(unique_tags))
        dt = h5py.special_dtype(vlen=str)
        data_file.create_dataset('list_of_tags', data = list(map( lambda x :str(x).encode('utf8'),unique_tags)), dtype = dt)
        points = []
        for point in sweep_holder.sweep.tagged_value_list:
            points += [[point[k] for k in unique_tags]]
        data_file.create_dataset('tagged_value_list', data = points)
        data_file.create_dataset('plot_type', data = plot_type)
        #loop through data, write data as it comes in
        job_finished = [False]*len(sweep_holder.futures)
        while not all(job_finished):
            time.sleep(1.)
            for index, future in enumerate(data):
                if future.status == 'finished' and not job_finished[index]:
                    for k in future.result().keys():
                        data_file.create_dataset(str(index)+'_'+k, data = future.result()[k])
                    job_finished[index] = True
