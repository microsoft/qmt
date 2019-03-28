from qmt.tasks import build_3d_geometry
from qmt.data import Part3DData
import numpy as np
import os
import FreeCAD


def test_xsection(datadir):
    small1 = Part3DData(
        "small1",
        "Sketch001",
        "extrude",
        domain_type="dielectric",
        material="HfO2",
        z0=-2,
        thickness=2,
    )

    small2 = Part3DData(
        "small2",
        "Sketch002",
        "extrude",
        domain_type="dielectric",
        material="HfO2",
        z0=0,
        thickness=2,
    )

    smallv = Part3DData(
        "smallv", "Sketch001", "extrude", domain_type="virtual", z0=-1, thickness=2
    )

    big = Part3DData(
        "big",
        "Sketch",
        "extrude",
        domain_type="metal_gate",
        material="Au",
        boundary_condition={"voltage": 0.0},
        z0=-4,
        thickness=8,
    )

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
    small1 = Part3DData(
        "small1",
        "Sketch001",
        "extrude",
        domain_type="dielectric",
        material="HfO2",
        z0=-2,
        thickness=2,
    )

    big = Part3DData(
        "big",
        "Sketch",
        "extrude",
        domain_type="metal_gate",
        material="Au",
        boundary_condition={"voltage": 0.0},
        z0=-4,
        thickness=8,
    )

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