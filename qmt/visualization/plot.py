import h5py

from .density_1d_plot import _plot_1d_density


def plot(filename, hv):
    with h5py.File(filename, 'r') as data_file:
        file_type = data_file['plot_type'][()]
    if file_type == '1d_density_plot':
        return _plot_1d_density(filename, hv)
    else:
        raise NameError('Plot type not recognized: '+str(file_type))


