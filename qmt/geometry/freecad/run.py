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
        send_back(cad.objectConstruction.build3d(data['current_options']))

    elif instruction == 'writeFCfile':
        pass

    elif instruction == 'regionMap':
        pass

    else:
        raise ValueError('Not a registered FreeCAD QMT instruction')


def active_doc_from(opts):
    """Return a valid FreeCAD document given a QMT Geometry3D opts dict.

    This will load from the opts filepath or the serialised FCDoc.
    """
    doc = cad.FreeCAD.newDocument('instance')
    cad.FreeCAD.setActiveDocument('instance')

    if 'file_path' in opts:
        doc.load(opts['file_path'])
    elif 'document' in opts:
        stored_doc = pickle.loads(opts['document'])
        for obj in stored_doc.Objects:
            doc.copyObject(obj, False)  # don't deep copy dependencies
    else:
        raise ValueError("No FreeCAD document available")

    return doc


def send_back(data):
    sys.stdout.write('MAGICTQMTRANSFERBYTES'+pickle.dumps(data))


if __name__ == '__main__':
    main()
