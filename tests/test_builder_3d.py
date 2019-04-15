from qmt.geometry import Geo3DBuilder


def test_builder_3d():
    builder = Geo3DBuilder()
    extrude = builder.extrusion("blah", None, "virtual", None, 1, 2)
    pass
