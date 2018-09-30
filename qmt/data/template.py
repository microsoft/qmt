# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import h5py
from six import iteritems

class Data(object):
    def __init__(self):
        """
        Class for passing data between tasks.
        """
        self.content = {}  # storage for contents to serialize

    def save(self, azure_info=None, file_path=None):
        """
        Save the data to Azure or disk. Azure takes precedence over local disk if specified.
        :param azure_info: Key information for Azure store
        :param file_path: File path for an hdf5 file in local storage.
        """
        self._serialize()
        if azure_info is not None:
            raise NotImplementedError("Azure implementation not currently complete.")
        elif file_path is not None:
            with h5py.File(file_path, 'w') as store:
                for dataset in self.content:
                    store.create_dataset(dataset, data=self.content[dataset])
        else:
            raise ValueError("No file given for save.")

    def load(self, azure_info=None, file_path=None):
        """
        Load the data from Azure or disk. Azure takes precedence over local disk if specified.
        :param azure_info: Key information for Azure store
        :param file_path: File path for an hdf5 file in local storage.
        """
        if azure_info is not None:
            raise NotImplementedError("Azure implementation not currently complete.")
        elif file_path is not None:
            with h5py.File(file_path, 'r') as store:
                for dataset in store.keys():
                    self.content[dataset] = store.get(dataset).value
            self._deserialize()
        else:
            raise ValueError("No file given for load.")

    def _serialize_unit(self, unit_instance):
        """
        Serializes a unit instance (e.g. units.meV -> 'meV')
        :param unit_instance: An instance of a unit (e.g. units.meV)
        """
        from qmt.physics_constants import units
        for k,v in iteritems(units.__dict__):
            if v==unit_instance:
                return k

    def _deserialize_unit(self, unit_string):
        """
        De-serializes a unit instance (e.g. 'meV' -> units.meV)
        :param unit_string: String corresponding with unit (e.g. 'meV')
        """
        from qmt.physics_constants import units
        return units.__dict__[unit_string]
