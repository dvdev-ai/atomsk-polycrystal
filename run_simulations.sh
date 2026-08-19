#!/usr/bin/env bash
# Запуск всех расчётов: Cu/Al × 0/300/600 K
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"

LMP="${LMP:-}"
for c in lmp_serial lmp_mpi lmp; do
  if command -v "$c" >/dev/null 2>&1; then LMP="$c"; break; fi
done
if [[ -z "$LMP" ]]; then
  LMP="/opt/homebrew/Cellar/lammps/20250722-update4/bin/lmp_serial"
fi
if [[ ! -x "$LMP" ]] && ! command -v "$LMP" >/dev/null 2>&1; then
  echo "LAMMPS не найден. Установите: brew install lammps"
  exit 1
fi

[[ -f models/Cu_poly.data ]] || { echo "Сначала: ./build_models.sh"; exit 1; }

POT_DIR="$(brew --prefix lammps 2>/dev/null)/share/lammps/potentials"
POT_DIR="${POT_DIR:-/opt/homebrew/Cellar/lammps/20250722-update4/share/lammps/potentials}"
mkdir -p potentials results
ln -sf "$POT_DIR/Cu_mishin1.eam.alloy" potentials/
ln -sf "$POT_DIR/Al_zhou.eam.alloy" potentials/

run_one() {
  local mat="$1" temp_label="$2" temp_val="$3" data pot elem
  case "$mat" in
    Cu) data="$ROOT/models/Cu_poly.data"; pot="$ROOT/potentials/Cu_mishin1.eam.alloy"; elem=Cu ;;
    Al) data="$ROOT/models/Al_poly.data"; pot="$ROOT/potentials/Al_zhou.eam.alloy"; elem=Al ;;
    *) echo "Unknown material $mat"; return 1 ;;
  esac
  local outdir="$ROOT/results/${mat}_T${temp_label}K"
  mkdir -p "$outdir"
  echo ">>> $mat @ ${temp_label} K (T=${temp_val})"
  (
    cd "$outdir"
    "$LMP" -in "$ROOT/lammps/in.tension" \
      -var material "$mat" \
      -var temp "$temp_val" \
      -var datafile "$data" \
      -var potfile "$pot" \
      -var elem "$elem" \
      -log log.lammps
    cp -f stress_strain.dat "$ROOT/results/stress_strain_${mat}_T${temp_label}K.dat" 2>/dev/null || true
  )
}

# 0 K → T=1 K в MD; подпись на графиках остаётся «0 K»
for mat in Cu Al; do
  for t in "0:1" "300:300" "600:600"; do
    label="${t%%:*}"
    val="${t##*:}"
    run_one "$mat" "$label" "$val"
  done
done

echo "Все расчёты завершены. Построение графиков: python3 plot_stress_strain.py"
