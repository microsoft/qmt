#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Landing script for Python 2.7 calls to FreeCAD."""


import os
import sys
import pickle

import qmt.geometry.freecad as cad


def main():
    """Fetch input data and dispatch instructions."""

    instruction = sys.argv[1]
    data = pickle.loads(''.join(sys.stdin.readlines()))
    doc = active_doc_from(data['current_options'])

    if instruction == 'build3d':
        print(pickle.dumps(build3d(data['current_options'])))
        # just for debugging:
        if not os.path.exists('tmp'):
            os.mkdirs('tmp')
        doc.saveAs("tmp/example_geogen_" + str(doc.modelParams.d1) + ".fcstd")

    if instruction == 'writeFCfile':
        pass

    if instruction == 'regionMap':
        pass


def build3d(opts):  # TODO: move to objectConstruction
    import qmt.geometry.freecad.objectConstruction as construct
    # extend params dictionary to original parts schema
    fcdict = {key: (value, 'freeCAD') for (key, value) in opts['params'].items()}
    cad.fileIO.updateParams(cad.FreeCAD.ActiveDocument, fcdict)
    for part in opts['parts']:
        construct.buildPart(part)
    # fill opts with serialised doc and parts
    #serialise opts
    return opts


def active_doc_from(opts):
    doc = cad.FreeCAD.newDocument('instance')
    cad.FreeCAD.setActiveDocument('instance')

    if 'filepath' in opts:
        doc.load(opts['filepath'])
    elif 'document' in opts:
        stored_doc = pickle.loads(opts['document'])
        for obj in stored_doc.Objects:
            doc.copyObject(obj, False)  # don't deep copy dependencies
    else:
        raise ValueError("No FreeCAD document available")

    return doc


if __name__ == '__main__':
    main()
