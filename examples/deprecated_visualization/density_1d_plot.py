import h5py

from qmt.visualization.plot_helpers import save_relevant_data


def generate_1d_density_plot(generic_task, filename, dask_client=None):
    if dask_client is None:
        dask_client = generic_task.sweep_manager.dask_client

    def _get_relevant_data(density_data):
        density_data._serialize()
        output = {}
        output['densities'] = density_data.content['densities']
        output['density_units'] = density_data.content['density_units']
        output['bands'] = density_data.content['bands']
        output['band_units'] = density_data.content['band_units']
        output['mesh'] = density_data.content['mesh']
        output['mesh_units'] = density_data.content['mesh_units']
        return output
    
    save_relevant_data(generic_task, filename, dask_client, _get_relevant_data, plot_type='1d_density_plot')


def _plot_1d_density(filename, hv):
    data_file = h5py.File(filename, 'r')
    kdims = data_file['list_of_tags']
    points = data_file['tagged_value_list']
    densities = [data_file[str(index)+'_densities'] for index in range(len(points))]
    density_units = [data_file[str(index)+'_density_units'][()] for index in range(len(points))]
    meshes = [data_file[str(index)+'_mesh'] for index in range(len(points))]
    mesh_units = [data_file[str(index)+'_mesh_units'][()] for index in range(len(points))]

    def density_plot(index):
        mesh_data = meshes[index]
        density_data = densities[index][0]
        return hv.Curve((mesh_data, density_data), kdims=[('x', 'x ('+str(mesh_units[index])+')'), ('density', 'density ('+str(density_units[index])+')')])
    curve_dict_2D = {tuple(points[index]): density_plot(index) for index in range(len(points))}
    return hv.util.Dynamic(hv.HoloMap(curve_dict_2D, kdims=list(kdims)))
