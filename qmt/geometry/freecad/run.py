#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Landing script for calls to FreeCAD."""

import pickle
import sys
import FreeCAD  # DON'T TOUCH: this must come before the fenics import further below


def main(instruction, data):
    """Fetch input data and dispatch instructions."""
    # WARNING: you must use send_back() to return data to the parent process.

    if instruction == 'build3d':
        from qmt.geometry.freecad.objectConstruction import build
        activate_doc_from(data['current_options'])
        geo_output = build(data['current_options'])
        return geo_output

    elif instruction == 'writeFCfile':
        pass

    else:
        raise ValueError('Not a registered FreeCAD QMT instruction')


def activate_doc_from(opts):
    """Activate a valid FreeCAD document from options.

    :param dict opts:   QMT Geometry3D opts dict.
    :return:            A FCStd doc loaded from the file_path or serialised document.
    """

    if 'serial_fcdoc' in opts:
        from qmt.data.geometry import Geo3DData
        data = Geo3DData()
        data.serial_fcdoc = opts['serial_fcdoc']
        doc = data.get_data('fcdoc')
    else:
        raise ValueError("No FreeCAD document available")

    return doc


def send_back(data):
    """Go away."""
    sys.stdout.write('MAGICQMTRANSFERBYTES' + pickle.dumps(data))
