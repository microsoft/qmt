# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

"""Testing data utilities."""

from qmt.data.data_utils import *


def test_store_serial(fix_testDir, fix_FCDoc):
    '''Test serialisation to memory.'''
    import FreeCAD
    # Serialise document
    obj = fix_FCDoc.addObject('App::FeaturePython', 'some_content')
    serial_data = store_serial(fix_FCDoc, lambda d, p: d.saveAs(p), 'fcstd')

    # Write to a file
    file_path = os.path.join(fix_testDir, 'test.fcstd')
    import codecs
    data = codecs.decode(serial_data.encode(), 'base64')
    with open(file_path, 'wb') as of:
        of.write(data)

    # Load back and check
    doc = FreeCAD.newDocument('instance')
    FreeCAD.setActiveDocument('instance')
    doc.load(file_path)

    assert doc.getObject('some_content') is not None
    FreeCAD.closeDocument('instance')
