# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

from __future__ import absolute_import, division, print_function

from pytest import approx

import qmt.physics_constants as pc

u = pc.units
m = pc.matrices
c = pc.constants


def test_units():
    assert pc.canonicalize(u.nm) == pc.canonicalize(u.cm / 1e7)
    assert pc.canonicalize(u.erg) == pc.canonicalize(
        u.g * u.cm ** 2 / u.s ** 2)
    assert pc.cancel(u.kg * u.cm / u.g / u.m) == 10.


def test_constants():
    assert pc.to_float(c.m_e / u.g) == approx(9.1 * 1e-28, abs=1e-30)
    assert pc.to_float(
        c.q_e / u.coulomb) == approx(1.60217662 * 1e-19, rel=1e-7)
    assert pc.to_float(c.mu_b / (u.eV / u.tesla)
                       ) == approx(5.788382 * 1e-5, rel=1e-6)
    assert pc.to_float(c.q_e ** 2 / c.hbar / c.c / c.epsilon0 /
                       4. / c.pi) == approx(1. / 137., abs=1e-4)


def test_matrices():
    assert m.s_x * m.s_x == m.s_0
    assert -1j * m.s_x * m.s_y * m.s_z == m.s_0
    assert m.s_x * m.s_y - m.s_y * m.s_x == 2 * 1j * m.s_z
    assert m.s_x * m.s_y + m.s_y * m.s_x == m.s_0 * 0
    assert m.s_x * m.s_x + m.s_x * m.s_x == 2 * m.s_0
    assert m.tau_zx * m.tau_zx == m.tau_00
