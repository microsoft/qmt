#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Landing script for Python 2.7 calls to FreeCAD."""


import os
import sys
import pickle


def main():
    """Fetch input data nd dispatch instructions."""

    data = pickle.loads(''.join(sys.stdin.readlines()))
    current_options = data['current_options']
    input_result_list = data['input_result_list']

    instruction = sys.argv[1]

    if instruction == 'updateParams':
        updateParams(current_options)

    if instruction == 'objectConstruction':
        pass

    if instruction == 'regionMap':
        pass


def updateParams(current_options):

    import hashlib
    file_hash = hashlib.sha256(str(current_options)).hexdigest()
    # ~ print(pickle.dumps(file_hash))

    print pickle.dumps("updated params for " + str(current_options))

    print(pickle.dumps('')) # prevent FreeCAD from polluting pipe
    import qmt.geometry.freecad as cad

    doc = cad.FreeCAD.newDocument('instance')
    cad.FreeCAD.setActiveDocument('instance')

    if 'filepath' in current_options:
        doc.load(current_options['filepath'])
    elif 'document' in current_options:
        for obj in current_options['document'].Objects:
            doc.copyObject(obj, False)  # don't deep copy dependencies
    else:
        raise ValueError("No FreeCAD document available")

    # extend params dictionary to generic parts schema
    fcdict = {key: (value, 'freeCAD') for (key, value) in current_options['params'].items()}

    cad.fileIO.updateParams(doc, fcdict)

    # Note: not atomic, yet we're at node level (shared fs?)... and mkdirs is lenient
    if not os.path.exists('tmp'):
        os.mkdirs('tmp')
    doc.saveAs("tmp/example_geogen_" + str(doc.modelParams.d1) + ".fcstd")
    # TODO: use file_hash


if __name__ == '__main__':
    main()
