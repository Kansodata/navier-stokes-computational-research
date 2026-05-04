from __future__ import annotations

import json
from dataclasses import asdict, dataclass
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
    dealiasing_enabled: bool = True


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
    )
