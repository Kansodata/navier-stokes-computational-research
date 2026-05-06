# Science Integrity Notes

This repository uses fail-closed validation to prevent successful execution from being confused with scientific acceptance.

The controlled 2D forced-turbulence diagnostics separate `execution_status`, `budget_status`, spectral diagnostics, and `scientific_acceptance`. A run can execute correctly while still producing `warning` when the energy budget, stationarity window, or spectral slope evidence is insufficient for stronger interpretation. This is intentional: warnings preserve uncertainty instead of converting limited numerical evidence into turbulence claims.

The resolution sensitivity study records how spectral slope diagnostics change as the grid is refined and where the 2/3 Orszag de-aliasing cutoff constrains the available high-wavenumber fit range. Its output is diagnostic evidence for experiment design, not a proof of inertial-range scaling, not a 3D result, and not a Millennium Problem claim.
