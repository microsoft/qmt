# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

from __future__ import absolute_import, division, print_function
from pytest import approx
import qmt.materials as materials


def test_band_offsets():
    """Test calculation of band positions and offsets."""
    matlib = materials.Materials()
    mat1 = matlib.find('InSb', eunit='eV')
    mat2 = matlib.find('InAs', eunit='eV')
    mat3 = matlib.find('GaAs', eunit='eV')
    assert matlib.conductionBandMinimum(mat1) - mat1['directBandGap'] == \
           approx(matlib.valenceBandMaximum(mat1))
    assert matlib.conductionBandMinimum(mat1) - matlib.conductionBandMinimum(mat2) == \
           approx(materials.conduction_band_offset(mat1, mat2))
    assert matlib.valenceBandMaximum(mat1) + mat1['directBandGap'] == \
           approx(matlib.conductionBandMinimum(mat1))
    assert matlib.valenceBandMaximum(mat1) - matlib.valenceBandMaximum(mat2) == \
           approx(materials.valence_band_offset(mat1, mat2))
    assert materials.conduction_band_offset(mat1, mat2) + \
           materials.conduction_band_offset(mat2, mat3) == \
           approx(materials.conduction_band_offset(mat1, mat3))
    assert materials.valence_band_offset(mat1, mat2) + \
           materials.valence_band_offset(mat2, mat3) == \
           approx(materials.valence_band_offset(mat1, mat3))


def test_bowing_parameters():
    """Test calculation of alloy band positions with bowing parameters."""
    matlib = materials.Materials()
    inas = matlib.find('InAs', eunit='meV')
    insb = matlib.find('InSb', eunit='meV')
    alloy = matlib.find('InAs80Sb20', eunit='meV')
    # band gap bowing for InAsSb is strong enough to push CBM in alloy below CBM in either binary
    assert matlib.conductionBandMinimum(alloy) < matlib.conductionBandMinimum(inas)
    assert matlib.conductionBandMinimum(inas) < matlib.conductionBandMinimum(insb)
    # check that we have bowing parameters for m_* and E_g, which are significant for this alloy
    bow = matlib.bowingParameters[('InAs', 'InSb')]
    assert 'directBandGap' in bow and 'electronMass' in bow
    # check interpolation with bowing parameters
    x = 0.2
    gap = (1 - x) * inas['directBandGap'] + x * insb['directBandGap'] \
          - x * (1 - x) * bow['directBandGap']
    mass = (1 - x) * inas['electronMass'] + x * insb['electronMass'] \
           - x * (1 - x) * bow['electronMass']
    assert alloy['directBandGap'] == approx(gap)
    assert alloy['electronMass'] == approx(mass)
    # parameters for which we don't have bowing parameters should be linearly interpolated
    assert 'valenceBandOffset' not in bow
    vbo = (1 - x) * inas['valenceBandOffset'] + x * insb['valenceBandOffset']
    assert alloy['valenceBandOffset'] == approx(vbo)


def test_band_offsets_fallback():
    """Test calculation of band positions and offsets via fallback on Anderson's rule."""
    # define a couple of semiconductors without valenceBandOffset
    matlib = materials.Materials()
    matlib.genMat('GaAs', 'semi', electronAffinity=4070., directBandGap=1519.)
    matlib.genMat('InAs', 'semi', directBandGap=417., electronAffinity=4900.)
    matlib.genMat('InSb', 'semi', electronAffinity=4590., directBandGap=235.)
    mat1 = matlib.find('InSb', eunit='eV')
    mat2 = matlib.find('InAs', eunit='eV')
    mat3 = matlib.find('GaAs', eunit='eV')
    assert matlib.conductionBandMinimum(mat1) - mat1['directBandGap'] == \
           approx(matlib.valenceBandMaximum(mat1))
    assert matlib.conductionBandMinimum(mat1) - matlib.conductionBandMinimum(mat2) == \
           approx(materials.conduction_band_offset(mat1, mat2))
    assert matlib.valenceBandMaximum(mat1) + mat1['directBandGap'] == \
           approx(matlib.conductionBandMinimum(mat1))
    assert matlib.valenceBandMaximum(mat1) - matlib.valenceBandMaximum(mat2) == \
           approx(materials.valence_band_offset(mat1, mat2))
    assert materials.conduction_band_offset(mat1, mat2) + \
           materials.conduction_band_offset(mat2, mat3) == \
           approx(materials.conduction_band_offset(mat1, mat3))
    assert materials.valence_band_offset(mat1, mat2) + \
           materials.valence_band_offset(mat2, mat3) == \
           approx(materials.valence_band_offset(mat1, mat3))


def test_effective_mass():
    """Test calculation of valence band masses from Luttinger parameters."""
    matlib = materials.Materials()
    gasb = matlib['GaSb']
    # check basic mass anisotropy
    assert gasb.holeMass('heavy', 'z') == gasb.holeMass('heavy', '001')
    assert gasb.holeMass('heavy', '001') < gasb.holeMass('heavy', '110')
    assert gasb.holeMass('heavy', '110') < gasb.holeMass('heavy', '111')
    assert gasb.holeMass('light', 'z') == gasb.holeMass('light', '001')
    assert gasb.holeMass('light', '001') > gasb.holeMass('light', '110')
    assert gasb.holeMass('light', '110') > gasb.holeMass('light', '111')
    # compare DOS average masses to directional masses
    assert gasb.holeMass('heavy', '001') < gasb.holeMass('heavy', 'dos') < \
           gasb.holeMass('heavy', '110')
    assert gasb.holeMass('light', '001') > gasb.holeMass('light', 'dos') > \
           gasb.holeMass('light', '110')
    assert gasb.holeMass('light', 'dos') < gasb.holeMass('heavy', 'dos') < \
           gasb.holeMass('dos', 'dos')
    # compare to a few reference values from http://www.ioffe.ru/SVA/NSM/
    assert gasb.holeMass('heavy', 'dos') == approx(0.4, rel=0.2)
    assert gasb.holeMass('light', 'dos') == approx(0.05, rel=0.2)
    inas = matlib.find('InAs')
    inas.holeMass('heavy', 'dos')
    assert inas.holeMass('heavy', 'dos') == approx(0.41, rel=0.2)
    assert inas.holeMass('light', 'dos') == approx(0.026, rel=0.2)
    assert inas.holeMass('dos', 'dos') == approx(0.41, rel=0.2)
