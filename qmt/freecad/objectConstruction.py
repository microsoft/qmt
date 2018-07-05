# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

###
### Functions that perform composite executions based on json file contents
###

import FreeCAD
import Draft

import numpy as np
# import qmt.freecad
from six import iteritems

from qmt.freecad import extrude, copy, delete, genUnion, getBB, \
    makeBB, splitSketch, makeHexFace, extendSketch, exportCAD, exportMeshed, updateParams,\
    deepRemove, findSegments, extrudeBetween, centerObjects, \
    intersect, checkOverlap, subtract, getModel, crossSection, findEdgeCycles, draftOffset


def buildWire(sketch, zBottom, width, faceOverride=None, offset=0.0):
    ''' Given a line segment, build a nanowire of given cross-sectional width
        with a bottom location at zBottom. Offset produces an offset with a specified
        offset.
    '''
    doc = FreeCAD.ActiveDocument
    if faceOverride is None:
        face = makeHexFace(sketch, zBottom - offset, width + 2 * offset)
    else:
        face = faceOverride
    sketchForSweep = extendSketch(sketch, offset)
    mySweepTemp = doc.addObject('Part::Sweep', sketch.Name + '_wire')
    mySweepTemp.Sections = [face]
    mySweepTemp.Spine = sketchForSweep
    mySweepTemp.Solid = True
    doc.recompute()
    mySweep = copy(mySweepTemp)
    deepRemove(mySweepTemp)
    return mySweep


def buildAlShell(sketch, zBottom, width, verts, thickness, depoZone=None, etchZone=None,
                 offset=0.0):
    '''Builds a shell on a nanowire parameterized by sketch, zBottom, and width.
    Here, verts describes the vertices that are covered, and thickness describes
    the thickness of the shell. depoZone, if given, is extruded and intersected
    with the shell (for an etch). Note that offset here *is not* a real offset - 
    for simplicity we keep this a thin shell that lies cleanly on top of the
    bigger wire offset. There's no need to include the bottom portion since that's
    already taken up by the wire.
    '''
    lineSegments = findSegments(sketch)[0]
    x0, y0, z0 = lineSegments[0]
    x1, y1, z1 = lineSegments[1]
    dx = x1 - x0
    dy = y1 - y0
    rAxis = np.array([-dy, dx, 0])
    rAxis /= np.sqrt(np.sum(rAxis ** 2))  # axis perpendicular to the wire in the xy plane
    zAxis = np.array([0, 0, 1.])
    doc = FreeCAD.ActiveDocument
    shellList = []
    for vert in verts:
        # Make the original wire (including an offset if applicable)
        originalWire = buildWire(sketch, zBottom, width, offset=offset)
        # Now make the shifted wire:
        angle = vert * np.pi / 3.
        dirVec = rAxis * np.cos(angle) + zAxis * np.sin(angle)
        shiftVec = (thickness) * dirVec
        transVec = FreeCAD.Vector(tuple(shiftVec))
        face = makeHexFace(sketch, zBottom - offset, width + 2 * offset)  # make the bigger face
        shiftedFace = Draft.move(face, transVec, copy=False)
        extendedSketch = extendSketch(sketch, offset)
        # The shell offset is handled manually since we are using faceOverride to
        # input a shifted starting face:
        shiftedWire = buildWire(extendedSketch, zBottom, width, faceOverride=shiftedFace)
        delete(extendedSketch)
        shellCut = doc.addObject("Part::Cut", sketch.Name + "_cut_" + str(vert))
        shellCut.Base = shiftedWire
        shellCut.Tool = originalWire
        doc.recompute()
        shell = Draft.move(shellCut, FreeCAD.Vector(0., 0., 0.), copy=True)
        doc.recompute()
        delete(shellCut)
        delete(originalWire)
        delete(shiftedWire)
        shellList += [shell]
    if len(shellList) > 1:
        coatingUnion = doc.addObject("Part::MultiFuse", sketch.Name + "_coating")
        coatingUnion.Shapes = shellList
        doc.recompute()
        coatingUnionClone = copy(coatingUnion)
        doc.removeObject(coatingUnion.Name)
        for shell in shellList:
            doc.removeObject(shell.Name)
    elif len(shellList) == 1:
        coatingUnionClone = shellList[0]
    else:
        raise NameError(
            'Trying to build an empty Al shell. If no shell is desired, omit the AlVerts key from the json.')
    if (depoZone is None) and (etchZone is None):
        return coatingUnionClone

    elif depoZone is not None:
        coatingBB = getBB(coatingUnionClone)
        zMin = coatingBB[4];
        zMax = coatingBB[5]
        depoVol = extrudeBetween(depoZone, zMin, zMax)
        etchedCoatingUnionClone = intersect([depoVol, coatingUnionClone], consumeInputs=True)
        return etchedCoatingUnionClone
    else:  # etchZone instead
        coatingBB = getBB(coatingUnionClone)
        zMin = coatingBB[4];
        zMax = coatingBB[5]
        etchVol = extrudeBetween(etchZone, zMin, zMax)
        etchedCoatingUnionClone = subtract(coatingUnionClone, etchVol, consumeInputs=True)
        return etchedCoatingUnionClone


