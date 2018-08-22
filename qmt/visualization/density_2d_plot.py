from qmt.visualization.plot_helpers import save_relevant_data
import h5py
import numpy as np

def generate_2d_density_plot(generic_task, filename, dask_client = None):
    if dask_client is None:
        dask_client = generic_task.sweep_manager.dask_client
    def _get_relevant_data(density_data):
        density_data._serialize()
        output = {}
        output['rho'] = density_data.content['rho']
        output['rho_units'] = density_data.content['rho_units']
        output['mesh'] = density_data.content['mesh'].meshgrid()
        output['mesh_units'] = density_data.content['mesh_units']
        return output
    
    save_relevant_data(generic_task, filename, dask_client, _get_relevant_data, plot_type = '2d_density_plot')


def _plot_2d_density(filename, hv):
    data_file = h5py.File(filename, 'r')
    kdims = data_file['list_of_tags']
    points = data_file['tagged_value_list']
    densities = [data_file[str(index)+'_rho'] for index in range(len(points))]
    density_units = [data_file[str(index)+'_rho_units'][()] for index in range(len(points))]
    meshes = [data_file[str(index)+'_mesh'] for index in range(len(points))]
    mesh_units = [data_file[str(index)+'_mesh_units'][()] for index in range(len(points))]
    def density_plot(index):
        mesh_data = meshes[index]
        density_data = densities[index]
        xs = np.transpose(mesh_data[0])[0,:]
        ys = np.transpose(mesh_data[1])[:,0]
        im1 = hv.Image((xs, ys, (np.transpose(density_data)<-1.e16)*(abs(np.transpose(density_data)))),
                               kdims=[('x','x ('+str(mesh_units[index])+')'),('y','y ('+str(mesh_units[index])+')')],
                               vdims = [('density','electron density (e/'+str(density_units[index])+r'$^3$)')],group='electrons').options(clims=(1.e16,1.e19),logz=True)

        im2 = hv.Image((xs, ys, (np.transpose(density_data)>1.e16)*(abs(np.transpose(density_data)))),
                               kdims=[('x','x ('+str(mesh_units[index])+')'),('y','y ('+str(mesh_units[index])+')')],
                               vdims = [('density','hole density (e/'+str(density_units[index])+r'$^3$)')],group='holes').options(clims=(1.e16,1.e19),logz=True)
        hv.opts("Image.electrons (cmap='Reds') [colorbar=True,cbar_padding=0]")
        hv.opts("Image.holes (cmap='Blues') [colorbar=True,cbar_padding=0.1,title_format='Charge density']")
        return im1*im2
    plot_dict = {tuple(points[index]):density_plot(index) for index in range(len(points))}
    return hv.HoloMap(plot_dict, kdims=list(kdims))
