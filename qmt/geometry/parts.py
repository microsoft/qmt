import pickle


class Part3D(object):
    def __init__(
            self, label, fc_name, directive, domain_type=None, material=None,
            z0=0, thickness=None, target_wire=None, shell_verts=None,
            depo_zone=None, etch_zone=None, z_middle=None, t_in=None, t_out=None,
            layer_num=None, litho_base=None,
            fill_litho=True, mesh_max_size=None, mesh_min_size=None, mesh_growth_rate=None,
            mesh_scale_vector=None, boundary_condition=None, subtract_list=None,
            ns=None, phi_nl=None, ds=None):
        """
        Add a geometric part to the model.
        :param str label: The descriptive name of this new part.
        :param str fc_name: The name of the 2D/3D freeCAD object that this is built from.
        :param str directive: The freeCAD directive is used to construct this part. Valid
                              options for this are:
                              extrude -- simple extrusion
                              wire -- hexagonal nanowire about a polyline
                              wire_shell -- shell coating a specified nanowire
                              sag -- SAG structure
                              lithography -- masked layer deposited on top
                              3d_shape -- just take the 3D shapre directly.
        :param str domain_type: The type of domain this part represents. Valid options are:
                                semiconductor -- region permitted to self-consistently accumulate
                                metal_gate -- an electrode
                                virtual -- a part just used for selection (ignores material)
                                dielectric -- no charge accumulation allowed
        :param str material: The material of the resulting part.
        :param float z0: The starting z coordinate. Required for extrude, wire,
                         SAG, and lithographydirectives.
        :param float thickness: The total thickness. Required for all directives.
                                On wireShell, this is interpreted as the layer thickness.
        :param str target_wire: Target wire directive for a coating directive.
        :param list shell_verts: Vertices to use when rendering the coating. Required
                                 for the shell directive.
        :param str depo_zone: FreeCAD sketch defining the (positive) mask for the deposition
                              of a wire coating. Note that only one of depoZone or etchZone may be used.
        :param str etch_zone: FreeCAD sketch defining the (negative) amsek for the deposition of a
                              wire coating. Note that only one of depoZone or etchZone may be used.
        :param float z_middle: The location for the "flare out" of the SAG directive.
        :param float t_in: The lateral distance from the 2D profile to the edge of the top bevel
                           for the SAG directive.
        :param float t_out: The lateral distance from the 2D profile to the furthest "flare out"
                            location for the SAG directive.
        :param int layer_num: The layer number used by the lithography directive. Lower numbers
                              go down first, with higher numbers deposited last.
        :param list litho_base: The base partNames to use for the lithography directive.
                                For multi-step lithography, the bases are just all merged,
                                so there is no need to list this more than once.
        :param bool fill_litho: If set to false, will attempt to hollow out lithography
                                steps by subtracting the base and subsequent lithography
                                layers, but this can sometimes fail in opencascade.
        :param float mesh_max_size: The maximum allowable mesh size for this part, in microns.
        :param float mesh_min_size: The minimum allowable mesh size for this part, in microns.
        :param float mesh_growth_rate: The maximum allowable mesh growth rate for this part.
        :param tuple mesh_scale_vector: 3D list with scaling factors for the mesh in
                                        x, y, z direction.
        :param dict boundary_condition: One or more boundary conditions, if applicable, of
                                        the form of a type -> value mapping. For example, this could be {'voltage':1.0} or,
                                        more explicitly, {'voltage': {'type': 'dirichlet', 'value': 1.0,'unit': 'V'}}.
        :param list subtract_list: A list of partNames that should be subtracted from the current
                                   part when forming the final 3D objects. This subtraction is carried out when boundary
                                   conditions are set.
        :param float ns: Volume charge density of a part, applicable to semiconductor and
                         dielectric parts. The units for this are 1/cm^3.
        :param float phi_nl: The neutral level for interface traps, measured in units of eV above
                             the valence band maximum (semiconductor only).
        :param float ds: Density of interface traps; units are 1/(cm^2*eV).
        """

        # Input validation
        if directive not in ['extrude', 'wire', 'wire_shell', 'SAG', 'lithography', '3d_shape']:
            raise NameError('Error - directive ' + directive + ' is not a valid directive!')
        if domain_type not in ['semiconductor', 'metal_gate', 'virtual', 'dielectric']:
            raise NameError('Error - domainType ' + domain_type + ' not valid!')
        if (etch_zone is not None) and (depo_zone is not None):
            raise NameError(
                'Error - etch_zone and depo_zone cannot both be set!')

        # Input storage
        self.label = label
        self.fc_name = fc_name
        self.directive = directive
        self.domain_type = domain_type
        self.material = material
        self.z0 = z0
        self.thickness = thickness
        self.target_wire = target_wire
        self.shell_verts = shell_verts
        self.depo_zone = depo_zone
        self.z_middle = z_middle
        self.t_in = t_in
        self.t_out = t_out
        self.layer_num = layer_num
        self.litho_base = [] if litho_base is None else litho_base
        self.fill_litho = fill_litho
        self.mesh_max_size = mesh_max_size
        self.mesh_min_size = mesh_min_size
        self.mesh_growth_rate = mesh_growth_rate
        self.mesh_scale_vector = mesh_scale_vector
        self.boundary_condition = boundary_condition
        self.subtract_list = [] if subtract_list is None else subtract_list
        self.ns = ns
        self.phi_nl = phi_nl
        self.ds = ds
        self.serial_stp = None # This gets set on geometry build


    def write_stp(self, file_path=None):
        """Write part geometry to a STEP file.

        Returns the STEP file path.
        """
        if file_path == None:
            file_path = self.label + '.stp'
        import codecs
        data = codecs.decode(self.serial_stp.encode(), 'base64')
        with open(file_path, 'wb') as of:
            of.write(data)
        return file_path
