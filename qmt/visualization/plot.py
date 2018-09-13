import h5py

from .density_1d_plot import _plot_1d_density
from .density_2d_plot import _plot_2d_density
from .mobility_plots import _plot_mobility

#do we need to import dask here?

def plot(filename, hv):
    with h5py.File(filename, 'r') as data_file:
        file_type = data_file['plot_type'][()]
    if file_type == '1d_density_plot':
        return _plot_1d_density(filename, hv)
    elif file_type == '2d_density_plot':
        return _plot_2d_density(filename, hv)
    elif file_type == 'mobility_plots':
        return _plot_mobility(filename, hv)
    else:
        raise NameError('Plot type not recognized: '+str(file_type))


