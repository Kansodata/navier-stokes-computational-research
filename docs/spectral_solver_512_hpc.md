# SpectralSolver512 HPC Design

`SpectralSolver512` is an opt-in 2D periodic vorticity-streamfunction solver for high-resolution experiments at `512 x 512`. It does not replace the validated baseline solver and does not introduce 3D, Millennium Problem, or formal-proof claims.

## Design choices

- FFTW plans are created once with `pyfftw.builders.fft2` and `pyfftw.builders.ifft2`.
- Large arrays are allocated with `pyfftw.empty_aligned` and reused across RK4 stages.
- The zero Fourier mode is explicitly cleared in the Poisson solve to enforce zero-mean streamfunction.
- The 2/3 Orszag de-aliasing mask is static and applied before inverse transforms that consume filtered spectral fields.
- The nonlinear Jacobian is transformed, filtered, and transformed back before RHS assembly.
- RK4 stage buffers are pre-allocated and updated with NumPy `out=` operations where practical.
- CFL and enstrophy divergence checks fail closed.
- Energy spectra are sampled into audit records at a configurable interval.

## Traceability note

ORCID identifies researchers; it is not a numerical V&V standard. For research traceability, this implementation records deterministic solver metadata, audit samples, CFL/enstrophy guards, de-aliasing policy, and explicit scientific limitations. That metadata can be linked to ORCID-authored reports, but scientific acceptance still requires human review and reproducible artifacts.
