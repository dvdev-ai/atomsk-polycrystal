#!/usr/bin/env bash
# Полная автоматизация: дождаться LAMMPS → графики → OVITO → презентация
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"
LOG="$ROOT/results/auto_finish.log"
exec > >(tee -a "$LOG") 2>&1

echo "=== auto_finish: $(date) ==="

# Ждём завершения run_simulations.sh (если запущен)
while pgrep -f "run_simulations.sh" >/dev/null 2>&1 || pgrep -f "lmp_serial.*in.tension" >/dev/null 2>&1; do
  echo "$(date +%H:%M:%S) Расчёты LAMMPS ещё идут..."
  sleep 120
done

echo "LAMMPS завершён. Сбор результатов..."
# Копируем stress_strain из подпапок, если нужно
for d in "$ROOT"/results/*_T*K; do
  [[ -d "$d" ]] || continue
  base=$(basename "$d")
  mat=$(echo "$base" | cut -d_ -f1)
  temp=$(echo "$base" | sed 's/.*_T\([0-9]*\)K/\1/')
  if [[ -f "$d/stress_strain.dat" ]]; then
    cp -f "$d/stress_strain.dat" "$ROOT/results/stress_strain_${mat}_T${temp}K.dat"
  fi
done

python3 "$ROOT/rebuild_stress_strain.py"
python3 "$ROOT/plot_stress_strain.py"
python3 "$ROOT/render_ovito_screenshots.py"
python3 "$ROOT/build_presentation.py"

echo "=== Готово: $(date) ==="
echo "Презентация: $ROOT/Презентация/ATOMSK_курсовая.pptx"
echo "Скриншоты OVITO: $ROOT/figures/ovito_*.png"
open "$ROOT/Презентация/ATOMSK_курсовая.pptx" 2>/dev/null || true