def makeSAG(sketch, zBot, zMid, zTop, tIn, tOut, offset=0.):
    doc = FreeCAD.ActiveDocument
    # First, compute the geometric quantities we will need:
    a = zTop - zMid  # height of the top part
    b = tOut + tIn  # width of one of the trianglular pieces of the top
    alpha = np.abs(np.arctan(a / np.float(b)))  # lower angle of the top part
    c = a + 2 * offset  # height of the top part including the offset
    d = c / np.tan(alpha)  # horizontal width of the trianglular part of the top after offset
    f = offset / np.sin(alpha)  # horizontal shift in the triangular part of the top after an offset
    
    sketchList = splitSketch(sketch)
    returnParts = []
    for tempSketch in sketchList:
        #TODO: right now, if we try to taper the top of the SAG wire to a point, this
        # breaks, since the offset of topSketch is empty. We should detect and handle this.
        # For now, just make sure that the wire has a small flat top.
        botSketch = draftOffset(tempSketch, offset)  # the base of the wire
        midSketch = draftOffset(tempSketch, f + d - tIn)  # the base of the cap
        topSketch = draftOffset(tempSketch, -tIn + f)  # the top of the cap
        delete(tempSketch)  # remove the copied sketch part
        # Make the bottom wire:
        rectPartTemp = extrude(botSketch, zMid - zBot)
        rectPart = copy(rectPartTemp, moveVec=(0., 0., zBot - offset))
        delete(rectPartTemp)
        # make the cap of the wire:
        topSketchTemp = copy(topSketch, moveVec=(0., 0., zTop - zMid + 2 * offset))
        capPartTemp = doc.addObject('Part::Loft', sketch.Name + '_cap')
        capPartTemp.Sections = [midSketch, topSketchTemp]
        capPartTemp.Solid = True
        doc.recompute()
        capPart = copy(capPartTemp, moveVec=(0., 0., zMid - offset))
        delete(capPartTemp)
        delete(topSketchTemp)
        delete(topSketch)
        delete(midSketch)
        delete(botSketch)
        returnParts += [capPart, rectPart]
    returnPart = genUnion(returnParts, consumeInputs=True)
    return returnPart


