

class Part3D(object):
    def __init__(
        self, label, fcName, directive, domainType=None, material=None,
        z0=0, thickness=None, targetWire=None, shellVerts=None,
        depoZone=None, etchZone=None, zMiddle=None, tIn=None, tOut=None,
        layerNum=None, lithoBase=[],
        fillLitho=True, meshMaxSize=None, meshGrowthRate=None,
        meshScaleVector=None, boundaryCondition=None, subtractList=[],
        Ns=None, Phi_NL=None, Ds=None):
        """ Add a geometric part to the model.
        @param partName: The descriptive name of this new part.
        @param fcName: The name of the 2D freeCAD object that this is built from.
        @param directive: The freeCAD directive is used to construct this part.
                            Valid options for this are:
                                extrude -- simple extrusion
                                wire -- hexagonal nanowire about a polyline
                                wireShell -- shell coating a specified nanowire
                                SAG -- SAG structure
                                lithography -- masked layer deposited on top
        @param material:    The material of the resulting part
        @param domainType: The type of domain this part represents:
                            Valid options are:
                                semiconductor -- region permitted to self-consistently accumulate
                                metalGate -- an electrode
                                virtual -- a part just used for selection (ignores material)
                                dielectric -- no charge accumulation allowed
        @param z0:          The starting z coordinate. Required for extrude,
                            wire, SAG, and lithography directives.
        @param thickness:   The total thickness. Required for all
                            directives. On wireShell, this is interpreted
                            as the layer thickness.
        @param targetWire:  Target wire directive for a coating directive.
        @param shellVerts:  Vertices to use when rendering the coating. Required
                            for the shell directive.
        @param depoZone:    Sketch defining the (positive) mask for the deposition
                            of a wire coating. Note that only one of depoZone or
                            etchZone may be used
        @param etchZone:	Sketch defining the (negative) amsek for the depostion
                                            of a wire coating. Note that only one of depoZone or
                                            etchZone may be used.
        @param zMiddle:     The location for the "flare out" of the SAG directive.
        @param tIN:         The lateral distance from the 2D profile to the
                            edge of the top bevel for the SAG directive.
        @param tOut:        The lateral distance from the 2D profile to the
                            furtheset "flare out" location for the SAG directive.
        @param layerNum:    The layer (int) number used by the lithography directive.
                            Lower numbers go down first, with higher numbers
                            deposited last.
        @param lithoBase:   The base partNames to use for the lithography directive.
                            For multi-step lithography, the bases are just all merged,
                            so there is no need to list this more than once.
        @param fillLitho:   Bool, defaulting to true. If set to false, will attempt
                            to hollow out lithography steps by subtracting the base
                            and subsequent lithography layers, but this can sometimes
                            fail in opencascade. COMSOL takes care of this using
                            parasolid if left to True.
        @param meshMaxSize: The maximum allowable mesh size for this part, in microns.
        @param meshGrowthRate: The maximum allowable mesh growth rate for this part
        @param meshScaleVector: 3D list with scaling factors for the mesh in x, y, z direction
        @param boundaryCondition: One or more boundary conditions, if applicable, of the form of
                            a type -> value mapping. For example, this could be {'voltage':1.0}
                            or, more explicitly, {'voltage': {'type': 'dirichlet', 'value': 1.0,
                                                              'unit': 'V'}}.
        @param subtractList: A list of partNames that should be subtracted from the
                             current part when forming the final 3D objects. This
                             subtraction is carried out in 3D using the COMSOL parasolid
                             kernel or using shapely in 2D.
        @param Ns:           Volume charge density of a part, applicable to semiconductor
                             and dielectric parts. The units for this are 1/cm^3.
        @param Phi_NL:       The neutral level for interface traps, measured in units of
                             eV above the valence band maximum (semiconductor only).
        @param Ds:           Density of interface traps; units are 1/(cm^2*eV).
        """
        # Input validation
        # ~ if partName in self.modelDict['3DParts']:
            # ~ raise NameError('Error - partName ' + partName +' was duplicated!')
        if directive not in ['extrude', 'wire', 'wireShell', 'SAG', 'lithography']:
            raise NameError('Error - directive ' + directive + ' is not a valid directive!')
        if domainType not in ['semiconductor', 'metalGate', 'virtual', 'dielectric']:
            raise NameError('Error - domainType ' + domainType + ' not valid!')
        if (etchZone is not None) and (depoZone is not None):
            raise NameError(
                'Error - etchZone and depoZone cannot both be set!')

        # Input storage
        self.label = label
        self.fcName = fcName
        self.directive = directive
        self.domainType = domainType
        self.material = material
        self.z0 = z0
        self.thickness = thickness
        self.targetWire = targetWire
        self.shellVerts = shellVerts
        self.depoZone = depoZone
        self.zMiddle = zMiddle
        self.tIn = tIn
        self.tOut = tOut
        self.layerNum = layerNum
        self.lithoBase = lithoBase
        self.fillLitho = fillLitho
        self.meshMaxSize = meshMaxSize
        self.meshGrowthRate = meshGrowthRate
        self.meshScaleVector = meshScaleVector
        self.boundaryCondition = boundaryCondition
        self.subtractList = subtractList
        self.Ns = Ns
        self.Phi_NL = Phi_NL
        self.Ds = Ds
        # ~ self.step_pickle = pickle(load(filepath))

    def write_step():
        """Write part to a STEP file.

        Returns the STEP file path and a subtractlist.
        """
        file_path = self.label
        data = pickle.dumps(self.serialised_stepfile)
        with open(file_path, 'b') as of:
            of.write(data)
        # ~ return {file_path: ..., subtractlist: [label1, ...] }
