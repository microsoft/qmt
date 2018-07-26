import h5py


class Data(object):
    def __init__(self):
        """
        Class for passing data between tasks.
        """
        self.content = {}  # storage for contents to serialize

    def _serialize(self):
        """
        Method for stuffing the contents of a Data class into the self.content dictionary, which
        is then saved to Azure or disk.
        """
        raise NotImplementedError("_serialize should define how to get data into self.content.")

    def _deserialize(self):
        """
        Method for retrieving data from self.content, called after it is loaded from Azure or disk.
        """
        raise NotImplementedError("_serialize should define how to get data into self.content.")


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

    def _serialize_unit(unit_instance):
        """
        Serializes a unit instance (e.g. units.meV -> 'meV')
        :param unit_instance: An instance of a unit (e.g. units.meV)
        """
        from qmt import units
        for k,v in units.__dict__.iteritems():
            if v==unit_instance:
                return k

    def _deserialize_unit(unit_string):
        """
        De-serializes a unit instance (e.g. 'meV' -> units.meV)
        :param unit_string: String corresponding with unit (e.g. 'meV')
        """
        from qmt import units
       return units.__dict__[unit_string]
