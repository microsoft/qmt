# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

#
# This defines the physical material specification format, which is stored as
# a json file. To add to the json or regenerate it, run this module as a script.
#

from __future__ import absolute_import, division, print_function
import collections
import json
import os
import re
import sys
import textwrap
from ast import literal_eval
import numpy as np
from six import iteritems, itervalues
import qmt.physics_constants as pc

units = pc.units
parseUnit = pc.parse_unit
toFloat = pc.to_float


__all__ = ["Material", "Materials", "conduction_band_offset", "valence_band_offset"]


class Material(collections.Mapping):
    """Wrapper for an entry in the materials database.

    Allows for the retrieval of a material's properties. Adds units awareness on top of a plain
    dict containing the properties.

    :param str name: Material name.
    :param dict properties: Collection of material properties.
    :param str eunit:
        Unit of energy. If specified, all queries for band parameters
        that have the dimension of an energy return floats with respect
        to this energy unit. With the default (None), such queries
        return sympy quantities that have the dimension of an energy.
    """

    def __init__(self, name, properties, eunit=None):
        self.name = name
        self.properties = dict(properties)
        if eunit is None:
            self.energyUnit = units.meV
        else:
            self.energyUnit = toFloat(units.meV / parseUnit(eunit))
        # Tuple of key values that have energy units:
        self.energy_quantities = (
            "workFunction",
            "fermiEnergy",
            "electronAffinity",
            "directBandGap",
            "valenceBandOffset",
            "chargeNeutralityLevel",
            "interbandMatrixElement",
            "spinOrbitSplitting",
        )

    def __getitem__(self, key):
        try:
            value = self.properties[key]
        except KeyError:
            raise KeyError("KeyError: material '{}' has no '{}'".format(self.name, key))
        if key in self.energy_quantities:
            value *= self.energyUnit
        return value

    def __setitem__(self, key, value):
        if key in self.energy_quantities:
            scaled_value = toFloat(
                value / self.energyUnit
            )  # if is an energy quantity, scale it
        else:
            scaled_value = value  # otherwise just pass
        self.properties[key] = scaled_value

    def __iter__(self):
        return iter(self.properties)

    def __len__(self):
        return len(self.properties)

    def __repr__(self):
        return "Material({}, {}, {})".format(
            self.name, self.properties, self.energyUnit
        )

    def serialize_dict(self):
        """Return a dict with the material properties that can be dumped to json."""
        return self.properties

    def hole_mass(self, band, direction):
        """Determine effective mass for a valence band.

        :param str band: Which valence band: 'heavy' or 'light' for a specific band. Also 'dos' for
            a density-of-states mass corresponding to both bands.
        :param str direction: Momentum direction: One of '001', '110', or '111'. 'z' is equivalent
            to '001'. Can also be 'dos' for the scalar density-of-states mass of a corresponding
            isotropic band dispersion.
        """
        # DOS effective mass corresponding to both heavy and light hole band
        # [Lax and Mavroides (1955) Eq. 17]
        if band == "dos":
            return (
                self.hole_mass("heavy", direction) ** 1.5
                + self.hole_mass("light", direction) ** 1.5
            ) ** (2 / 3.0)

        # Retrieve Luttinger parameters
        gamma1, gamma2, gamma3 = (self["luttingerGamma%s" % i] for i in (1, 2, 3))
        if band == "heavy":
            sign = -1
        elif band == "light":
            sign = 1
        else:
            raise RuntimeError("invalid band: {}".format(band))

        # DOS effective mass corresponding to anisotropic (possibly warped) band.
        # [We use the expansion from Lax and Mavroides (1955) Eq. 15;
        #  also cf. Lawaetz (1971) Eqs. 33-36.
        #  These approximations agree with the exact averages obtained by angular integration to
        #  within a few percent for relevant materials, cf. Table 1 of Mecholsky, Resca, Pegg
        #  & Fornari (2016).]
        if direction == "dos":
            # light-to-heavy hole splitting
            gamma_bar = np.sqrt(2 * (gamma2 ** 2 + gamma3 ** 2))
            # anisotropy factor for heavy or light hole
            gamma_hl = (
                -sign
                * 6
                * (gamma3 ** 2 - gamma2 ** 2)
                / (gamma_bar * (gamma1 + sign * gamma_bar))
            )
            return (
                1.0
                / (gamma1 + sign * gamma_bar)
                * (1 + 0.05 * gamma_hl + 0.0164 * gamma_hl ** 2) ** (2 / 3.0)
            )
            # The following expression would hold if the band was circularly symmetric in xy-plane
            # return (self.holeMass(band, '001') * self.holeMass(band,
            # '110')**2)**(1 / 3.)

        # Effective mass for a specific band and direction [Vurgaftman et al.
        # (2001) Eqs. 2.16-2.17]
        if direction in ("z", "001"):
            return 1.0 / (gamma1 + sign * 2 * gamma2)
        elif direction == "110":
            return 2.0 / (2 * gamma1 + sign * gamma2 + sign * 3 * gamma3)
        elif direction == "111":
            return 1.0 / (gamma1 + sign * 2 * gamma3)
        else:
            raise RuntimeError("invalid direction: " + str(direction))