class modelBuilder:
    def __init__(self, passModel=None, debugMode=False):
        ''' Builds a model defined by the JSON input file.
        '''
        if passModel is None:
            self.model = getModel()
        else:
            self.model = passModel
        self.debugMode = debugMode
        self.doc = FreeCAD.ActiveDocument
        self._buildPartsDict = {}
        self.lithoSetup = False  # Has the litho setup routine been run?
        self.trash = []  # trash for garbage collection at the end
        # Update the FreeCAD model to reflect the current value of any model parameters:
        updateParams(passModel=self.model)

    def buildPart(self, partName):
        partDict = self.model.modelDict['3DParts'][partName]
        directive = partDict['directive']
        if directive == 'extrude':
            objs = self._build_extrude(partName)
        elif directive == 'wire':
            objs = self._build_wire(partName)
        elif directive == 'wireShell':
            objs = self._build_wire_shell(partName)
        elif directive == 'SAG':
            objs = self._build_SAG(partName)
        elif directive == 'lithography':
            objs = self._build_litho(partName)
        else:
            raise ValueError('Directive ' + directive + ' is not a recognized directive type.')
        self._buildPartsDict[partName] = objs
        for obj in objs:
            self.model.registerCadPart(partName, obj.Name, None)

    def exportBuiltParts(self, stepFileDir=None, stlFileDir=None):
        # Now that we are ready to export, we first want to merge all of the 
        # 3D renders corresponding to a single shape into one entity:
        totalObjsDict = {}
        for partName in self._buildPartsDict.keys():
            totalObjList = []
            totalFileNamesList = []
            totalPartNamesList = []
            objsList = self._buildPartsDict[partName]
            mergedObj = genUnion(objsList, consumeInputs=True)
            mergedObj.Label = partName
            totalObjsDict[partName] = mergedObj
        # Now that we have merged the objects, we want to center them  in the x-y 
        # plane so the distances aren't ridiculous:
        centerObjects(totalObjsDict.values())
        # Finally, we go through the dictionary and export:
        for partName in totalObjsDict.keys():
            obj = totalObjsDict[partName]
            objFCName = obj.Name
            if stepFileDir is not None:
                filePath = stepFileDir + '/' + partName + '.step'
                exportCAD(obj, filePath)
                self.model.registerCadPart(partName, objFCName, filePath, reset=True)
            if stlFileDir is not None:
                filePath = stlFileDir + '/' + partName + '.stl'
                exportMeshed(obj, filePath)

    def saveFreeCADState(self, fileName):
        ''' Save a copy of the freeCAD model and do garbage collection.
        '''
        self._collect_garbarge()
        FreeCAD.ActiveDocument.saveAs(fileName)

    def _build_extrude(self, partName):
        ''' Build an extrude part.
        '''
        partDict = self.model.modelDict['3DParts'][partName]
        assert partDict['directive'] == 'extrude'
        z0 = self._fetch_geo_param(partDict['z0'])
        deltaz = self._fetch_geo_param(partDict['thickness'])
        sketch = self.doc.getObject(partDict['fcName'])
        splitSketches = splitSketch(sketch)
        extParts = []
        for mySplitSketch in splitSketches:
            extPart = extrudeBetween(mySplitSketch, z0, z0 + deltaz)
            extPart.Label = partName
            extParts += [extPart]
            delete(mySplitSketch)
        return extParts

    def _build_wire(self, partName, offset=0.):
        ''' Build a wire part.
        '''
        partDict = self.model.modelDict['3DParts'][partName]
        assert partDict['directive'] == 'wire'
        zBottom = self._fetch_geo_param(partDict['z0'])
        width = self._fetch_geo_param(partDict['thickness'])
        sketch = self.doc.getObject(partDict['fcName'])
        wire = buildWire(sketch, zBottom, width, offset=offset)
        wire.Label = partName
        return [wire]

    def _build_wire_shell(self, partName, offset=0.):
        ''' Build a wire shell part.
        '''
        partDict = self.model.modelDict['3DParts'][partName]
        wirePartDict = self.model.modelDict['3DParts'][partDict['targetWire']]
        assert partDict['directive'] == 'wireShell'
        zBottom = self._fetch_geo_param(wirePartDict['z0'])
        width = self._fetch_geo_param(wirePartDict['thickness'])
        wireSketch = self.doc.getObject(wirePartDict['fcName'])
        shellVerts = partDict['shellVerts']
        thickness = self._fetch_geo_param(partDict['thickness'])
        depoZoneName = partDict['depoZone']
        etchZoneName = partDict['etchZone']
        if depoZoneName is not None:
            depoZone = self.doc.getObject(depoZoneName)
        else:
            depoZone = None
        if etchZoneName is not None:
            etchZone = self.doc.getObject(etchZoneName)
        else:
            etchZone = None
        shell = buildAlShell(wireSketch, zBottom, width, shellVerts, thickness, depoZone=depoZone,
                             etchZone=etchZone, offset=offset)
        shell.Label = partName
        return [shell]

    def _build_SAG(self, partName, offset=0.):
        partDict = self.model.modelDict['3DParts'][partName]
        assert partDict['directive'] == 'SAG'
        zBot = self._fetch_geo_param(partDict['z0'])
        zMid = self._fetch_geo_param(partDict['zMiddle'])
        zTop = self._fetch_geo_param(partDict['thickness']) + zBot
        tIn = self._fetch_geo_param(partDict['tIn'])
        tOut = self._fetch_geo_param(partDict['tOut'])
        sketch = self.doc.getObject(partDict['fcName'])
        SAG = makeSAG(sketch, zBot, zMid, zTop, tIn, tOut, offset=offset)
        SAG.Label = partName
        return [SAG]

    def _build_litho(self, partName):
        '''Build a lithography part.
        '''
        partDict = self.model.modelDict['3DParts'][partName]
        if not self.lithoSetup:
            self._initialize_lithography(fillShells=partDict['fillLitho'])
            self.lithoSetup = True
        assert partDict['directive'] == 'lithography'
        layerNum = partDict['layerNum']
        returnObjs = []
        for objID in self.lithoDict['layers'][layerNum]['objIDs']:
            if partName == self.lithoDict['layers'][layerNum]['objIDs'][objID]['partName']:
                returnObjs += [self._gen_G(layerNum, objID)]
        return returnObjs

    def _fetch_geo_param(self, param):
        ''' Fetch the numerical value of a geometric parameter, which might be
        either a string or a float.
        '''
        if type(param) is str or type(param) is unicode:
            returnParam = float(self.model.modelDict['geometricParams'][param][0])
        else:
            returnParam = param
        return returnParam

    def _gen_offset(self, obj, offsetVal):
        ''' Generates an offset non-destructively. 
        '''
        # First, we need to check if the object needs special treatment:
        treatment = 'standard'
        for partName in self.model.modelDict['3DParts'].keys():
            partDict = self.model.modelDict['3DParts'][partName]
            if obj.Name in partDict['fileNames']:
                treatment = partDict['directive']
                break
        if treatment == 'extrude' or treatment == 'lithography':
            treatment = 'standard'
        if treatment == 'standard':
            if offsetVal < 1e-5:  # Apparently the offset function is buggy for very small offsets...
                offsetDupe = copy(obj)
            else:
                offset = self.doc.addObject("Part::Offset")
                offset.Source = obj
                offset.Value = offsetVal
                offset.Mode = 0
                offset.Join = 2
                self.doc.recompute()
                offsetDupe = copy(offset)
                self.doc.recompute()
                delete(offset)
        elif treatment == 'wire':
            offsetDupe = self._build_wire(partName, offset=offsetVal)[0]
        elif treatment == 'wireShell':
            offsetDupe = self._build_wire_shell(partName, offset=offsetVal)[0]
        elif treatment == 'SAG':
            offsetDupe = self._build_SAG(partName, offset=offsetVal)[0]
        self.doc.recompute()
        return offsetDupe

    def _initialize_lithography(self, fillShells=True):
        self.fillShells = fillShells
        # The lithography step requires some infrastructure to track things 
        # throughout.
        self.lithoDict = {}  # dictionary containing objects for the lithography step
        self.lithoDict['layers'] = {}
        # Dictionary for containing the substrate. () indicates un-offset objects,
        # and subsequent tuples are offset by t_i for each index in the tuple.
        self.lithoDict['substrate'] = {(): []}
        # To start, we need to collect up all the lithography directives, and
        # organize them by layerNum and objectIDs within layers.   
        baseSubstratePartNames = []
        for partName in self.model.modelDict['3DParts'].keys():
            partDict = self.model.modelDict['3DParts'][partName]
            if 'lithography' == partDict['directive']:  # If this part is a litho step
                layerNum = partDict['layerNum']  # layerNum of this part
                # Add the layerNum to the layer dictionary:
                if layerNum not in self.lithoDict['layers']:
                    self.lithoDict['layers'][layerNum] = {'objIDs': {}}
                layerDict = self.lithoDict['layers'][layerNum]
                # Gennerate the base and thickness of the layer:
                layerBase = self._fetch_geo_param(partDict['z0'])
                layerThickness = self._fetch_geo_param(partDict['thickness'])
                # All parts within a given layer number are required to have
                # identical thickness and base, so check that:
                if 'base' in layerDict:
                    assert layerBase == layerDict['base']
                else:
                    layerDict['base'] = layerBase
                if 'thickness' in layerDict:
                    assert layerThickness == layerDict['thickness']
                else:
                    layerDict['thickness'] = layerThickness
                # A given part references a base sketch. However, we need to split
                # the sketch here into possibly disjoint sub-sketches to work
                # with them:
                sketch = self.doc.getObject(partDict['fcName'])
                splitSketches = splitSketch(sketch)
                for mySplitSketch in splitSketches:
                    objID = len(layerDict['objIDs'])
                    objDict = {}
                    objDict['partName'] = partName
                    objDict['sketch'] = mySplitSketch
                    self.trash += [mySplitSketch]
                    self.lithoDict['layers'][layerNum]['objIDs'][objID] = objDict
                # Add the base substrate to the appropriate dictionary
                baseSubstratePartNames += partDict['lithoBase']
        # Get rid of any duplicates:
        baseSubstratePartNames = list(set(baseSubstratePartNames))
        # Now convert the part names for the substrate into 3D freeCAD objects, which
        # should have already been rendered.
        for baseSubstratePartName in baseSubstratePartNames:
            for baseSubstrateObjName in self.model.modelDict['3DParts'][baseSubstratePartName][
                'fileNames'].keys():
                self.lithoDict['substrate'][()] += [self.doc.getObject(baseSubstrateObjName)]
        # Now that we have ordered the primitives, we need to compute a few
        # aux quantities that we will need. First, we compute the total bounding
        # box of the lithography procedure:
        thicknesses = []
        bases = []
        for layerNum in self.lithoDict['layers'].keys():
            thicknesses += [self.lithoDict['layers'][layerNum]['thickness']]
            bases += [self.lithoDict['layers'][layerNum]['base']]
        bottom = min(bases)
        totalThickness = sum(thicknesses)
        assert len(self.lithoDict['substrate'][
                       ()]) > 0  # Otherwise, we don't have a reference for the lateral BB
        substrateUnion = genUnion(self.lithoDict['substrate'][()],
                                  consumeInputs=False)  # total substrate
        BB = list(getBB(substrateUnion))  # bounding box
        BB[4] = min([bottom, BB[4]])
        BB[5] = max([BB[5] + totalThickness, bottom + totalThickness])
        BB = tuple(BB)
        constructionZone = makeBB(BB)  # box that encompases the whole domain.
        self.lithoDict['boundingBox'] = [BB, constructionZone]
        delete(substrateUnion)  # not needed for next steps
        delete(constructionZone)  # not needed for next steps
        # Next, we add two prisms for each sketch. The first, which we denote "B", 
        # is bounded by the base from the bottom and the layer thickness on the top. 
        # These serve as "stencils" that would be the deposited shape if no other.
        # objects got in the way. The second set of prisms, denoted "C", covers the 
        # base of the layer to the top of the entire domain box. This is used for 
        # forming the volumes occupied when substrate objects are offset and 
        # checking for overlaps.
        for layerNum in self.lithoDict['layers'].keys():
            base = self.lithoDict['layers'][layerNum]['base']
            thickness = self.lithoDict['layers'][layerNum]['thickness']
            for objID in self.lithoDict['layers'][layerNum]['objIDs']:
                sketch = self.lithoDict['layers'][layerNum]['objIDs'][objID]['sketch']
                B = extrudeBetween(sketch, base, base + thickness)
                C = extrudeBetween(sketch, base, BB[5])
                self.lithoDict['layers'][layerNum]['objIDs'][objID]['B'] = B
                self.lithoDict['layers'][layerNum]['objIDs'][objID]['C'] = C
                self.trash += [B]
                self.trash += [C]
                # In addition, add a hook for the HDict, which will contain the "H"
                # constructions for this object, but offset to thicknesses of various 
                # layers, according to the keys.
                self.lithoDict['layers'][layerNum]['objIDs'][objID]['HDict'] = {}

    def _screened_H_union_list(self, obj, m, j, offsetTuple, checkOffsetTuple):
        ''' Foremd the "screened union list" of obj with the layer m, objID j H object that has 
        been offset according to offsetTuple. The screened union list is defined by checking 
        first whether the object intersects with the components of the checkOffset version 
        of the H object. Then, for each component that would intersect, we return the a list
        of the offsetTuple version of the object.
        '''
        # First, we need to check to see if we need to compute either of the underlying H obj lists:
        HDict = self.lithoDict['layers'][m]['objIDs'][j]['HDict']
        # HDict stores a collection of H object component lists for each (layerNum,objID)
        # pair. The index of this dictionary is a tuple: () indicates no 
        # offset, while other indices indicate an offset by summing the thicknesses
        # from corresponding layers.        
        if checkOffsetTuple not in HDict:  # If we haven't computed this yet
            HDict[checkOffsetTuple] = self._H_offset(m, j, tList=list(
                checkOffsetTuple))  # list of H parts
            self.trash += HDict[checkOffsetTuple]
        if offsetTuple not in HDict:  # If we haven't computed this yet
            HDict[offsetTuple] = self._H_offset(m, j, tList=list(offsetTuple))  # list of H parts
            self.trash += HDict[offsetTuple]
        HObjCheckList = HDict[checkOffsetTuple]
        HObjList = HDict[offsetTuple]
        returnList = []
        for i, HObjPart in enumerate(HObjCheckList):
            if checkOverlap([obj, HObjPart]):  # if we need to include an overlap
                returnList += [HObjList[i]]
        return returnList

    def _screened_A_UnionList(self, obj, t, ti, offsetTuple, checkOffsetTuple):
        ''' Foremd the "screened union list" of obj with the substrate A that has 
        been offset according to offsetTuple.
        '''
        # First, we need to see if we have built the objects before:
        if checkOffsetTuple not in self.lithoDict['substrate']:
            self.lithoDict['substrate'][checkOffsetTuple] = []
            for A in self.lithoDict['substrate'][()]:
                AObj = self._gen_offset(A, t)
                self.trash += [AObj]
                self.lithoDict['substrate'][checkOffsetTuple] += [AObj]
        if offsetTuple not in self.lithoDict['substrate']:
            self.lithoDict['substrate'][offsetTuple] = []
            for A in self.lithoDict['substrate'][()]:
                AObj = self._gen_offset(A, t + ti)
                self.trash += [AObj]
                self.lithoDict['substrate'][offsetTuple] += [AObj]

        returnList = []
        for i, ACheck in enumerate(self.lithoDict['substrate'][checkOffsetTuple]):
            if checkOverlap([obj, ACheck]):
                returnList += [self.lithoDict['substrate'][offsetTuple][i]]
        return returnList

    def _H_offset(self, layerNum, objID, tList=[]):
        ''' For a given layerNum=n and ObjID=i, compute the deposited object
            H_{n,i}(t) = C_{n,i}(t) \cap [ B_{n,i}(t) \cup (\cup_{m<n;j} H_{m,j}(t_i+t)) \cup (\cup_k A_k(t_i + t))],
            where A_k is from the base substrate list. This is computed recursively. The list of integers
            tList determines the offset t; t = the sum of all layer thicknesses ti that appear
            in tList. For example, tList = [1,2,3] -> t = t1+t2+t3. 
            
            Note: this object is returned as a list of objects that need to be unioned together
            in order to form the full H.
        '''
        # This is a tuple that encodes the check offset t:        
        checkOffsetTuple = tuple(sorted(tList))
        # This is a tuple that encodes the total offset t_i+t:        
        offsetTuple = tuple(sorted(tList + [layerNum]))
        # First, check if we have to do anything:
        if checkOffsetTuple in self.lithoDict['layers'][layerNum]['objIDs'][objID]['HDict']:
            return self.lithoDict['layers'][layerNum]['objIDs'][objID]['HDict'][checkOffsetTuple]
        # First, compute t:
        t = 0.0
        for tIndex in tList:
            t += self.lithoDict['layers'][tIndex]['thickness']
        ti = self.lithoDict['layers'][layerNum]['thickness']  # thickness of this layer
        # Set the aux. thickness t:
        B = self.lithoDict['layers'][layerNum]['objIDs'][objID][
            'B']  # B prism for this layer & objID
        C = self.lithoDict['layers'][layerNum]['objIDs'][objID][
            'C']  # C prism for this layer & ObjID
        B_t = self._gen_offset(B, t)  # offset the B prism
        C_t = self._gen_offset(C, t)  # offset the C prism
        self.trash += [B_t]
        self.trash += [C_t]
        # Build up the substrate due to previously deposited gates
        HOffsetList = []
        for m in self.lithoDict['layers'].keys():
            if m < layerNum:  # then this is a lower layer
                for j in self.lithoDict['layers'][m]['objIDs'].keys():
                    HDict = self.lithoDict['layers'][m]['objIDs'][j]['HDict']
                    HOffsetList += self._screened_H_union_list(C_t, m, j, offsetTuple,
                                                               checkOffsetTuple)
                    # Next, build up the original substrate list:
        AOffsetList = []
        AOffsetList += self._screened_A_UnionList(C_t, t, ti, offsetTuple, checkOffsetTuple)
        unionList = HOffsetList + AOffsetList
        returnList = [B_t]
        for obj in unionList:
            intObj = intersect([C_t, obj])
            self.trash += [intObj]
            returnList += [intObj]
        self.lithoDict['layers'][layerNum]['objIDs'][objID]['HDict'][checkOffsetTuple] = returnList
        return returnList

    def _gen_U(self, layerNum, objID):
        ''' For a given layerNum and objID, compute the quantity:

            U_{n,i}(t) = (\cup_{m<n;j} G_{m,j}) \cup (\cup_{k} A_k),

            where the inner union terms are not included if their intersection
            with B_i is empty.
        '''
        B = self.lithoDict['layers'][layerNum]['objIDs'][objID][
            'B']  # B prism for this layer & objID
        GList = []
        for m in self.lithoDict['layers'].keys():
            if m < layerNum:  # then this is a lower layer
                for j in self.lithoDict['layers'][m].keys():
                    if 'G' not in self.lithoDict['layers'][layerNum]['objIDs'][objID]:
                        self._gen_G(m, j)
                    G = self.lithoDict['layers'][layerNum]['objIDs'][objID]['G']
                    if checkOverlap([B, G]):
                        GList += [G]
        AList = []
        for A in self.lithoDict['substrate'][()]:
            if checkOverlap([B, A]):
                AList += [A]
        unionList = GList + AList
        unionObj = genUnion(unionList, consumeInputs=False)
        return unionObj

    def _gen_G(self, layerNum, objID):
        ''' Generate the gate deposition for a given layerNum and objID.
        '''
        if 'G' not in self.lithoDict['layers'][layerNum]['objIDs'][objID]:
            if () not in self.lithoDict['layers'][layerNum]['objIDs'][objID]['HDict']:
                self.lithoDict['layers'][layerNum]['objIDs'][objID]['HDict'][()] = self._H_offset(
                    layerNum, objID)
            H = genUnion(self.lithoDict['layers'][layerNum]['objIDs'][objID]['HDict'][()],
                         consumeInputs=False)
            self.trash += [H]
            if self.fillShells:
                G = copy(H)
            else:
                U = self._gen_U(layerNum, objID)
                G = subtract(H, U)
                delete(U)
            self.lithoDict['layers'][layerNum]['objIDs'][objID]['G'] = G
        G = self.lithoDict['layers'][layerNum]['objIDs'][objID]['G']
        partName = self.lithoDict['layers'][layerNum]['objIDs'][objID]['partName']
        G.Label = partName
        return G

    def _collect_garbarge(self):
        ''' Delete all the objects in self.trash.
        '''
        for obj in self.trash:
            try:
                delete(obj)
            except:
                pass


