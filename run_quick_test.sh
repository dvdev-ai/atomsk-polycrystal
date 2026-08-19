#!/usr/bin/env bash
# Быстрый тест: один расчёт Cu @ 300 K (уменьшенные шаги)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
LMP="/opt/homebrew/Cellar/lammps/20250722-update4/bin/lmp_serial"
POT="/opt/homebrew/Cellar/lammps/20250722-update4/share/lammps/potentials"
mkdir -p "$ROOT/potentials" "$ROOT/results/quick_Cu_300K"
ln -sf "$POT/Cu_mishin1.eam.alloy" "$ROOT/potentials/"

sed -e 's/run             10000/run             2000/' \
    -e 's/run             30000/run             5000/' \
    "$ROOT/lammps/in.tension" > "$ROOT/results/quick_Cu_300K/in.quick"

cd "$ROOT/results/quick_Cu_300K"
"$LMP" -in in.quick \
  -var material Cu -var temp 300 \
  -var datafile "$ROOT/models/Cu_poly.data" \
  -var potfile "$ROOT/potentials/Cu_mishin1.eam.alloy" \
  -var elem Cu -log log.lammps

cp stress_strain.dat "$ROOT/results/stress_strain_Cu_T300K.dat"
echo "Готово. Запустите: python3 plot_stress_strain.py"
