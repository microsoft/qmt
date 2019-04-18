# -*-coding: utf-8 -*-
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

"""General FreeCAD helper functions."""

import os
import sys
import contextlib
import shutil
import tempfile
import zipfile
from xml.etree import ElementTree
import FreeCAD


def delete(obj):
    """Delete an object by FreeCAD name.

    Parameters
    ----------
    obj : FreeCAD.App.Document
        A FreeCAD object.

    Returns
    -------
    None

    """
    doc = FreeCAD.ActiveDocument
    doc.removeObject(obj.Name)
    doc.recompute()


def _deepRemove_impl(obj):
    """Implementation helper for deepRemove.

    Parameters
    ----------
    obj : FreeCAD.App.Document
        A FreeCAD object.

    Returns
    -------
    None

    """
    for child in obj.OutList:
        _deepRemove_impl(child)
    FreeCAD.ActiveDocument.removeObject(obj.Name)


def deepRemove(obj=None, name=None, label=None):
    """Remove a targeted object and recursively delete all its sub-objects.

    Parameters
    ----------
    obj : FreeCAD.App.Document
        A FreeCAD object. (Default value = None)
    name : str
        (Default value = None)
    label : str
        (Default value = None)

    Returns
    -------
    None

    """
    doc = FreeCAD.ActiveDocument
    if obj is not None:
        pass
    elif name is not None:
        obj = doc.getObject(name)
    elif label is not None:
        obj = doc.getObjectsByLabel(label)[0]
    else:
        raise RuntimeError("No object selected!")
    _deepRemove_impl(obj)
    doc.recompute()


@contextlib.contextmanager
def silent_stdout():
    """Suppress standard output."""
    sys.stdout.flush()
    stored_py = sys.stdout
    stored_fileno = None
    try:
        stored_fileno = os.dup(sys.stdout.fileno())
    except:
        pass
    with open(os.devnull, "w") as devnull:
        sys.stdout = devnull  # for python stdout.write
        os.dup2(devnull.fileno(), 1)  # for library write to fileno 1
        try:
            yield
        finally:
            sys.stdout = stored_py
            if stored_fileno is not None:
                os.dup2(stored_fileno, 1)


def _remove_from_zip(zipfname, *filenames):  # pragma: no cover
    """Remove file names from zip archive.

    Parameters
    ----------
    zipfname : str
        The file name of the zip-file.
    *filenames : sequence of strings


    Returns
    -------
    None

    """
    tempdir = tempfile.mkdtemp()
    try:
        tempname = os.path.join(tempdir, "new.zip")
        with zipfile.ZipFile(zipfname, "r") as zipread:
            with zipfile.ZipFile(tempname, "w") as zipwrite:
                for item in zipread.infolist():
                    if item.filename not in filenames:
                        data = zipread.read(item.filename)
                        zipwrite.writestr(item, data)
        shutil.move(tempname, zipfname)
    finally:
        shutil.rmtree(tempdir)


def _replace_in_zip_fstr(zipfname, filename, content):  # pragma: no cover
    """Replace a file in a zip archive with some content string.

    Parameters
    ----------
    zipfname : str
        The file name of the zip-file.
    filename : str

    content :


    Returns
    -------
    None

    """
    _remove_from_zip(zipfname, filename)
    zfile = zipfile.ZipFile(zipfname, mode="a")
    zfile.writestr(filename, content)


def make_objects_visible(zipfname):  # pragma: no cover
    """Make objects visible in a fcstd file with GuiDocument.xml.

    Parameters
    ----------
    zipfname : str
        The file name of the zip-file.

    Returns
    -------
    None

    """
    zfile = zipfile.ZipFile(zipfname)
    gui_xml = zfile.read("GuiDocument.xml")
    guitree = ElementTree.fromstring(gui_xml)

    for viewp in guitree.getiterator(tag="ViewProvider"):
        for elem in viewp.getiterator(tag="Properties"):
            for prop in elem.getiterator(tag="Property"):
                if prop.attrib.get("name") == "Visibility":
                    for state in prop.getiterator(tag="Bool"):
                        state.set("value", "true")

    gui_xml = ElementTree.tostring(guitree).decode()
    _replace_in_zip_fstr(zipfname, "GuiDocument.xml", gui_xml)
