"""Research-grade 2D incompressible Navier-Stokes simulations."""

from .config import SimulationConfig, load_config
from .runner import run_simulation

__all__ = ["SimulationConfig", "load_config", "run_simulation"]
