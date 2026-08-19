#!/usr/bin/env bash
# Установка ATOMSK + LAMMPS на macOS (Homebrew)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"

echo "=== Homebrew: LAMMPS, компилятор, LAPACK ==="
brew install lammps lapack gcc libomp git

echo "=== Сборка ATOMSK из GitHub ==="
BUILD_DIR="${TMPDIR:-/tmp}/atomsk-build-$$"
git clone --depth 1 https://github.com/pierrehirel/atomsk.git "$BUILD_DIR"
make -C "$BUILD_DIR/src" atomsk
mkdir -p "$ROOT/tools"
cp "$BUILD_DIR/src/atomsk" "$ROOT/tools/atomsk"
echo "ATOMSK: $ROOT/tools/atomsk"

echo ""
echo "=== OVITO ==="
echo "Скачайте с https://www.ovito.org/download/ (бесплатная версия для учёбы)."
echo ""
echo "=== Проверка ==="
"$ROOT/tools/atomsk" --version || true
LMP=$(command -v lmp_serial || command -v lmp_mpi || echo "lammps")
echo "LAMMPS: $LMP"
echo ""
echo "Далее:"
echo "  cd $ROOT"
echo "  ./build_models.sh"
echo "  ./run_simulations.sh    # может занять несколько часов"
echo "  python3 plot_stress_strain.py"
echo "  python3 build_presentation.py"
