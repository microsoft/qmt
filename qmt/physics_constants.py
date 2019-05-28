# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import sympy.physics.units as spu
from scipy import constants as sc
from sympy.matrices import eye
from sympy.physics.matrices import msigma
from sympy.physics.quantum import TensorProduct as kron
from types import SimpleNamespace
import numpy as np
import deepdish


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
    """convert name of a unit into the corresponding sympy value

    Parameters
    ----------
    s :


    Returns
    -------


    """
    for u in dir(units):
        if u[:2] == "__":
            continue
        if u == s:
            return units.__dict__[u]
    # if s is a sympy object we assume it has already been parsed and pass it
    # through
    if hasattr(s, "subs"):
        return s
    raise RuntimeError(f"unknown unit: {s}")


constants = SimpleNamespace(
    hbar=spu.hbar,
    k_B=sc.physical_constants["Boltzmann constant in eV/K"][0] * units.eV / units.K,
    m_e=sc.physical_constants["electron mass"][0] * spu.kg,
    q_e=sc.physical_constants["elementary charge"][0] * units.coulomb,
    mu_b=sc.physical_constants["Bohr magneton in eV/T"][0] * units.eV / units.tesla,
    epsilon0=sc.epsilon_0 * spu.farad / spu.m,
    c=sc.physical_constants["speed of light in vacuum"][0] * spu.m / spu.s,
    pi=sc.pi,
)


def canonicalize(expr, base=None):
    """Convert all units to given base units (default: SI base units)

    Parameters
    ----------
    expr :

    base :
        (Default value = None)

    Returns
    -------


    """
    if base is None:
        base = (spu.m, spu.kg, spu.s, spu.A, spu.K, spu.mol, spu.cd)
    return spu.convert_to(expr, base)


def cancel(expr):
    """Cancel different units referring to the same dimension, e.g. cancel(kg/g) -> 1000

    Parameters
    ----------
    expr :


    Returns
    -------


    """
    return canonicalize(expr, 1)


def to_float(expr):
    """Convert sympy expression involving units to a float. Fails if expr is not
    dimensionless.

    Parameters
    ----------
    expr :


    Returns
    -------


    """
    return float(cancel(expr))


matrices = SimpleNamespace(s_0=eye(2), s_x=msigma(1), s_y=msigma(2), s_z=msigma(3))

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


class UArray(np.ndarray, deepdish.util.SaveableRegistry):
    """Extend a numpy array to have units information from sympy
    From https://docs.scipy.org/doc/numpy/user/basics.subclassing.html#simple-example-adding-an-extra-attribute-to-ndarray

    Pickle stuff copied from https://stackoverflow.com/questions/26598109/preserve-custom-attributes-when-pickling-subclass-of-numpy-array
    
    Deepdish save from https://deepdish.readthedocs.io/en/latest/io.html#class-instances
    
    Parameters
    ----------

    Returns
    -------


    """

    def __new__(cls, input_array, unit=None):
        # Input array is an already formed ndarray instance
        # We first cast to be our class type
        if input_array is None:
            return None
        obj = np.asarray(input_array).view(cls)
        # add the unit to the created instance
        obj.unit = unit
        obj.dtype = input_array.dtype
        # Finally, we must return the newly created object:
        return obj

    def __array_finalize__(self, obj):
        # see InfoArray.__array_finalize__ for comments
        if obj is None:
            return
        self.unit = getattr(obj, "unit", None)

    def __reduce__(self):
        # Get the parent's __reduce__ tuple
        pickled_state = super().__reduce__()
        # Create our own tuple to pass to __setstate__
        new_state = pickled_state[2] + (self.unit,)
        # Return a tuple that replaces the parent's __setstate__ tuple with our own
        return (pickled_state[0], pickled_state[1], new_state)

    def __setstate__(self, state):
        self.unit = state[-1]  # Set the unit attribute
        # Call the parent's __setstate__ with the other tuple elements.
        super().__setstate__(state[0:-1])

    @classmethod
    def load_from_dict(self, d):
        obj = UArray(d["array"], d["unit"])
        return obj

    def save_to_dict(self):
        return {"array": np.asarray(self), "unit": self.unit}


__all__ = ["units", "constants", "matrices", "parse_unit", "to_float", "UArray"]