def buildCrossSection(sliceInfo, passModel=None):
    ''' Render the 2D objects required for cross-sections
    '''
    if passModel is None:
        passModel = getModel()
    doc = FreeCAD.ActiveDocument

    sliceName = sliceInfo['sliceName']
    axis, distance = sliceInfo['axis'], sliceInfo['distance']
    sliceParts = {}
    for name, part in iteritems(passModel.modelDict['3DParts']):
        # loop over FreeCAD shapes corresponding to part
        polygons = {}
        for shapeName in part['fileNames'].keys():
            # slice the 3D part
            fcName = shapeName + '_section_' + sliceName
            partObj = doc.getObject(shapeName)
            section = crossSection(partObj, axis=axis, d=distance, name=fcName)
            # if len(section.Shape.Vertexes) == 0:
            #     continue

            # separate disjoint pieces
            segments, cycles = findEdgeCycles(section)
            for i, cycle in enumerate(cycles):
                points = [tuple(segments[idx, 0]) for idx in cycle]
                patchName = fcName
                patchName = '{}_{}'.format(shapeName, i)
                polygons[patchName] = points

        # store sliced part
        if polygons:
            slicePart = part.copy()
            slicePart['type'] = "domain"
            slicePart['3DPart'] = name
            slicePart['geometry'] = polygons
            sliceParts[name] = slicePart

    return sliceParts