class Materials(collections.Mapping):
    """Class for creating, loading, and manipulating a json file that
    contains information about materials.

    The default constructor (matPath=None, matDict=None) sets matPath to the module's
    materials.json and loads it. If both matPath and matDict are specified, the Materials
    database is initialized from the given path and then updated with the supplied dict.

    :param str matPath:
        Path to the mat json file. If initialized with None, should be set
        manually before loading/saving.
    :param dict matDict:
        Dictionary of materials to fill the database.
    :param Bool load:
        Load the json file. Needs to be False when creating a new materials.json file.
    """

    def __init__(self, matPath=None, matDict=None, load=True):
        self.matDict = {}
        self.bowingParameters = {}
        if matPath is None and matDict is None:
            matPath = os.path.join(os.path.dirname(__file__), "materials.json")
        self.matPath = matPath

        if matPath is not None and load:
            self.load()

        if matDict is not None:
            self.bowingParameters.update(matDict.pop("__bowing_parameters", {}))
            self.matDict = matDict

    def __iter__(self):
        return iter(self.matDict)

    def __len__(self):
        return len(self.matDict)

    def add_material(self, name, mat_type, **kwargs):
        """Generate a material and add it to the matDict.
        """
        if mat_type in ("metal", "dielectric"):
            kwargs["electronMass"] = kwargs.get("electronMass", 1.0)
        self.matDict[name] = self._make_material(mat_type, **kwargs)

    def set_bowing_parameters(self, name_a, name_b, mat_type, **kwargs):
        """Generate a bowing parameter set and add it to the bowingParameters dict."""
        self.bowingParameters[(name_a, name_b)] = self._make_material(
            mat_type, **kwargs
        )

    def _make_material(self, mat_type, **kwargs):
        material = {}

        def set_property(key):
            if key in kwargs and kwargs[key] is not None:
                material[key] = float(kwargs.pop(key))

        material["type"] = mat_type
        set_property("relativePermittivity")  # \eps_r
        set_property("electronMass")  # m_e* [in units of bare electron mass]
        if mat_type in ("metal", "dielectric"):
            set_property("workFunction")  # Work function \Phi [in meV]
            set_property("fermiEnergy")
        if mat_type == "semi":
            set_property("electronAffinity")  # Electron affinity \chi [in meV]
            set_property("directBandGap")  # E_g(\Gamma) [in meV]
            # wrt InSb valence band maximum [in meV]
            set_property("valenceBandOffset")
            set_property("spinOrbitSplitting")  # [in meV]
            # describes coupling of s and p states [in meV]
            set_property("interbandMatrixElement")
            # Luttinger parameters \gamma_{1,2,3}
            set_property("luttingerGamma1")
            set_property("luttingerGamma2")
            set_property("luttingerGamma3")
            # Charge neutrality level, measured from the VB edge [in meV].
            set_property("chargeNeutralityLevel")
            # Density of surface states [in cm-2 eV-1]
            set_property("surfaceChargeDensity")

            # Unused so far
            # set_property('holeMass')  # Hole mass [in units of bare electron mass]
            # set_property('valence_band_maximum')  # Position of valence band maximum [in meV]
            # set_property('conduction_band_minimum')  # Position of conduction band minimum [in
            # meV]
            # set_property('bulkDoping')  # Bulk doping [unit?]

        if kwargs:
            raise TypeError("unused arguments: " + str(list(kwargs.keys())))
        return material

    def __getitem__(self, key):
        return self.find(key)

    def __setitem__(self, key, val):
        # This assumes that val is a Material object
        self.matDict[key] = val.properties

    def find(self, name, eunit=None):
        """Retrieve a named material from the database.

        If the material is not found directly, an attempt is made to construct
        it by mixing two known materials. If that also fails, a KeyError is raised.

        :param str name:
            Name of the desired material.
        :param str eunit:
            Unit of energy. This is passed on to the Material constructor.
        """
        if name in self.matDict:
            properties = self.matDict[name]
        else:
            # print("parsing", name)
            # A_y B_x C
            bin_pattern1 = (
                r"([A-Z][a-z]*)(\d+\.?\d*|\.\d+)([A-Z][a-z]*)(\d+\.?\d*|\.\d+)([A-Z]["
                r"a-z]*)"
            )
            # A B_y C_x
            bin_pattern2 = (
                r"([A-Z][a-z]*)([A-Z][a-z]*)(\d+\.?\d*|\.\d+)([A-Z][a-z]*)("
                r"\d+\.?\d*|\.\d+)"
            )
            # (A)_y (B)_x
            bin_pattern3 = r"\((.+)\)(\d+\.?\d*|\.\d+)\((.+)\)(\d+\.?\d*|\.\d+)"
            match1 = re.match(bin_pattern1, name)
            match2 = re.match(bin_pattern2, name)
            match3 = re.match(bin_pattern3, name)
            if match1:
                A, y, B, x, C = match1.groups()
                x, y = float(x), float(y)
                x /= x + y
                properties = self._make_binary_alloy(A + C, B + C, x)
            elif match2:
                A, B, y, C, x = match2.groups()
                x, y = float(x), float(y)
                x /= x + y
                properties = self._make_binary_alloy(A + B, A + C, x)
            elif match3:
                A, y, B, x = match3.groups()
                x, y = float(x), float(y)
                x /= x + y
                properties = self._make_binary_alloy(A, B, x)
            else:
                raise KeyError(name)
        return Material(name, properties, eunit=eunit)

    def _make_binary_alloy(self, nameA, nameB, x):
        """Interpolate properties of binary alloy A_{1-x} B_x.

        The material database must contain properties for the two named materials.
        Properties of the alloy are computed by quadratic interpolation between the endpoints if
        there is a corresponding bowing parameter for this property and alloy. Otherwise linear
        interpolation is employed. Following Eq. 4.1 of
        [Vurgaftman et al., J. Appl. Phys. 89, 5837 (2001)], the quadratic interpolation formula
        uses the convention
            O(A_{1-x} B_x) = (1-x) O(A) + x O(B) - x(1-x) O_{AB} ,
        with the bowing parameter O_{AB}.
        """
        assert x >= 0 and x <= 1
        if (nameB, nameA) in self.bowingParameters:
            nameA, nameB = nameB, nameA
            x = 1.0 - x
        matA, matB = self.find(nameA, eunit="meV"), self.find(nameB, eunit="meV")
        bow = self.bowingParameters.get((nameA, nameB), {})
        alloy = {}
        for key, valA in iteritems(matA):
            if key not in matB:
                continue
            valB = matB[key]
            if key == "type":
                assert valA == valB
                val = valA
            else:
                bowVal = bow.get(key, 0)
                val = (1 - x) * valA + x * valB - x * (1 - x) * bowVal
            alloy[key] = val
        return alloy

    def serialize_dict(self):
        db = self.matDict.copy()
        bowingParms = {}
        for k, v in iteritems(self.bowingParameters):
            bowingParms[str(k)] = v
        db["__bowing_parameters"] = bowingParms
        return db

    def deserialize_dict(self, db):
        bowingParms = db.pop("__bowing_parameters", {})
        self.matDict = db
        self.bowingParameters = {}
        for k, v in iteritems(bowingParms):
            self.bowingParameters[literal_eval(k)] = v

    def save(self):
        """Save the current materials database to disk.
        """
        db = self.serialize_dict()
        with open(self.matPath, "w") as myFile:
            json.dump(db, myFile, indent=4, sort_keys=True)

    def load(self):
        """Load the materials database from disk.
        """
        try:
            with open(self.matPath, "r") as myFile:
                db = json.load(myFile)
            self.deserialize_dict(db)
        except IOError:
            print("Could not load materials file %s." % self.matPath)
            print("Generating a new file at that location...")
            generate_file(self.matPath)
            self.load()

    def conduction_band_minimum(self, mat):
        """Calculate the energy of the conduction band minimum $E_c$ of a semiconductor material.

        The reference energy E=0 is fixed to the vacuum level, as defined by the electron affinity
        of InSb. If Anderson's rule were exact, this method would return the (negative) electron
        affinity of `mat`. Since Anderson's rule ignores interface effects, it is preferable to use
        empirically determined band offsets for the alignment of bands in heterostructures rather
        than electron affinities (c.f. Vurgaftman et al. (2001)). Therefore, we use the electron
        affinity of a single material as reference point and try to align all other materials
        according to the respective band offsets.
        If the material's valenceBandOffset is not known, we return `-mat[electronAffinity]`,
        effectively falling back on Anderson's rule.

        :param Material mat:
            Material whose conduction band position is to be determined.

        See also
        --------
        - valence_band_maximum(mat) is equivalent to
          `self.conduction_band_minimum(mat) - mat['directBandGap']`
        - conduction_band_offset(mat1, mat2) is equivalent to
          `self.conduction_band_minimum(mat1) - self.conduction_band_minimum(mat2)`
        """
        ref_name = "InSb"
        if mat["type"] == "metal":
            return -mat["workFunction"] - mat["fermiEnergy"]
        elif mat["type"] == "dielectric":
            return 0.0 * mat.energyUnit  # vacuum energy
        assert mat["type"] == "semi"
        try:
            cbo = mat["valenceBandOffset"] + mat["directBandGap"]
            ref = self.matDict[ref_name]
            ref_level = -(
                ref["electronAffinity"]
                + ref["directBandGap"]
                + ref["valenceBandOffset"]
            )
            ref_level *= mat.energyUnit
            return cbo + ref_level
        except KeyError:
            # fall back to Anderson's rule
            if "cbo" not in locals():
                msg = "Material '{}' misses valenceBandOffset or directBandGap.".format(
                    mat.name
                )
            elif "ref" not in locals():
                msg = (
                    "Reference material '"
                    + ref_name
                    + "' missing from materials library."
                )
            else:
                msg = (
                    "Reference material '" + ref_name + "' misses valenceBandOffset or "
                    "directBandGap or electronAffinity."
                )
            msg += " Falling back on Anderson's rule."
            print(msg)
            return -mat["electronAffinity"]

    def valence_band_maximum(self, mat):
        """Calculate the energy of the valence band maximum $E_v$ of a semiconductor material.

        The reference energy E=0 is fixed to the vacuum level, as defined by the electron affinity
        of InSb. See conduction_band_minimum for additional details.

        :param Material mat:
            Material whose valence band position is to be determined.

        See also
        --------
        - conduction_band_minimum(mat) is equivalent to
          `self.valence_band_maximum(mat) + mat['directBandGap']`
        - valence_band_offset(mat1, mat2) is equivalent to
          `self.valence_band_maximum(mat1) - self.valence_band_maximum(mat2)`
        """
        if mat["type"] == "metal":
            return -10.0e3 * mat.energyUnit  # very low
        elif mat["type"] == "dielectric":
            return -10.0e3 * mat.energyUnit  # very low
        assert mat["type"] == "semi"
        ref_name = "InSb"
        try:
            vbo = mat["valenceBandOffset"]
            ref = self.matDict[ref_name]
            ref_level = -(
                ref["electronAffinity"]
                + ref["directBandGap"]
                + ref["valenceBandOffset"]
            )
            ref_level *= mat.energyUnit
            return vbo + ref_level
        except KeyError:
            # fall back to Anderson's rule
            if "vbo" not in locals():
                msg = "Material '" + mat.name + "' misses valenceBandOffset."
            elif "ref" not in locals():
                msg = (
                    "Reference material '"
                    + ref_name
                    + "' missing from materials library."
                )
            else:
                msg = (
                    "Reference material '" + ref_name + "' misses valenceBandOffset or "
                    "directBandGap or electronAffinity."
                )
            msg += " Falling back on Anderson's rule."
            print(msg)
            return -(mat["electronAffinity"] + mat["directBandGap"])

    # TODO: make this user-configurable and shift all energy properties reported by materials
    def reference_level(self, eunit=None):
        if eunit is None:
            eunit = units.meV
        else:
            eunit = toFloat(units.meV / parseUnit(eunit))
        return -self.matDict["InSb"]["electronAffinity"] * eunit


