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
    assert matlib.conduction_band_minimum(mat1) - mat1['directBandGap'] == \
        approx(matlib.valence_band_maximum(mat1))
    assert matlib.conduction_band_minimum(mat1) - matlib.conduction_band_minimum(
        mat2) == approx(materials.conduction_band_offset(mat1, mat2))
    assert matlib.valence_band_maximum(mat1) + mat1['directBandGap'] == \
        approx(matlib.conduction_band_minimum(mat1))
    assert matlib.valence_band_maximum(mat1) - matlib.valence_band_maximum(
        mat2) == approx(materials.valence_band_offset(mat1, mat2))
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
    # band gap bowing for InAsSb is strong enough to push CBM in alloy below
    # CBM in either binary
    assert matlib.conduction_band_minimum(
        alloy) < matlib.conduction_band_minimum(inas)
    assert matlib.conduction_band_minimum(
        inas) < matlib.conduction_band_minimum(insb)
    # check that we have bowing parameters for m_* and E_g, which are
    # significant for this alloy
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
    # parameters for which we don't have bowing parameters should be linearly
    # interpolated
    assert 'valenceBandOffset' not in bow
    vbo = (1 - x) * inas['valenceBandOffset'] + x * insb['valenceBandOffset']
    assert alloy['valenceBandOffset'] == approx(vbo)


def test_band_offsets_fallback():
    """Test calculation of band positions and offsets via fallback on Anderson's rule."""
    # define a couple of semiconductors without valenceBandOffset
    matlib = materials.Materials()
    matlib.add_material('GaAs', 'semi', electronAffinity=4070., directBandGap=1519.)
    matlib.add_material('InAs', 'semi', directBandGap=417., electronAffinity=4900.)
    matlib.add_material('InSb', 'semi', electronAffinity=4590., directBandGap=235.)
    mat1 = matlib.find('InSb', eunit='eV')
    mat2 = matlib.find('InAs', eunit='eV')
    mat3 = matlib.find('GaAs', eunit='eV')
    assert matlib.conduction_band_minimum(mat1) - mat1['directBandGap'] == \
           approx(matlib.valence_band_maximum(mat1))
    assert matlib.conduction_band_minimum(mat1) - matlib.conduction_band_minimum(
        mat2) == approx(materials.conduction_band_offset(mat1, mat2))
    assert matlib.valence_band_maximum(mat1) + mat1['directBandGap'] == \
           approx(matlib.conduction_band_minimum(mat1))
    assert matlib.valence_band_maximum(mat1) - matlib.valence_band_maximum(
        mat2) == approx(materials.valence_band_offset(mat1, mat2))
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
    assert gasb.hole_mass('heavy', 'z') == gasb.hole_mass('heavy', '001')
    assert gasb.hole_mass('heavy', '001') < gasb.hole_mass('heavy', '110')
    assert gasb.hole_mass('heavy', '110') < gasb.hole_mass('heavy', '111')
    assert gasb.hole_mass('light', 'z') == gasb.hole_mass('light', '001')
    assert gasb.hole_mass('light', '001') > gasb.hole_mass('light', '110')
    assert gasb.hole_mass('light', '110') > gasb.hole_mass('light', '111')
    # compare DOS average masses to directional masses
    assert gasb.hole_mass('heavy', '001') < gasb.hole_mass('heavy', 'dos') < \
           gasb.hole_mass('heavy', '110')
    assert gasb.hole_mass('light', '001') > gasb.hole_mass('light', 'dos') > \
           gasb.hole_mass('light', '110')
    assert gasb.hole_mass('light', 'dos') < gasb.hole_mass('heavy', 'dos') < \
           gasb.hole_mass('dos', 'dos')
    # compare to a few reference values from http://www.ioffe.ru/SVA/NSM/
    assert gasb.hole_mass('heavy', 'dos') == approx(0.4, rel=0.2)
    assert gasb.hole_mass('light', 'dos') == approx(0.05, rel=0.2)
    inas = matlib.find('InAs')
    inas.hole_mass('heavy', 'dos')
    assert inas.hole_mass('heavy', 'dos') == approx(0.41, rel=0.2)
    assert inas.hole_mass('light', 'dos') == approx(0.026, rel=0.2)
    assert inas.hole_mass('dos', 'dos') == approx(0.41, rel=0.2)
