from qmt.geometry import Geom3DBuilder


def test_builder_3d():
    builder = Geom3DBuilder()
    extrude = builder.extrusion("blah", None, "virtual", None, 1, 2)
    pass
