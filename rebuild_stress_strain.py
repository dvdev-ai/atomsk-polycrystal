#!/usr/bin/env python3
"""Восстановить ε из шагов MD (исправление бага variable L0 equal lx)."""
from __future__ import annotations

import re
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent
RESULTS = ROOT / "results"

TIMESTEP = 0.001  # ps
PRINT_EVERY = 200
ERATE_PS = 1.0e9 / 1.0e12  # 0.001 /ps


def read_l0(log_path: Path) -> float:
    text = log_path.read_text()
    m = re.search(r"^L0=([0-9.]+)", text, re.M)
    if m:
        return float(m.group(1))
    # fallback: lx после equilibration из thermo
    for line in reversed(text.splitlines()):
        if line.strip().startswith("10000 ") and len(line.split()) >= 5:
            return float(line.split()[4])
    raise ValueError(f"L0 not found in {log_path}")


def rebuild_one(run_dir: Path) -> Path:
    raw = run_dir / "stress_strain.dat"
    log = run_dir / "log.lammps"
    if not raw.exists() or not log.exists():
        raise FileNotFoundError(run_dir)

    L0 = read_l0(log)
    data = np.loadtxt(raw, comments="#")
    n = len(data)
    steps = PRINT_EVERY * np.arange(1, n + 1)
    time_ps = steps * TIMESTEP
    strain = ERATE_PS * time_ps  # ε = ε̇·t при постоянной скорости

    out_cols = np.column_stack([strain, data[:, 1], data[:, 2], data[:, 3]])
    out = run_dir / "stress_strain_fixed.dat"
    np.savetxt(
        out,
        out_cols,
        header="strain sxx_GPa syy_GPa szz_GPa",
        comments="# ",
        fmt="%.8e",
    )

    dest = RESULTS / f"stress_strain_{run_dir.name}.dat"
    np.savetxt(
        dest,
        out_cols[:, :2],
        header="# strain  sxx_GPa",
        comments="",
        fmt="%.8e",
    )
    return dest


def main() -> None:
    for d in sorted(RESULTS.glob("*_T*K")):
        if (d / "stress_strain.dat").exists():
            p = rebuild_one(d)
            print(f"OK {d.name} -> {p.name}")


if __name__ == "__main__":
    main()
