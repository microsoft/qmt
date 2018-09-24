# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

from __future__ import absolute_import, division, print_function

import sympy.physics.units as spu
from scipy import constants as sc
from sympy.matrices import eye
from sympy.physics.matrices import msigma
from sympy.physics.quantum import TensorProduct as kron

try:
    from types import SimpleNamespace
except ImportError:
    # SimpleNamespace was introduced in python 3.3; in earlier versions use the
    # simple implementation from docs.python.org
    class SimpleNamespace:
        def __init__(self, **kwargs):
            self.__dict__.update(kwargs)

        def __repr__(self):
            keys = sorted(self.__dict__)
            items = ("{}={!r}".format(k, self.__dict__[k]) for k in keys)
            return "{}({})".format(type(self).__name__, ", ".join(items))

        def __eq__(self, other):
            return self.__dict__ == other.__dict__


units = SimpleNamespace(
    nm=spu.nm,
    um=spu.um,
    angstrom=spu.nm / 10,
    erg=spu.cm * spu.cm * spu.g / spu.s / spu.s,
    kg=spu.kg,
    g=spu.g,
    eV=spu.eV,
    meV=spu.eV / 1e3,
    microeV=spu.eV / 1e6,
    coulomb=spu.coulomb,
    tesla=spu.tesla,
    m=spu.m,
    s=spu.s,
    farad=spu.farad,
    cm=spu.cm,
    volt=spu.volt,
    V=spu.volt,
    K=spu.K,
    mK=spu.K / 1e3,
    amp=spu.coulomb / spu.s,
    nA=1e-9 * spu.coulomb / spu.s,
)


def parse_unit(s):
    """convert name of a unit into the corresponding sympy value"""
    for u in dir(units):
        if u[:2] == '__':
            continue
        if u == s:
            return units.__dict__[u]
    # if s is a sympy object we assume it has already been parsed and pass it
    # through
    if hasattr(s, 'subs'):
        return s
    raise RuntimeError('unknown unit: {}'.format(s))


constants = SimpleNamespace(
    hbar=spu.hbar,
    k_B=sc.physical_constants['Boltzmann constant in eV/K'][0] *
    units.eV / units.K,
    m_e=sc.physical_constants["electron mass"][0] * spu.kg,
    q_e=sc.physical_constants["elementary charge"][0] * units.coulomb,
    mu_b=sc.physical_constants["Bohr magneton in eV/T"][0] *
    units.eV / units.tesla,
    epsilon0=sc.epsilon_0 * spu.farad / spu.m,
    c=sc.physical_constants["speed of light in vacuum"][0] * spu.m / spu.s,
    pi=sc.pi
)

# Unify unit conversion between old and new units module
if "convert_to" in dir(spu):
    def canonicalize(expr, base=None):
        """Convert all units to given base units (default: SI base units)"""
        if base is None:
            base = (spu.m, spu.kg, spu.s, spu.A, spu.K, spu.mol, spu.cd)
        return spu.convert_to(expr, base)
else:
    def canonicalize(expr, base=None):
        return expr


def cancel(expr):
    """Cancel different units referring to the same dimension, e.g. cancel(kg/g) -> 1000"""
    return canonicalize(expr, 1)


def to_float(expr):
    """Convert sympy expression involving units to a float. Fails if expr is not dimensionless."""
    return float(cancel(expr))


matrices = SimpleNamespace(
    s_0=eye(2),
    s_x=msigma(1),
    s_y=msigma(2),
    s_z=msigma(3),
)

matrices.tau_00 = kron(matrices.s_0, matrices.s_0)
matrices.tau_0x = kron(matrices.s_0, matrices.s_x)
matrices.tau_0y = kron(matrices.s_0, matrices.s_y)
matrices.tau_0z = kron(matrices.s_0, matrices.s_z)

matrices.tau_x0 = kron(matrices.s_x, matrices.s_0)
matrices.tau_xx = kron(matrices.s_x, matrices.s_x)
matrices.tau_xy = kron(matrices.s_x, matrices.s_y)
matrices.tau_xz = kron(matrices.s_x, matrices.s_z)

matrices.tau_y0 = kron(matrices.s_y, matrices.s_0)
matrices.tau_yx = kron(matrices.s_y, matrices.s_x)
matrices.tau_yy = kron(matrices.s_y, matrices.s_y)
matrices.tau_yz = kron(matrices.s_y, matrices.s_z)

matrices.tau_z0 = kron(matrices.s_z, matrices.s_0)
matrices.tau_zx = kron(matrices.s_z, matrices.s_x)
matrices.tau_zy = kron(matrices.s_z, matrices.s_y)
matrices.tau_zz = kron(matrices.s_z, matrices.s_z)

__all__ = ["units", "constants", "matrices", "parse_unit", "to_float"]
