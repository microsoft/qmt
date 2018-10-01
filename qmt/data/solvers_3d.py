# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

from collections import namedtuple

try:
    import kwant  # kwant import to stop fenics from segfaulting
except:
    pass
from qmt.data import store_serial, load_serial


class Fem3DData(object):
    def __init__(self, coordinates=None, coordinate_units=None, data=None, data_units=None, fenics_3d_data=None):
        self.coordinates = coordinates
        self.coordinate_units = coordinate_units
        self.data = data
        self.data_units = data_units
        self.fenics_3d_data = fenics_3d_data

    def get_data(self, data):
        if data == 'function':
            return deserialize_fenics_function(self.fenics_3d_data)
        else:
            print(
                'Unknown datatype {data} for get_data function'.format(data=data))


class SerialFenicsFunctionData(object):
    def __init__(self, serial_mesh, serial_function):
        self.serial_mesh = serial_mesh
        self.serial_function = serial_function


def serialize_fenics_function(mesh, fenics_function):
    import fenics as fn

    def _write_fenics_file(data, path):
        fn.File(path) << data

    serial_mesh = store_serial(mesh, _write_fenics_file, 'xml')
    serial_function = store_serial(fenics_function, _write_fenics_file, 'xml')

    return SerialFenicsFunctionData(serial_mesh, serial_function)


def deserialize_fenics_function(serial_function_data, element_type='P', element_degree=1):
    serial_mesh = serial_function_data.serial_mesh
    serial_fenics_function = serial_function_data.serial_function
    import fenics as fn
    mesh = load_serial(serial_mesh, fn.Mesh, ext_format='xml')

    def _load_fenics_function(path):
        V = fn.FunctionSpace(mesh, element_type, element_degree)
        return fn.Function(V, path)
    potential = load_serial(serial_fenics_function,
                            _load_fenics_function, ext_format='xml')
    return potential


TransportData = namedtuple('TransportData', ['conductance', 'smatrix'])
