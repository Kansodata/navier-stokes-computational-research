from __future__ import annotations

import json
from pathlib import Path

import pytest

from navier_stokes_research.config import ForcingConfig, load_config


def _write_config(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload), encoding="utf-8")


def test_load_config_adds_disabled_forcing_defaults(tmp_path: Path) -> None:
    config_path = tmp_path / "baseline.json"
    _write_config(
        config_path,
        {
            "experiment_name": "baseline",
            "physics": {"viscosity": 0.001},
        },
    )

    config = load_config(config_path)

    assert config.forcing == ForcingConfig()
    assert config.to_dict()["forcing"]["enabled"] is False
    assert config.to_dict()["forcing"]["forcing_type"] == "none"


def test_forcing_config_accepts_enabled_deterministic_narrow_band() -> None:
    forcing = ForcingConfig(
        enabled=True,
        forcing_type="fourier_deterministic_narrow_band",
        k_min=2.0,
        k_max=4.0,
        target_energy_input_rate=0.01,
        ekman_drag=0.1,
    )

    assert forcing.enabled is True
    assert forcing.forcing_type == "fourier_deterministic_narrow_band"


def test_forcing_config_accepts_enabled_ou_narrow_band() -> None:
    forcing = ForcingConfig(
        enabled=True,
        forcing_type="fourier_ou_narrow_band",
        k_min=2.0,
        k_max=4.0,
        target_energy_input_rate=0.01,
        ou_correlation_time=0.5,
        ou_noise_amplitude=1.0,
        ekman_drag=0.1,
    )

    assert forcing.enabled is True
    assert forcing.forcing_type == "fourier_ou_narrow_band"


def test_forcing_config_rejects_enabled_without_implemented_type() -> None:
    with pytest.raises(ValueError, match="must use an implemented forcing_type"):
        ForcingConfig(enabled=True)


def test_forcing_config_rejects_ou_without_positive_noise_amplitude() -> None:
    with pytest.raises(ValueError, match="ou_noise_amplitude > 0"):
        ForcingConfig(
            enabled=True,
            forcing_type="fourier_ou_narrow_band",
            k_min=2.0,
            k_max=4.0,
            target_energy_input_rate=0.01,
        )


def test_forcing_config_rejects_non_none_type_while_disabled() -> None:
    with pytest.raises(ValueError, match="forcing_type='none'"):
        ForcingConfig(forcing_type="fourier_ou_narrow_band")


def test_forcing_config_rejects_invalid_numeric_parameters() -> None:
    invalid_cases = [
        ("k_min", -1.0, "k_min"),
        ("k_max", -1.0, "k_max"),
        ("ou_correlation_time", 0.0, "ou_correlation_time"),
        ("ou_noise_amplitude", -1.0, "ou_noise_amplitude"),
        ("target_energy_input_rate", -1.0, "target_energy_input_rate"),
        ("ekman_drag", -1.0, "ekman_drag"),
    ]
    for field_name, value, expected_message in invalid_cases:
        with pytest.raises(ValueError, match=expected_message):
            ForcingConfig(**{field_name: value})


def test_forcing_config_rejects_inverted_forcing_band() -> None:
    with pytest.raises(ValueError, match="k_max must be greater than or equal"):
        ForcingConfig(k_min=4.0, k_max=3.0)


def test_forcing_config_rejects_enabled_zero_band_or_zero_input_rate() -> None:
    with pytest.raises(ValueError, match="k_max > 0"):
        ForcingConfig(
            enabled=True,
            forcing_type="fourier_deterministic_narrow_band",
            target_energy_input_rate=0.01,
        )
    with pytest.raises(ValueError, match="target_energy_input_rate > 0"):
        ForcingConfig(
            enabled=True,
            forcing_type="fourier_deterministic_narrow_band",
            k_min=2.0,
            k_max=4.0,
        )