def conduction_band_offset(mat, ref_mat):
    """
    Calculate the conduction band offset $E_c - E_{c,ref}$ between two semiconductor materials.

    :param Material mat:
        Material whose conduction band position is to be determined.
    :param Material ref_mat:
        Material whose conduction band minimum is used as reference energy.
    """
    assert mat.energyUnit == ref_mat.energyUnit
    try:
        cbo = mat["valenceBandOffset"] + mat["directBandGap"]
        ref_level = ref_mat["valenceBandOffset"] + ref_mat["directBandGap"]
        return cbo - ref_level
    except KeyError:
        # fall back to Anderson's rule
        if "cbo" not in locals():
            msg = "Material '{}' misses valenceBandOffset or directBandGap.".format(
                mat.name
            )
        else:
            msg = (
                "Reference material '"
                + ref_mat.name
                + "' misses valenceBandOffset or directBandGap."
            )
        msg += " Falling back on Anderson's rule."
        print(msg)
        chi = mat["electronAffinity"]
        return ref_mat["electronAffinity"] - chi


def valence_band_offset(mat, ref_mat):
    """
    Calculate the valence band offset $E_v - E_{v,ref}$ between two semiconductor materials.

    :param Material mat:
        Material whose conduction band position is to be determined.
    :param Material ref_mat:
        Material whose conduction band minimum is used as reference energy.
    """
    assert mat.energyUnit == ref_mat.energyUnit
    try:
        vbo = mat["valenceBandOffset"]
        ref_level = ref_mat["valenceBandOffset"]
        return vbo - ref_level
    except KeyError:
        # fall back to Anderson's rule
        if "vbo" not in locals():
            msg = "Material '" + mat.name + "' misses valenceBandOffset."
        else:
            msg = "Reference material '" + ref_mat.name + "' misses valenceBandOffset."
        msg += " Falling back on Anderson's rule."
        print(msg)
        e_ion = mat["electronAffinity"] + mat["directBandGap"]
        e_ref = ref_mat["electronAffinity"] + ref_mat["directBandGap"]
        return e_ref - e_ion