def build2DGeo(passModel=None):
    ''' Construct the 2D geometry entities defined in the json file.
    '''
    # TODO: THIS FUNCTION NEEDS TO BE UPDATED AFTER modelRevision RESTRUCTURING!
    if passModel is None:
        myModel = getModel()
    else:
        myModel = passModel
    twoDObjs = {}
    doc = FreeCAD.ActiveDocument
    for fcName in myModel.modelDict['freeCADInfo']:
        keys = myModel.modelDict['freeCADInfo'][fcName].keys()
        if '2DObject' in keys:
            objType = '2DObject'
            objControlDict = myModel.modelDict['freeCADInfo'][fcName][objType]
            returnDict = {}
            returnDict.update(objControlDict['physicsProps'])
            returnDict['type'] = objControlDict['type']
            if objControlDict['type'] == 'boundary':
                points = [tuple(v.Point) for v in doc.getObject(fcName).Shape.Vertexes]
                twoDObjs[fcName] = (points, returnDict)
            else:
                lineSegments, cycles = findEdgeCycles(doc.getObject(fcName))
                for i, cycle in enumerate(cycles):
                    points = [tuple(lineSegments[idx, 0]) for idx in cycle]
                    name = fcName
                    if len(cycles) > 1:
                        name = '{}_{}'.format(name, i)
                    twoDObjs[name] = (points, returnDict)
    return twoDObjs
