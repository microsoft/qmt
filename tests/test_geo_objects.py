from qmt.geometry import part_3d, build_3d_geometry
import numpy as np
import os
import FreeCAD


def test_xsection(datadir):
    small1 = part_3d.ExtrudeData("small1", "Sketch001", z0=-2, thickness=2)

    small2 = part_3d.ExtrudeData("small2", "Sketch002", z0=0, thickness=2)

    smallv = part_3d.ExtrudeData(
        "smallv", "Sketch001", z0=-1, thickness=2, virtual=True
    )

    big = part_3d.ExtrudeData("big", "Sketch", z0=-4, thickness=8)

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
    assert set(cut_2d_geo_data.parts["small2_0"].exterior.coords) == {
        (1.0, 0.0),
        (1.0, 2.0),
        (7.5, 0.0),
        (7.5, 2.0),
    }
    assert set(cut_2d_geo_data.parts["small2_1"].exterior.coords) == {
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
    small1 = part_3d.ExtrudeData("small1", "Sketch001", z0=-2, thickness=2)

    big = part_3d.ExtrudeData("big", "Sketch", z0=-4, thickness=8)

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