def write_database_to_markdown(out_file, mat_lib):
    """
    Write all materials parameters in mat_lib to a nicely formatted markdown file.

    :param stream out_file: Output file handle.
    :param Materials mat_lib: Materials database to be written.
    """
    import pytablewriter

    print("# Materials database", file=out_file)
    print(file=out_file)

    print("## Metals", file=out_file)
    writer = pytablewriter.MarkdownTableWriter()
    writer.stream = out_file
    table = []
    for name in sorted(mat_lib.matDict.keys()):
        mat = mat_lib.find(name, eunit="eV")
        if mat["type"] == "metal":
            table.append([name, mat["workFunction"]])
            table.append([name, mat["fermiEnergy"]])
    writer.header_list = ["metal", "work function [eV]"]
    writer.value_matrix = table
    writer.write_table()
    print(
        textwrap.dedent(
            """\
        Sources:
        * Wikipedia
        * Ioffe Institute, http://www.ioffe.ru/SVA/NSM/Semicond/Si/basic.html
        """
        ),
        file=out_file,
    )

    print("## Dielectrics", file=out_file)
    table = []
    for name in sorted(mat_lib.matDict.keys()):
        mat = mat_lib.find(name, eunit="eV")
        if mat["type"] == "dielectric":
            table.append([name, mat["relativePermittivity"]])
    writer.header_list = ["dielectric", "relative permittivity"]
    writer.value_matrix = table
    writer.write_table()
    print(
        textwrap.dedent(
            """\
        Sources:
        * Robertson, EPJAP 28, 265 (2004): High dielectric constant oxides,
          https://doi.org/10.1051/epjap:2004206
        * Biercuk et al., APL 83, 2405 (2003), Low-temperature atomic-layer-deposition lift-off
        method
          for microelectronic and nanoelectronic applications, https://doi.org/10.1063/1.1612904
        * Yota et al.,  JVSTA 31, 01A134 (2013), Characterization of atomic layer deposition HfO2,
          Al2O3, and plasma-enhanced chemical vapor deposition Si3N4 as metal-insulator-metal
          capacitor dielectric for GaAs HBT technology, https://doi.org/10.1116/1.4769207
        """
        ),
        file=out_file,
    )

    print("## Semiconductors", file=out_file)
    semi_props = [
        ("relativePermittivity", "relative permittivity"),
        ("electronMass", r"electron mass [m_e]"),
        ("electronAffinity", r"electron affinity $\chi$ [eV]"),
        ("directBandGap", r"direct band gap $E_g(\Gamma)$ [eV]"),
        ("valenceBandOffset", r"valence band offset w.r.t. InSb [eV]"),
        ("spinOrbitSplitting", r"spin-orbit splitting $\Delta_{so}$ [eV]"),
        ("interbandMatrixElement", r"interband matrix element $E_P$ [eV]"),
        ("luttingerGamma1", r"Luttinger parameter $\gamma_1$"),
        ("luttingerGamma2", r"Luttinger parameter $\gamma_2$"),
        ("luttingerGamma3", r"Luttinger parameter $\gamma_3$"),
        ("chargeNeutralityLevel", r"charge neutrality level [from VB edge, in eV]"),
        (
            "surfaceChargeDensity",
            r"density of surface states [10$^{12}$ cm$^{-2}$ eV$^(-1)$]",
        ),
    ]
    scale_factors = dict(surfaceChargeDensity=1e-12)
    table = [[desc] for desc in list(zip(*semi_props))[1]]
    semi_names = [
        name for name, mat in sorted(iteritems(mat_lib)) if mat["type"] == "semi"
    ]
    for name in semi_names:
        mat = mat_lib.find(name, eunit="eV")
        for i, (p, _) in enumerate(semi_props):
            if p in scale_factors and p in mat:
                value = scale_factors[p] * mat[p]
            else:
                value = mat.get(p, "")
            table[i].append(value)
    writer.header_list = [""] + semi_names
    writer.value_matrix = table
    writer.write_table()
    print(
        textwrap.dedent(
            """\
        Sources:
        * [Vurgaftman] Vurgaftman et al., APR 89, 5815 (2001): Band parameters for III-V compound
          semiconductors and their alloys,  https://doi.org/10.1063/1.1368156
        * [Heedt] Heedt, et al. Resolving ambiguities in nanowire field-effect transistor
          characterization. Nanoscale 7, 18188-18197, 2015. https://doi.org/10.1039/c5nr03608a
        * [Monch] Monch, Semiconductor Surfaces and Interfaces, 3rd Edition, Springer (2001).
        * [ioffe.ru] http://www.ioffe.ru/SVA/NSM/Semicond
        """
        ),
        file=out_file,
    )

    print(
        textwrap.dedent(
            """\
        ### Bowing parameters

        Properties of an alloy $A_{1-x} B_x$ are computed by quadratic interpolation between the
        endpoints if there is a corresponding bowing parameter for this property and alloy.
        Otherwise linear interpolation is employed. The quadratic interpolation formula uses the
        convention
            $O(A_{1-x} B_x) = (1-x) O(A) + x O(B) - x(1-x) O_{AB}$,
        with the bowing parameter $O_{AB}$.
        """
        ),
        file=out_file,
    )
    scale_factors = dict(
        (p, 1e-3)
        for p in (
            "workFunction",
            "fermiEnergy",
            "electronAffinity",
            "directBandGap",
            "valenceBandOffset",
            "chargeNeutralityLevel",
            "interbandMatrixElement",
            "spinOrbitSplitting",
        )
    )
    table = []
    bowing_mats = sorted(mat_lib.bowingParameters.keys())
    bowing_props = []
    for p, desc in semi_props:
        if np.any(
            [p in bow_parms for bow_parms in itervalues(mat_lib.bowingParameters)]
        ):
            bowing_props.append(p)
            table.append([desc])
    for name in bowing_mats:
        bow_parms = mat_lib.bowingParameters[name]
        for i, p in enumerate(bowing_props):
            if p in bow_parms:
                value = bow_parms[p] * scale_factors.get(p, 1.0)
            else:
                value = ""
            table[i].append(value)
    writer.header_list = [""] + ["({}, {})".format(*k) for k in bowing_mats]
    writer.value_matrix = table
    writer.write_table()
    print(
        textwrap.dedent(
            """\
        Sources:
        * [Vurgaftman] Vurgaftman et al., APR 89, 5815 (2001): Band parameters for III-V compound
          semiconductors and their alloys,  https://doi.org/10.1063/1.1368156
        """
        ),
        file=out_file,
    )


