import pickle,os,shutil,codecs

from qmt import Materials
from qmt.data import Data

class Geo1DData(Data):
    def __init__(self):
        """
        Class for holding a 1D geometry specification.
        """
        super(Geo1DData, self).__init__()
        self.parts = {}
        self.materials_database = Materials()

    def get_material(self, part_name):
        return self.materials_database[self.parts[part_name].material]

    def get_material_mapping(self):
        return {name: self.get_material(name) for name in self.parts.keys()}

    def add_part(self, part_name, start_point, end_point, overwrite=False):
        """
        Add a part to this geometry.
        :param str part_name: Name of the part to create
        :param float start_point: Position of the start of the part
        :param float end_point: Position of the end of the part
        :param bool overwrite: Should we allow this to overwrite?
        """
        start, end = sorted([start_point, end_point])
        if (part_name in self.parts) and (not overwrite):
            raise ValueError("Attempted to overwrite the part " + part_name + ".")
        else:
            self.parts[part_name] = (start, end)

    def remove_part(self, part_name, ignore_if_absent=False):
        """
        Remove a part from this geometry.
        :param str part_name: Name of part to remove
        :param bool ignore_if_absent: Should we ignore an attempted removal if the part name
        is not found?
        """
        if part_name in self.parts:
            del self.parts[part_name]
        else:
            if not ignore_if_absent:
                raise ValueError(
                    "Attempted to remove the part " + part_name + ", which doesn't exist.")
            else:
                pass


class Geo2DData(Data):
    def __init__(self):
        """
        Class for holding a 2D geometry specification. This class holds two main dicts:
            - parts is a dictionary of shapely Polygon objects
            - edges is a dictionary of shapely LineString objects
        Parts are intended to be 2D domains, while edges are used for setting boundary conditions
        and surface conditions.
        """
        super(Geo2DData, self).__init__()
        self.parts = {}
        self.edges = {}
        self.build_order = []

    def add_part(self, part_name, part, overwrite=False):
        """
        Add a part to this geometry.
        :param str part_name: Name of the part to create
        :param Polygon part: Polygon object from shapely.geometry. This must be a valid Polygon.
        :param bool overwrite: Should we allow this to overwrite?
        """
        if not part.is_valid:
            raise ValueError("Part " + part_name + " is not a valid polygon.")
        if (part_name in self.parts) and (not overwrite):
            raise ValueError("Attempted to overwrite the part " + part_name + ".")
        else:
            self.parts[part_name] = part
            self.build_order += [part_name]

    def remove_part(self, part_name, ignore_if_absent=False):
        """
        Remove a part from this geometry.
        :param str part_name: Name of part to remove
        :param bool ignore_if_absent: Should we ignore an attempted removal if the part name
        is not found?
        """
        if part_name in self.parts:
            del self.parts[part_name]
            self.build_order.remove(part_name)
        else:
            if not ignore_if_absent:
                raise ValueError(
                    "Attempted to remove the part " + part_name + ", which doesn't exist.")
            else:
                pass

    def add_edge(self, edge_name, edge, overwrite=False):
        """
        Add an edge to this geometry.
        :param str edge_name: Name of the edge to create
        :param LineString edge: LineString object from shapely.geometry.
        :param bool overwrite: Should we allow this to overwrite?
        """
        if (edge_name in self.edges) and (not overwrite):
            raise ValueError("Attempted to overwrite the edge " + edge_name + ".")
        else:
            self.edges[edge_name] = edge
            self.build_order += [edge_name]

    def remove_edge(self, edge_name, ignore_if_absent=False):
        """
        Remove an edge from this geometry.
        :param str edge_name: Name of part to remove
        :param bool ignore_if_absent: Should we ignore an attempted removal if the part name
        is not found?
        """
        if edge_name in self.edges:
            del self.edges[edge_name]
            self.build_order.remove(edge_name)
        else:
            if not ignore_if_absent:
                raise ValueError(
                    "Attempted to remove the edge " + edge_name + ", which doesn't exist.")
            else:
                pass

