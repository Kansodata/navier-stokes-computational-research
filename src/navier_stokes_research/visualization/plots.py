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
