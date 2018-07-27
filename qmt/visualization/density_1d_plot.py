from qmt.visualization.plot_helpers import save_relevant_data

def generate_1d_density_plot(generic_task, filename, dask_client = None):
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
    
    save_relevant_data(generic_task, filename, dask_client, _get_relevant_data, plot_type = '1d_density_plot')


def _plot_1d_density(data):
    import Holoviews as hv
    def fm_modulation(tag_values):
        sampleInc = 1.0/sampleRate
        x = np.arange(0,length, sampleInc)
        y = np.sin(2*np.pi*f_carrier*x + mod_index*np.sin(2*np.pi*f_mod*x))
        return hv.Curve((x, y), 'position (nm)', 'Energy')
    
    f_carrier = np.linspace(20, 60, 3)
    f_mod = np.linspace(20, 100, 5)

    curve_dict = {tag_values: fm_modulation(tag_values) for fc in f_carrier for fm in f_mod}

    kdims = [hv.Dimension(('f_carrier', 'Carrier frequency'), default=40),
            hv.Dimension(('f_mod', 'Modulation frequency'), default=60)]
    holomap = hv.HoloMap(curve_dict, kdims=kdims)
