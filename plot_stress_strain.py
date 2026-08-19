#!/usr/bin/env python3
"""Диаграммы σ–ε (публикационное качество)."""
from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parent
RESULTS = ROOT / "results"
FIGURES = ROOT / "figures"
FIGURES.mkdir(exist_ok=True)

try:
    plt.style.use("seaborn-v0_8-whitegrid")
except OSError:
    plt.style.use("ggplot")
plt.rcParams.update(
    {
        "font.family": "sans-serif",
        "font.size": 12,
        "axes.labelsize": 13,
        "axes.titlesize": 14,
        "legend.fontsize": 11,
        "figure.dpi": 200,
        "axes.spines.top": False,
        "axes.spines.right": False,
    }
)

STYLES = {
    0: {"color": "#2563EB", "label": "0 K (MD ≈ 1 K)", "lw": 2.2},
    300: {"color": "#EA580C", "label": "300 K", "lw": 2.2},
    600: {"color": "#DC2626", "label": "600 K", "lw": 2.2},
}

MAT_NAMES = {"Cu": "медь (Cu)", "Al": "алюминий (Al)"}


def load_curve(path: Path) -> tuple[np.ndarray, np.ndarray]:
    data = np.loadtxt(path, comments="#")
    if data.ndim == 1:
        data = data.reshape(1, -1)
    strain = np.maximum(data[:, 0], 0.0)
    stress = data[:, 1]
    return strain, stress


def smooth(y: np.ndarray, w: int = 9) -> np.ndarray:
    if len(y) < w:
        return y
    k = np.ones(w) / w
    return np.convolve(y, k, mode="same")


def plot_material(material: str) -> Path:
    fig, ax = plt.subplots(figsize=(8, 5.5))

    for temp in (0, 300, 600):
        for pattern in (
            RESULTS / f"stress_strain_{material}_T{temp}K.dat",
            RESULTS / f"{material}_T{temp}K/stress_strain_fixed.dat",
        ):
            if pattern.exists():
                fpath = pattern
                break
        else:
            print(f"Нет данных: {material} {temp} K")
            continue

        strain, stress = load_curve(fpath)
        mask = strain >= 0
        strain, stress = strain[mask], stress[mask]
        stress_s = smooth(np.clip(stress, 0, None), 7)

        st = STYLES[temp]
        ax.plot(strain * 100, stress_s, label=st["label"], color=st["color"], lw=st["lw"])

    ax.set_xlim(0, None)
    ax.set_ylim(0, None)
    ax.set_xlabel("Инженерная деформация ε, %")
    ax.set_ylabel("Напряжение σ$_{xx}$, ГПа")
    ax.set_title(f"Одноосное растяжение поликристаллического {MAT_NAMES[material]}")
    ax.legend(loc="best", framealpha=0.95)
    ax.grid(True, alpha=0.35)

    fig.tight_layout()
    out = FIGURES / f"stress_strain_{material}.png"
    fig.savefig(out, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return out


def plot_combined() -> Path:
    fig, axes = plt.subplots(1, 2, figsize=(13, 5.5), sharey=True)

    for ax, mat in zip(axes, ("Cu", "Al")):
        for temp in (0, 300, 600):
            fpath = RESULTS / f"stress_strain_{mat}_T{temp}K.dat"
            if not fpath.exists():
                continue
            s, sig = load_curve(fpath)
            st = STYLES[temp]
            ax.plot(s * 100, smooth(np.clip(sig, 0, None), 7), **{k: st[k] for k in ("color", "label", "lw")})
        ax.set_title(MAT_NAMES[mat], fontweight="bold")
        ax.set_xlabel("Деформация ε, %")
        ax.set_xlim(0, None)
        ax.set_ylim(0, None)
        ax.legend(loc="best", fontsize=9)
        ax.grid(True, alpha=0.35)

    axes[0].set_ylabel("σ$_{xx}$, ГПа")
    fig.suptitle("Поликристаллы: диаграммы напряжение–деформация", fontsize=15, y=1.02)
    fig.tight_layout()
    out = FIGURES / "stress_strain_combined.png"
    fig.savefig(out, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return out


def plot_summary_table() -> Path:
    """Сводка: σ_max при ε≈3%."""
    rows = []
    for mat in ("Cu", "Al"):
        for temp in (0, 300, 600):
            f = RESULTS / f"stress_strain_{mat}_T{temp}K.dat"
            if not f.exists():
                continue
            e, s = load_curve(f)
            rows.append((mat, temp, e.max() * 100, s.max()))

    fig, ax = plt.subplots(figsize=(7, 3))
    ax.axis("off")
    lines = ["Материал | T (K) | ε_max (%) | σ_max (ГПа)", "-" * 42]
    for mat, t, em, sm in rows:
        lines.append(f"{mat:6} | {t:5} | {em:8.2f} | {sm:8.3f}")
    ax.text(0.05, 0.95, "\n".join(lines), va="top", family="monospace", fontsize=11)
    ax.set_title("Сводка результатов MD", pad=20)
    out = FIGURES / "summary_table.png"
    fig.savefig(out, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return out


def main() -> None:
    for mat in ("Cu", "Al"):
        print(f"Сохранено: {plot_material(mat)}")
    print(f"Сохранено: {plot_combined()}")
    print(f"Сохранено: {plot_summary_table()}")


if __name__ == "__main__":
    main()
