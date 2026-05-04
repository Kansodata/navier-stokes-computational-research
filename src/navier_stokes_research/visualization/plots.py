from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np


def save_heatmap(field: np.ndarray, path: str | Path, title: str, colorbar_label: str) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(6, 5), constrained_layout=True)
    image = ax.imshow(field.T, origin="lower", cmap="coolwarm", aspect="auto")
    ax.set_title(title)
    ax.set_xlabel("x index")
    ax.set_ylabel("y index")
    fig.colorbar(image, ax=ax, label=colorbar_label)
    fig.savefig(destination, dpi=160)
    plt.close(fig)


def save_metric_evolution(metrics: list[dict[str, float]], path: str | Path) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    times = [entry["time"] for entry in metrics]

    fig, axes = plt.subplots(3, 1, figsize=(8, 9), constrained_layout=True)
    axes[0].plot(times, [entry["energy"] for entry in metrics], color="#0f766e")
    axes[0].set_title("Kinetic Energy")
    axes[1].plot(times, [entry["enstrophy"] for entry in metrics], color="#b45309")
    axes[1].set_title("Enstrophy")
    axes[2].plot(times, [entry["max_velocity"] for entry in metrics], color="#1d4ed8")
    axes[2].set_title("Max Velocity")

    for axis in axes:
        axis.set_xlabel("Time")
        axis.grid(alpha=0.25)

    fig.savefig(destination, dpi=160)
    plt.close(fig)


def save_taylor_green_error_diagnostics(
    rows: list[dict[str, float | int | str | None]],
    output_dir: str | Path,
    roundoff_floor: float,
    include_log_combined: bool = True,
) -> dict[str, Path]:
    if not rows:
        raise ValueError("Taylor-Green diagnostics requires at least one row.")
    if not np.isfinite(roundoff_floor) or roundoff_floor <= 0.0:
        raise ValueError("roundoff_floor must be a positive finite value.")

    required = {"resolution", "l2_error", "linf_error", "relative_error"}
    for index, row in enumerate(rows):
        missing = required.difference(row.keys())
        if missing:
            missing_text = ", ".join(sorted(missing))
            raise ValueError(f"Row {index} is missing required fields: {missing_text}")

    destination_dir = Path(output_dir)
    destination_dir.mkdir(parents=True, exist_ok=True)

    resolutions = np.array([float(row["resolution"]) for row in rows], dtype=float)
    l2 = np.array([float(row["l2_error"]) for row in rows], dtype=float)
    linf = np.array([float(row["linf_error"]) for row in rows], dtype=float)
    relative = np.array([float(row["relative_error"]) for row in rows], dtype=float)
    floor_series = np.full_like(resolutions, float(roundoff_floor), dtype=float)

    artifacts: dict[str, Path] = {}

    def _plot_single(metric: np.ndarray, metric_label: str, filename: str) -> None:
        fig, ax = plt.subplots(figsize=(7.5, 5), constrained_layout=True)
        ax.plot(resolutions, metric, marker="o", linewidth=1.75, label=metric_label)
        ax.plot(
            resolutions,
            floor_series,
            linestyle="--",
            linewidth=1.3,
            color="#b91c1c",
            label=f"ROUND_OFF_ERROR_FLOOR={roundoff_floor:.2e}",
        )
        ax.set_yscale("log")
        ax.set_xlabel("Resolution N (NxN)")
        ax.set_ylabel("Error (log scale)")
        ax.set_title(f"Taylor-Green 2D: {metric_label} by Resolution")
        ax.grid(alpha=0.3)
        ax.legend()
        ax.text(
            0.02,
            0.02,
            "Near-floor saturation indicates roundoff dominance, not formal order proof.",
            transform=ax.transAxes,
            fontsize=8,
            bbox={"boxstyle": "round", "facecolor": "#f8fafc", "alpha": 0.8},
        )
        destination = destination_dir / filename
        fig.savefig(destination, dpi=160)
        plt.close(fig)
        artifacts[filename] = destination

    _plot_single(l2, "L2 error", "taylor_green_l2_error_by_resolution.png")
    _plot_single(linf, "L∞ error", "taylor_green_linf_error_by_resolution.png")
    _plot_single(relative, "Relative L2 error", "taylor_green_relative_l2_error_by_resolution.png")

    if include_log_combined:
        fig, ax = plt.subplots(figsize=(7.5, 5), constrained_layout=True)
        ax.plot(resolutions, l2, marker="o", linewidth=1.75, label="L2 error")
        ax.plot(resolutions, linf, marker="s", linewidth=1.75, label="L∞ error")
        ax.plot(resolutions, relative, marker="^", linewidth=1.75, label="Relative L2 error")
        ax.plot(
            resolutions,
            floor_series,
            linestyle="--",
            linewidth=1.3,
            color="#b91c1c",
            label=f"ROUND_OFF_ERROR_FLOOR={roundoff_floor:.2e}",
        )
        ax.set_yscale("log")
        ax.set_xlabel("Resolution N (NxN)")
        ax.set_ylabel("Error (log scale)")
        ax.set_title("Taylor-Green 2D: Combined Error Diagnostics")
        ax.grid(alpha=0.3)
        ax.legend()
        ax.text(
            0.02,
            0.02,
            "Floor proximity may indicate machine-precision saturation.",
            transform=ax.transAxes,
            fontsize=8,
            bbox={"boxstyle": "round", "facecolor": "#f8fafc", "alpha": 0.8},
        )
        combined = destination_dir / "taylor_green_combined_error_logscale.png"
        fig.savefig(combined, dpi=160)
        plt.close(fig)
        artifacts["taylor_green_combined_error_logscale.png"] = combined

    return artifacts
