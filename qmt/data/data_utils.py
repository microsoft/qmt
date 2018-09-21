# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

"""Utility functions for dealing with data."""

import os
import uuid
import codecs


def serialised_file(path):
    '''Return a serialised blob of the contents of a given file path.'''
    with open(path, 'rb') as f:
        serial_data = codecs.encode(f.read(), 'base64').decode()
    return serial_data


def write_deserialised_file(serial_obj, path):
    '''Write a deserialised file from a serialised blob to a given file path.'''
    data = codecs.decode(serial_obj.encode(), 'base64')
    with open(path, 'wb') as f:
        f.write(data)


def store_serial(obj, save_fct, ext_format, scratch_dir=None):
    '''
    Return a serialised representation of
    save_fct(obj, scratch_dir/temporary_file.ext_format).
    The temporary file has a unique name.
    The parameter ext_format can be used for format distinction in some save_fct.
    '''
    if not scratch_dir:
        scratch_dir = os.curdir
    tmp_path = os.path.join(scratch_dir, uuid.uuid4().hex + '.' + ext_format)
    save_fct(obj, tmp_path)
    serial_data = serialised_file(tmp_path)
    os.remove(tmp_path)
    return serial_data


def load_serial(serial_obj, load_fct, ext_format=None, scratch_dir=None):
    '''
    Return the original object stored with store_serial.
    The load_fct must be a correct complement of the previously used store_fct.
    '''
    if not ext_format:
        ext_format = 'tmpdata'
    if not scratch_dir:
        scratch_dir = os.curdir
    tmp_path = os.path.join(scratch_dir, uuid.uuid4().hex + '.' + ext_format)
    write_deserialised_file(serial_obj, tmp_path)
    obj = load_fct(tmp_path)
    os.remove(tmp_path)
    return obj
