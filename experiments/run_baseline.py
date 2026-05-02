from __future__ import annotations

from navier_stokes_research.config import load_config
from navier_stokes_research.logging_utils import configure_logging
from navier_stokes_research.runner import run_simulation


def main() -> None:
    config = load_config("configs/baseline_random.json")
    configure_logging(config.output.log_level)
    run_simulation(config)


if __name__ == "__main__":
    main()
