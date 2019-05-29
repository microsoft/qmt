# Materials database

## Metals
|   metal    |work function [eV]|
|------------|-----------------:|
|Al          |             4.280|
|Au          |             5.285|
|NbTiN       |             4.280|
|degenDopedSi|             4.050|

Sources:
* Wikipedia
* Ioffe Institute, http://www.ioffe.ru/SVA/NSM/Semicond/Si/basic.html

## Dielectrics
|dielectric|relative permittivity|
|----------|--------------------:|
|Al2O3     |                  9.0|
|HfO2      |                 25.0|
|Si3N4     |                  7.0|
|SiO2      |                  3.9|
|ZrO2      |                 25.0|
|air       |                  1.0|

Sources:
* Robertson, EPJAP 28, 265 (2004): High dielectric constant oxides,
  https://doi.org/10.1051/epjap:2004206
* Biercuk et al., APL 83, 2405 (2003), Low-temperature atomic-layer-deposition lift-off method
  for microelectronic and nanoelectronic applications, https://doi.org/10.1063/1.1612904
* Yota et al.,  JVSTA 31, 01A134 (2013), Characterization of atomic layer deposition HfO2,
  Al2O3, and plasma-enhanced chemical vapor deposition Si3N4 as metal-insulator-metal
  capacitor dielectric for GaAs HBT technology, https://doi.org/10.1116/1.4769207

## Semiconductors
|                                                         | AlAs | AlSb  | GaAs | GaSb | InAs |  InP  | InSb |  Si  |
|---------------------------------------------------------|-----:|------:|-----:|-----:|-----:|------:|-----:|-----:|
|relative permittivity                                    |10.060|11.0000|13.100|15.700|15.150|12.5000|16.800|11.700|
|electron mass [m_e]                                      | 0.150| 0.1400| 0.067| 0.039| 0.026| 0.0795| 0.013| 1.108|
|electron affinity $\chi$ [eV]                            | 2.970|       | 4.070| 4.060| 4.900| 4.3800| 4.590| 4.050|
|direct band gap $E_g(\Gamma)$ [eV]                       | 3.099| 2.3860| 1.519| 0.812| 0.417| 1.4236| 0.235| 3.480|
|valence band offset w.r.t. InSb [eV]                     |-1.330|-0.4100|-0.800|-0.030|-0.590|-0.9400| 0.000|      |
|spin-orbit splitting $\Delta_{so}$ [eV]                  | 0.280| 0.6760| 0.341| 0.760| 0.390| 0.1080| 0.810| 0.044|
|interband matrix element $E_P$ [eV]                      |21.100|18.7000|28.800|27.000|21.500|20.7000|23.300|      |
|Luttinger parameter $\gamma_1$                           | 3.760| 5.1800| 6.980|13.400|20.000| 5.0800|34.800| 4.280|
|Luttinger parameter $\gamma_2$                           | 0.820| 1.1900| 2.060| 4.700| 8.500| 1.6000|15.500| 0.339|
|Luttinger parameter $\gamma_3$                           | 1.420| 1.9700| 2.930| 6.000| 9.200| 2.1000|16.500| 1.446|
|charge neutrality level [from VB edge, in eV]            |      |       |      |      | 0.577|       | 0.118|      |
|density of surface states [10$^{12}$ cm$^{-2}$ eV$^(-1)$]|      |       |      |      | 3.000|       | 3.000|      |

Sources:
* [Vurgaftman] Vurgaftman et al., APR 89, 5815 (2001): Band parameters for III-V compound
  semiconductors and their alloys,  https://doi.org/10.1063/1.1368156
* [Heedt] Heedt, et al. Resolving ambiguities in nanowire field-effect transistor
  characterization. Nanoscale 7, 18188-18197, 2015. https://doi.org/10.1039/c5nr03608a
* [Monch] Monch, Semiconductor Surfaces and Interfaces, 3rd Edition, Springer (2001).
* [ioffe.ru] http://www.ioffe.ru/SVA/NSM/Semicond

### Bowing parameters

Properties of an alloy $A_{1-x} B_x$ are computed by quadratic interpolation between the
endpoints if there is a corresponding bowing parameter for this property and alloy.
Otherwise linear interpolation is employed. The quadratic interpolation formula uses the
convention
    $O(A_{1-x} B_x) = (1-x) O(A) + x O(B) - x(1-x) O_{AB}$,
with the bowing parameter $O_{AB}$.

|                                       |(AlAs, GaAs)|(AlAs, InAs)|(GaAs, InAs)|(GaSb, InSb)|(InAs, InSb)|
|---------------------------------------|-----------:|-----------:|-----------:|-----------:|-----------:|
|electron mass [m_e]                    |           0|      0.0490|      0.0091|      0.0092|       0.035|
|direct band gap $E_g(\Gamma)$ [eV]     |            |      0.7000|      0.4770|      0.4250|       0.670|
|valence band offset w.r.t. InSb [eV]   |            |     -0.6400|     -0.3800|            |            |
|spin-orbit splitting $\Delta_{so}$ [eV]|            |      0.1500|      0.1500|      0.1000|       1.200|
|interband matrix element $E_P$ [eV]    |            |            |     -1.4800|            |            |

Sources:
* [Vurgaftman] Vurgaftman et al., APR 89, 5815 (2001): Band parameters for III-V compound
  semiconductors and their alloys,  https://doi.org/10.1063/1.1368156