def generate_file(fname=None):
    materials = Materials(fname, load=False)

    # === Metals ===
    materials.add_material(
        "Al",
        "metal",
        relativePermittivity=1,
        # source? Wikipedia and others quote 4.06 - 4.26 eV
        # depending on face.
        workFunction=4280.0,
        # Ashcroft and Mermin:
        fermiEnergy=11700.0,
    )
    materials.add_material(
        "Au",
        "metal",
        relativePermittivity=1,
        # source- Wikipedia quotes it as 5.1-5.47; this is the
        # average.
        workFunction=5285.0,
        # Ashcroft and Mermin:
        fermiEnergy=5530.0,
    )
    materials.add_material(
        "degenDopedSi",
        "metal",
        relativePermittivity=1,
        # source - Ioffe Institute,
        # http://www.ioffe.ru/SVA/NSM/Semicond/Si/basic.html
        workFunction=4050.0,
        # unknown / probably depends on doping density; setting
        # it to Au for now.
        fermiEnergy=5530.0,
    )
    materials.add_material(
        "NbTiN",
        "metal",
        relativePermittivity=1,
        # Unknown; just setting it to Al for now.
        workFunction=4280.0,
        # Unknown; just setting it to Au for now.
        fermiEnergy=5530.0,
    )

    # === Dielectrics ===
    # Sources:
    # - Robertson, EPJAP 28, 265 (2004): High dielectric constant oxides,
    #   https://doi.org/10.1051/epjap:2004206
    # - Biercuk et al., APL 83, 2405 (2003), Low-temperature atomic-layer-deposition lift-off method
    #   for microelectronic and nanoelectronic applications, https://doi.org/10.1063/1.1612904
    # - Yota et al.,  JVSTA 31, 01A134 (2013), Characterization of atomic layer deposition HfO2,
    #   Al2O3, and plasma-enhanced chemical vapor deposition Si3N4 as metal-insulator-metal
    # capacitor dielectric for GaAs HBT technology,
    # https://doi.org/10.1116/1.4769207

    # air
    materials.add_material("air", "dielectric", relativePermittivity=1)

    # Si3N4
    # [Robertson]: eps=7.
    # [Yota]: eps=6.5 for PECVD Si3N4
    # [???]: eps=7.9
    materials.add_material("Si3N4", "dielectric", relativePermittivity=7.0)  # Robertson

    # SiO2
    # [Robertson]: eps=3.9
    materials.add_material("SiO2", "dielectric", relativePermittivity=3.9)

    # HfO2
    # [Robertson] eps=25
    # [Biercuk] eps=16-19 for ALD HfO2
    # [Yota] eps=18.7 for ALD HfO2
    # NB: Dielectric constant of ALD HfO2 seems to depend strongly on growth conditions like
    # temperature.
    materials.add_material("HfO2", "dielectric", relativePermittivity=25.0)  # Robertson

    # ZrO2
    # [Robertson] eps=25
    # [Biercuk] eps=20-29 for ALD ZrO2
    materials.add_material("ZrO2", "dielectric", relativePermittivity=25.0)  # Robertson

    # Al2O3
    # [Robertson] eps=9
    # [Biercuk] eps=8-9 for ALD Al2O3
    # [Yota] eps=10.3 for ALD Al2O3
    materials.add_material("Al2O3", "dielectric", relativePermittivity=9.0)  # Robertson

    # === Semiconductors ===
    # Sources:
    # - [ioffe.ru] http://www.ioffe.ru/SVA/NSM/Semicond
    # - [Vurgaftman] Vurgaftman et al., APR 89, 5815 (2001): Band parameters for III-V compound
    #   semiconductors and their alloys,  https://doi.org/10.1063/1.1368156
    # - [Heedt] Heedt, et al. Resolving ambiguities in nanowire field-effect transistor
    #   characterization. Nanoscale 7, 18188-18197, 2015. https://doi.org/10.1039/c5nr03608a
    # - [Monch] Monch, Semiconductor Surfaces and Interfaces, 3rd Edition, Springer (2001).
    materials.add_material(
        "GaAs",
        "semi",
        relativePermittivity=13.1,  # source?
        # 300K,
        # http://www.ioffe.ru/SVA/NSM/Semicond/GaAs/basic.html
        electronAffinity=4070.0,
        # Vurgaftman et al. (2001)
        electronMass=0.067,
        directBandGap=1519.0,
        valenceBandOffset=-800.0,
        luttingerGamma1=6.98,
        luttingerGamma2=2.06,
        luttingerGamma3=2.93,
        spinOrbitSplitting=341.0,
        interbandMatrixElement=28800.0,
    )
    # caution: AlAs has global CB minimum at X! We give values for the local
    # minimum at Gamma here.
    materials.add_material(
        "AlAs",
        "semi",
        # 300K, http://www.ioffe.ru/SVA/NSM/Semicond/AlGaAs/basic.html
        # Values for interpolating properties of Al_{x}Ga_{1-x}As with x<0.45.
        # Pure GaAs has \chi_a=3.5 eV.
        relativePermittivity=12.90 - 2.84,
        electronAffinity=4070.0 - 1100.0,
        # Vurgaftman et al. (2001)
        electronMass=0.15,
        directBandGap=3099,
        valenceBandOffset=-1330.0,
        luttingerGamma1=3.76,
        luttingerGamma2=0.82,
        luttingerGamma3=1.42,
        spinOrbitSplitting=280.0,
        interbandMatrixElement=21100.0,
    )
    materials.add_material(
        "InAs",
        "semi",
        relativePermittivity=15.15,  # ioffe.ru at 300 K; Davies quotes 14.6
        # Vurgaftman et al. (2001)
        electronMass=0.026,
        directBandGap=417.0,
        valenceBandOffset=-590.0,
        # NB: uncertainty on InAs Luttinger parameters seems to be
        # large
        luttingerGamma1=20.0,
        luttingerGamma2=8.5,
        luttingerGamma3=9.2,
        spinOrbitSplitting=390.0,
        interbandMatrixElement=21500.0,
        # ioffe.ru:
        electronAffinity=4900.0,
        # Heedt:
        chargeNeutralityLevel=417.0 + 160.0,
        surfaceChargeDensity=3e12,
    )
    materials.add_material(
        "GaSb",
        "semi",
        # 300 K,
        # http://www.ioffe.ru/SVA/NSM/Semicond/GaSb/basic.html
        relativePermittivity=15.7,
        electronAffinity=4060.0,
        # Vurgaftman et al. (2001)
        electronMass=0.039,
        directBandGap=812.0,
        valenceBandOffset=-30.0,
        luttingerGamma1=13.4,
        luttingerGamma2=4.7,
        luttingerGamma3=6.0,
        spinOrbitSplitting=760.0,
        interbandMatrixElement=27000.0,
    )
    materials.add_material(
        "AlSb",
        "semi",
        # https://en.wikipedia.org/wiki/Aluminium_antimonide and
        # https://www.azom.com/article.aspx?ArticleID=8427
        relativePermittivity=11.0,
        # Vurgaftman et al. (2001)
        electronMass=0.14,
        directBandGap=2386.0,
        valenceBandOffset=-410.0,
        luttingerGamma1=5.18,
        luttingerGamma2=1.19,
        luttingerGamma3=1.97,
        spinOrbitSplitting=676.0,
        interbandMatrixElement=18700.0,
    )
    materials.add_material(
        "InSb",
        "semi",
        # 300 K,
        # http://www.ioffe.ru/SVA/NSM/Semicond/InSb/basic.html
        relativePermittivity=16.8,
        electronAffinity=4590.0,
        # Vurgaftman et al. (2001)
        electronMass=0.0135,
        directBandGap=235.0,
        valenceBandOffset=0.0,
        luttingerGamma1=34.8,
        luttingerGamma2=15.5,
        luttingerGamma3=16.5,
        spinOrbitSplitting=810.0,
        interbandMatrixElement=23300.0,
        # Monch has some values for this, but I don't think we have too
        # good an idea. For now, I'll use mid-gap states of density equal to
        # InAs. TODO: experimentally determine this!
        chargeNeutralityLevel=0.5 * 235.0,
        surfaceChargeDensity=3e12,
    )
    materials.add_material(
        "InP",
        "semi",
        # 300 K,
        # http://www.ioffe.ru/SVA/NSM/Semicond/InP/basic.html
        relativePermittivity=12.5,
        electronAffinity=4380.0,
        # Vurgaftman et al. (2001)
        electronMass=0.0795,
        directBandGap=1423.6,
        valenceBandOffset=-940.0,
        luttingerGamma1=5.08,
        luttingerGamma2=1.60,
        luttingerGamma3=2.10,
        spinOrbitSplitting=108.0,
        interbandMatrixElement=20700.0,
    )
    materials.add_material(
        "Si",
        "semi",
        # 300 K,
        # http://www.ioffe.ru/SVA/NSM/Semicond/Si/basic.html
        relativePermittivity=11.7,
        electronAffinity=4050.0,
        electronMass=(0.98 + 0.19 * 2) ** (1.0 / 3.0),  # DOS mass
        # Yu & Cardona
        directBandGap=3480.0,
        luttingerGamma1=4.28,
        luttingerGamma2=0.339,
        luttingerGamma3=1.446,
        spinOrbitSplitting=44.0,
    )

    # bowing parameters from Vurgaftman et al. (2001)
    materials.set_bowing_parameters(
        "GaAs",
        "InAs",
        "semi",
        electronMass=0.0091,
        directBandGap=477.0,
        valenceBandOffset=-380.0,
        spinOrbitSplitting=150.0,
        interbandMatrixElement=-1480.0,
    )
    materials.set_bowing_parameters("AlAs", "GaAs", "semi", electronMass=0.0)
    materials.set_bowing_parameters(
        "AlAs",
        "InAs",
        "semi",
        electronMass=0.049,
        directBandGap=700.0,
        valenceBandOffset=-640.0,
        spinOrbitSplitting=150.0,
    )
    materials.set_bowing_parameters(
        "GaSb",
        "InSb",
        "semi",
        electronMass=0.0092,
        directBandGap=425.0,
        spinOrbitSplitting=100.0,
    )
    materials.set_bowing_parameters(
        "InAs",
        "InSb",
        "semi",
        electronMass=0.035,
        directBandGap=670.0,
        # the bowing of the spinOrbitSplitting seems
        # to be closer to zero for some
        # first-principles calculations!
        spinOrbitSplitting=1200.0,
    )

    materials.save()

    with open("materials.md", "w") as f:
        write_database_to_markdown(f, materials)


# New physical materials go here:
if __name__ == "__main__":
    if len(sys.argv) > 1:
        fname = sys.argv[1]
    else:
        fname = None
    generate_file(fname)
