import h5py
import numpy as np

from qmt.visualization.plot_helpers import save_relevant_data


def generate_mobility_plots(
    generic_task, filename, x_axis_tag, x_axis_units, dask_client=None
):
    r"""
    This function takes as input a mobility task, a filename, the tag which is the x axis of the eventual plot,
    and the units of the x-axis as a string. It then saves all of the data relevant to this plot. 
    """
    if dask_client is None:
        dask_client = generic_task.sweep_manager.dask_client

    def _get_relevant_data(mobility_data):
        mobility_data._serialize()
        output = {}
        output["conductance"] = mobility_data.content["conductance"]
        output["conductance_units"] = mobility_data.content["conductance_units"]
        output["mobility"] = mobility_data.content["mobility"]
        output["mobility_units"] = mobility_data.content["mobility_units"]
        output["x_axis"] = str(x_axis_tag).encode("utf8")
        output["x_axis_units"] = str(x_axis_units).encode("utf8")
        return output

    save_relevant_data(
        generic_task,
        filename,
        dask_client,
        _get_relevant_data,
        plot_type="mobility_plots",
    )


def _plot_mobility(filename, hv):
    r"""
    This function is called by the qmt.visualizer.plot function - it is responsible for generating the
    Holoviews plots
    """
    # First, read in the relevant data
    data_file = h5py.File(filename, "r")
    kdims = list(data_file["list_of_tags"])
    points = data_file["tagged_value_list"]
    conductance = [
        data_file[str(index) + "_conductance"].value for index in range(len(points))
    ]
    conductance_units = [
        data_file[str(index) + "_conductance_units"].value
        for index in range(len(points))
    ]
    mobility = [
        data_file[str(index) + "_mobility"].value for index in range(len(points))
    ]
    mobility_units = [
        data_file[str(index) + "_mobility_units"].value for index in range(len(points))
    ]
    x_axis_label = data_file["0_x_axis"].value
    x_axis_units = data_file["0_x_axis_units"].value
    # This awful bit of code is designed to reorganize the data.
    # Each data point is saved separately in the data file
    # This strings together values that are the same except for their
    # "x-axis" value (e.g. different voltage, same Dit)
    new_points = []
    new_data = [[], [], []]
    x_axis_index = list(map(lambda x: x.encode("utf8"), kdims)).index(x_axis_label)
    for index, point in enumerate(points):
        current_axis_value = point[x_axis_index]
        point = list(np.delete(point, x_axis_index))
        try:
            index_in_new_points = new_points.index(point)
            new_data[0][index_in_new_points] += [current_axis_value]
            new_data[1][index_in_new_points] += [conductance[index]]
            new_data[2][index_in_new_points] += [mobility[index]]
        except ValueError:
            new_points += [point]
            new_data[0] += [[current_axis_value]]
            new_data[1] += [[conductance[index]]]
            new_data[2] += [[mobility[index]]]
    kdims.pop(x_axis_index)
    points = new_points
    x_axis = new_data[0]
    conductance = new_data[1]
    mobility = new_data[2]
    # Now that the data has been reorganized, plotting is straightforward.

    def mobility_plots(index):
        x_data = x_axis[index]
        y1_data = conductance[index]
        y2_data = mobility[index]
        return hv.Curve(
            (x_data, y1_data),
            kdims=[
                (
                    "x",
                    x_axis_label.decode("utf8")
                    + " ("
                    + x_axis_units.decode("utf8")
                    + ")",
                ),
                ("conductance", "conductance (" + str(conductance_units[index]) + ")"),
            ],
        ) + hv.Curve(
            (x_data, y2_data),
            kdims=[
                (
                    "x",
                    x_axis_label.decode("utf8")
                    + " ("
                    + x_axis_units.decode("utf8")
                    + ")",
                ),
                ("mobility", "mobility (" + str(mobility_units[index]) + ")"),
            ],
        )

    curve_dict_2D = {
        tuple(points[index]): mobility_plots(index) for index in range(len(points))
    }
    return hv.util.Dynamic(hv.HoloMap(curve_dict_2D, kdims=list(kdims)))
