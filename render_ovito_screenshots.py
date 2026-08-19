#!/usr/bin/env python3
"""Скриншоты OVITO для курсовой (единый стиль: grainID, белый фон)."""
from __future__ import annotations

import math
from pathlib import Path

from ovito.io import import_file
from ovito.modifiers import ColorCodingModifier
from ovito.vis import Viewport

ROOT = Path(__file__).resolve().parent
FIG = ROOT / "figures"
FIG.mkdir(exist_ok=True)

# Общие параметры камеры (как у «хороших» кубов Cu/Al)
CAM_POS = (95, -110, 85)
CAM_DIR = (-0.9, 1.0, -0.55)
FOV_DEG = 42
SIZE_MAIN = (1920, 1080)
BG_WHITE = (1.0, 1.0, 1.0)


def render_polycrystal(cfg: Path, out: Path) -> None:
    pipeline = import_file(str(cfg))
    pipeline.modifiers.append(ColorCodingModifier(property="grainID"))
    pipeline.add_to_scene()

    vp = Viewport(type=Viewport.Type.Perspective)
    vp.camera_pos = CAM_POS
    vp.camera_dir = CAM_DIR
    vp.fov = math.radians(FOV_DEG)
    vp.render_image(filename=str(out), size=SIZE_MAIN, background=BG_WHITE)


def render_tension(dump: Path, out: Path, frame: int = -1) -> None:
    """Один кадр растяжения: белый фон, одна коробка, без дублей."""
    pipeline = import_file(str(dump))
    # В dump нет grainID (только id type x y z) — раскраска по X (направление растяжения)
    pipeline.modifiers.append(ColorCodingModifier(property="Position.X"))
    pipeline.add_to_scene()

    # Не рисовать полупрозрачные периодические копии (эффект «двух кубов»)
    try:
        pipeline.source.vis.enabled = False
    except AttributeError:
        pass

    vp = Viewport(type=Viewport.Type.Perspective)
    vp.camera_pos = CAM_POS
    vp.camera_dir = CAM_DIR
    vp.fov = math.radians(FOV_DEG)
    vp.zoom_all(size=SIZE_MAIN)
    vp.render_image(
        filename=str(out),
        size=SIZE_MAIN,
        background=BG_WHITE,
        frame=frame,
    )


def main() -> None:
    jobs = [
        (ROOT / "models/poly/Cu_poly.cfg", FIG / "ovito_Cu_polycrystal.png"),
        (ROOT / "models/poly/Al_poly.cfg", FIG / "ovito_Al_polycrystal.png"),
    ]
    for cfg, out in jobs:
        if not cfg.exists():
            print(f"Пропуск (нет файла): {cfg}")
            continue
        print(f"Рендер: {cfg.name} -> {out.name}")
        render_polycrystal(cfg, out)

    dumps = [
        ROOT / "results/Cu_T300K/dump_tension.lammpstrj",
        ROOT / "results/quick_Cu_300K/dump_tension.lammpstrj",
    ]
    for dump in dumps:
        if dump.exists():
            out = FIG / f"ovito_tension_{dump.parent.name}.png"
            print(f"Кадр растяжения (финальный): {dump}")
            render_tension(dump, out, frame=-1)
            break

    print(f"Скриншоты в {FIG}/")
    print("Для презентации используйте только ovito_Cu_*, ovito_Al_*, один ovito_tension_*.")


if __name__ == "__main__":
    main()
