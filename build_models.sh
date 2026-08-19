#!/usr/bin/env bash
# Генерация поликристаллических моделей Cu и Al (ATOMSK)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"

ATOMSK="${ATOMSK:-atomsk}"
if ! command -v "$ATOMSK" >/dev/null 2>&1; then
  if [[ -x "$ROOT/tools/atomsk" ]]; then
    ATOMSK="$ROOT/tools/atomsk"
  elif [[ -x /tmp/atomsk-src/src/atomsk ]]; then
    ATOMSK="/tmp/atomsk-src/src/atomsk"
  else
    echo "Ошибка: atomsk не найден. Запустите: ./install_macos.sh"
    exit 1
  fi
fi

mkdir -p models/seeds models/poly

echo "=== Создание элементарных ячеек ==="
"$ATOMSK" --create fcc 3.615 Cu models/seeds/Cu_seed.xsf
"$ATOMSK" --create fcc 4.046 Al models/seeds/Al_seed.xsf

echo "=== Поликристалл Cu (8 зёрен, 60×60×60 Å) ==="
"$ATOMSK" --polycrystal models/seeds/Cu_seed.xsf params/polycrystal_cu.txt \
  models/poly/Cu_poly.cfg -wrap

echo "=== Поликристалл Al ==="
"$ATOMSK" --polycrystal models/seeds/Al_seed.xsf params/polycrystal_al.txt \
  models/poly/Al_poly.cfg -wrap

echo "=== Экспорт в LAMMPS data ==="
"$ATOMSK" models/poly/Cu_poly.cfg lammps models/Cu_poly.data
"$ATOMSK" models/poly/Al_poly.cfg lammps models/Al_poly.data
for f in models/Cu_poly.data models/Al_poly.data; do
  [[ -f "$f" ]] || mv -f "${f}.lmp" "$f" 2>/dev/null || true
done

echo "Готово:"
echo "  models/Cu_poly.data"
echo "  models/Al_poly.data"
echo "  models/poly/*.cfg  — для OVITO (File → Load File, колорировать по grainID)"
