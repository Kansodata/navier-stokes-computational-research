from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class GridConfig:
    nx: int = 64
    ny: int = 64
    lx: float = 6.283185307179586
    ly: float = 6.283185307179586


@dataclass(frozen=True)
class TimeConfig:
    dt: float = 0.0025
    steps: int = 400
    save_every: int = 20
    cfl_safety: float = 0.8
    diffusion_safety: float = 0.5


@dataclass(frozen=True)
class PhysicsConfig:
    viscosity: float = 0.001


@dataclass(frozen=True)
class ForcingConfig:
    """Configuration for controlled 2D forcing experiments.

    Defaults preserve exact unforced baseline semantics. Deterministic and
    Ornstein-Uhlenbeck narrow-band Fourier forcing are opt-in only.
    """

    enabled: bool = False
    forcing_type: str = "none"
    k_min: float = 0.0
    k_max: float = 0.0
    seed: int = 42
    ou_correlation_time: float = 1.0
    ou_noise_amplitude: float = 0.0
    target_energy_input_rate: float = 0.0
    ekman_drag: float = 0.0

    def __post_init__(self) -> None:
        allowed_types = {"none", "fourier_deterministic_narrow_band", "fourier_ou_narrow_band"}
        if self.forcing_type not in allowed_types:
            raise ValueError(f"Unsupported forcing_type: {self.forcing_type}")
        if not self.enabled and self.forcing_type != "none":
            raise ValueError("Disabled forcing config must use forcing_type='none'.")
        if self.enabled and self.forcing_type == "none":
            raise ValueError("Enabled forcing config must use an implemented forcing_type.")
        if self.k_min < 0.0:
            raise ValueError("forcing.k_min must be non-negative")
        if self.k_max < 0.0:
            raise ValueError("forcing.k_max must be non-negative")
        if self.k_max < self.k_min:
            raise ValueError("forcing.k_max must be greater than or equal to forcing.k_min")
        if self.enabled and self.k_max <= 0.0:
            raise ValueError("enabled forcing requires k_max > 0")
        if self.ou_correlation_time <= 0.0:
            raise ValueError("forcing.ou_correlation_time must be positive")
        if self.ou_noise_amplitude < 0.0:
            raise ValueError("forcing.ou_noise_amplitude must be non-negative")
        if self.enabled and self.forcing_type == "fourier_ou_narrow_band" and self.ou_noise_amplitude <= 0.0:
            raise ValueError("OU forcing requires ou_noise_amplitude > 0")
        if self.target_energy_input_rate < 0.0:
            raise ValueError("forcing.target_energy_input_rate must be non-negative")
        if self.enabled and self.target_energy_input_rate <= 0.0:
            raise ValueError("enabled forcing requires target_energy_input_rate > 0")
        if self.ekman_drag < 0.0:
            raise ValueError("forcing.ekman_drag must be non-negative")


@dataclass(frozen=True)
class InitialConditionConfig:
    kind: str = "random"
    amplitude: float = 1.0
    smoothing_sigma: float = 6.0
    seed: int = 42
    vortex_radius: float = 0.35
    vortex_strength: float = 8.0
    vortex_distance: float = 1.5


@dataclass(frozen=True)
class OutputConfig:
    output_dir: str = "outputs/default_run"
    save_plots: bool = True
    save_snapshots: bool = True
    log_level: str = "INFO"


@dataclass(frozen=True)
class SimulationConfig:
    experiment_name: str
    grid: GridConfig
    time: TimeConfig
    physics: PhysicsConfig
    initial_condition: InitialConditionConfig
    output: OutputConfig
    forcing: ForcingConfig = field(default_factory=ForcingConfig)

    def to_dict(self) -> dict:
        return asdict(self)


def _merge_dataclass(cls, payload: dict | None):
    payload = payload or {}
    defaults = cls()
    values = asdict(defaults)
    values.update(payload)
    return cls(**values)


def load_config(path: str | Path) -> SimulationConfig:
    config_path = Path(path)
    with config_path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)

    experiment_name = payload.get("experiment_name", config_path.stem)
    return SimulationConfig(
        experiment_name=experiment_name,
        grid=_merge_dataclass(GridConfig, payload.get("grid")),
        time=_merge_dataclass(TimeConfig, payload.get("time")),
        physics=_merge_dataclass(PhysicsConfig, payload.get("physics")),
        initial_condition=_merge_dataclass(
            InitialConditionConfig,
            payload.get("initial_condition"),
        ),
        output=_merge_dataclass(OutputConfig, payload.get("output")),
        forcing=_merge_dataclass(ForcingConfig, payload.get("forcing")),
    )
