from qmt.geometry import part_3d, build_3d_geometry, Geo2DData
import numpy as np
import os
import FreeCAD
from qmt.geometry.freecad.geomUtils import checkOverlap
from shapely.geometry import Polygon


def test_xsection(datadir):
    small1 = part_3d.ExtrudePart("small1", "Sketch001", z0=-2, thickness=2)

    small2 = part_3d.ExtrudePart("small2", "Sketch002", z0=0, thickness=2)

    smallv = part_3d.ExtrudePart(
        "smallv", "Sketch001", z0=-1, thickness=2, virtual=True
    )

    big = part_3d.ExtrudePart("big", "Sketch", z0=-4, thickness=8)

    input_parts = [small1, small2, big, smallv]
    file_path = os.path.join(datadir, "simple.FCStd")
    geo_data = build_3d_geometry(
        input_parts=input_parts,
        input_file=file_path,
        xsec_dict={"test_xsec": {"axis": (1, 0, 0), "distance": 0}},
    )

    cut_2d_geo_data = geo_data.xsec_to_2d("test_xsec")

    assert set(cut_2d_geo_data.parts["small1"].exterior.coords) == {
        (-5.0, -2.0),
        (-5.0, 0.0),
        (5.0, -2.0),
        (5.0, 0.0),
    }
    assert set(cut_2d_geo_data.parts["small2:0"].exterior.coords) == {
        (1.0, 0.0),
        (1.0, 2.0),
        (7.5, 0.0),
        (7.5, 2.0),
    }
    assert set(cut_2d_geo_data.parts["small2:1"].exterior.coords) == {
        (-7.5, 0.0),
        (-7.5, 2.0),
        (-1.0, 0.0),
        (-1.0, 2.0),
    }
    assert set(cut_2d_geo_data.parts["smallv"].exterior.coords) == {
        (-5.0, -1.0),
        (-5.0, 1.0),
        (5.0, -1.0),
        (5.0, 1.0),
    }
    assert set(cut_2d_geo_data.parts["big"].exterior.coords) == {
        (-10.0, -4.0),
        (-10.0, 4.0),
        (10.0, -4.0),
        (10.0, 4.0),
    }


def test_simple_xsection(datadir):
    small1 = part_3d.ExtrudePart("small1", "Sketch001", z0=-2, thickness=2)

    big = part_3d.ExtrudePart("big", "Sketch", z0=-4, thickness=8)

    input_parts = [small1, big]
    file_path = os.path.join(datadir, "simple.FCStd")
    geo_data = build_3d_geometry(
        input_parts=input_parts,
        input_file=file_path,
        xsec_dict={"test_xsec": {"axis": (1, 0, 0), "distance": 0}},
    )

    cut_2d_geo_data = geo_data.xsec_to_2d("test_xsec")

    assert set(cut_2d_geo_data.parts["small1"].exterior.coords) == {
        (-5.0, -2.0),
        (-5.0, 0.0),
        (5.0, -2.0),
        (5.0, 0.0),
    }
    assert set(cut_2d_geo_data.parts["big"].exterior.coords) == {
        (-10.0, -4.0),
        (-10.0, 4.0),
        (10.0, -4.0),
        (10.0, 4.0),
    }


def test_overlapping_parts(datadir):
    """
    This tests that two parts that were generated from lithography over a wire register as intersecting. Due to
    an OCC bug, FC 0.18 at one point would claim that these didn't intersect, resulting in geometry and meshing errors.
    """
    path = os.path.join(datadir, "intersection_test.FCStd")
    doc = FreeCAD.newDocument("instance")
    FreeCAD.setActiveDocument("instance")
    doc.load(path)
    shape_1 = doc.Objects[0]
    shape_2 = doc.Objects[1]
    assert checkOverlap([shape_1, shape_2])
    FreeCAD.closeDocument(doc.Name)


def test_crop():
    r"""
    The two shapes are:
     ____________
    |    ____    |
    |   /    \   |
    |  /      \  |
    | /        \ |
    |/__________\|
    The inner rectangle is the crop
     ____________
    |  ________  |
    | | /    \ | |
    | |/      \| |
    | /________\ |
    |/__________\|
    Which gives:
     ________ 
    | /    \ |
    |/      \|
    |________|
    """
    geo_data = Geo2DData()
    outline = Polygon([[0, 0], [0, 5], [10, 5], [10, 0]])
    inner = Polygon([[0, 0], [4, 4], [6, 4], [10, 0]])
    outer = outline.difference(inner)
    geo_data.add_part("inner", inner)
    geo_data.add_part("outer", outer)
    cropped_geo = geo_data.crop(x_min=1, x_max=9, y_min=1, y_max=4)
    assert set(cropped_geo.parts["inner"].exterior.coords) == {
        (1.0, 1.0),
        (4.0, 4.0),
        (6.0, 4.0),
        (9.0, 1.0),
    }
    assert set(cropped_geo.parts["outer:0"].coords) == {(4.0, 4.0), (6.0, 4.0)}
    assert set(cropped_geo.parts["outer:1"].exterior.coords) == {
        (1.0, 1.0),
        (1.0, 4.0),
        (4.0, 4.0),
    }
    assert set(cropped_geo.parts["outer:2"].exterior.coords) == {
        (6.0, 4.0),
        (9.0, 1.0),
        (9.0, 4.0),
    }