class Geo3DData(Data):
    def __init__(self):
        """
        Class for a 3D geometry specification. It holds:
            - parts is a dict of Part3D objects, keyed by the label of each Part3D object.
            - build_order is a list of strings indicating the construction order.
        """
        super(Geo3DData, self).__init__()
        self.build_order = []
        self.parts = {}   # dict of parts in this geometry
        self.serial_fcdoc = None  # serialized FreeCAD document for this geometry
        self.serial_mesh = None # Holding container for the serialized xml of the meshed geometry
        self.serial_region_marker = None # Holding container for the serialized xml of the region
        # marker function
        self.fenics_ids = None # dictionary with part name keys mapping to fenics ids.

    def get_parts(self):
        return self.parts

    def add_part(self, part_name, part, overwrite=False):
        """
        Add a part to this geometry.
        :param str part_name: Name of the part to create
        :param Part3D part: Part3D object.
        :param bool overwrite: Should we allow this to overwrite?
        """
        if (part_name in self.parts) and (not overwrite):
            raise ValueError("Attempted to overwrite the part " + part_name + ".")
        else:
            self.parts[part_name] = part

    def remove_part(self, part_name, ignore_if_absent=False):
        """
        Remove a part from this geometry.
        :param str part_name: Name of part to remove
        :param bool ignore_if_absent: Should we ignore an attempted removal if the part name
        is not found?
        """
        if part_name in self.parts:
            del self.parts[part_name]
        else:
            if not ignore_if_absent:
                raise ValueError(
                    "Attempted to remove the part " + part_name + ", which doesn't exist.")
            else:
                pass

    def set_data(self,data_name,data,scratch_dir=None):
        """
        Set data to a serial format that is easily portable.
        :param str data_name: Options are:
                            "fcdoc", freeCAD document
                            "mesh", for a fenics mesh
                            "rmf", for a fenics region marker function
        :param data: The corresponding data that we would like to set.
        :param str file_path: File path for a scratch folder. Default is "tmp"; must be empty.
        """
        if scratch_dir is None:
            import uuid
            scratch_dir = 'tmp_'+str(uuid.uuid4())
        os.mkdir(scratch_dir)
        if data_name == 'fcdoc':
            tmp_path = os.path.join(scratch_dir,'tmp_doc_'+str(hash(data))+'.fcstd')
            data.saveAs(tmp_path)
        elif data_name == 'mesh' or data_name == 'rmf':
            import fenics as fn
            tmp_path = os.path.join(scratch_dir,'tmp_fenics_'+str(hash(data))+'.xml')
            fn.File(tmp_path) << data
        else:
            raise ValueError(str(data_name)+' was not a valid data_name.')
        with open(tmp_path, 'rb') as f:
            # The data is encoded in base64 then decoded as a string so that it can be passed
            # safely over subprocess pipes.
            serial_data = codecs.encode(f.read(), 'base64').decode()
        if data_name == 'fcdoc':
            self.serial_fcdoc = serial_data
        elif data_name == 'mesh':
            self.serial_mesh = serial_data
        elif data_name == 'rmf':
            self.serial_region_marker = serial_data
        shutil.rmtree(scratch_dir)

    def get_data(self,data_name, mesh=None, scratch_dir=None):
        """
        Get data from stored serial format.
        :param str data_name: Options are:
                            "fcdoc", freeCAD document
                            "mesh", for a fenics mesh
                            "rmf", for a fenics region marker function
        :param str file_path: File path for a scratch folder. Default is "tmp"; must be empty.
        :return data: The freeCAD document or fenics object that was stored.
        """
        if scratch_dir is None:
            import uuid
            scratch_dir = 'tmp_'+str(uuid.uuid4())
        os.mkdir(scratch_dir)
        if data_name == 'fcdoc':
            serial_data = self.serial_fcdoc
            tmp_path = os.path.join(scratch_dir,'tmp_doc_'+str(hash(serial_data))+'.fcstd')
        elif data_name == 'mesh' or data_name == 'rmf':
            if data_name == 'mesh':
                serial_data = self.serial_mesh
            else:
                serial_data = self.serial_region_marker
            tmp_path = os.path.join(scratch_dir, 'tmp_fenics_' + str(hash(serial_data)) + '.xml')
        else:
            raise ValueError(str(data_name) + ' was not a valid data_name.')
        decoded_data = codecs.decode(serial_data.encode(), 'base64')
        with open(tmp_path, 'wb') as of:
            of.write(decoded_data)
        if data_name == 'fcdoc':
            import FreeCAD
            data = FreeCAD.newDocument('instance')
            FreeCAD.setActiveDocument('instance')
            data.load(tmp_path)
        elif data_name == 'mesh':
            import fenics as fn
            data = fn.Mesh(tmp_path)
        else:
            import fenics as fn
            assert mesh, 'Need to specify a mesh on which to generate the region marker function'
            data = fn.CellFunction('size_t', mesh)
            fn.File(tmp_path) >> data
        shutil.rmtree(scratch_dir)
        return data

    def write_fcstd(self, file_path=None):
        """Write geometry to a fcstd file.

        Returns the fcstd file path.
        """
        if file_path == None:
            file_path = str(self.build_order) + '.fcstd'
        import codecs
        data = codecs.decode(self.serial_fcdoc.encode(), 'base64')
        with open(file_path, 'wb') as of:
            of.write(data)
        return file_path
