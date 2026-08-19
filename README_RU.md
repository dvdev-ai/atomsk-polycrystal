# Курсовая: ATOMSK + LAMMPS + OVITO

Поликристаллические **Cu** и **Al**, одноосное растяжение, диаграммы σ–ε при **0, 300 и 600 K**.

## Полностью автоматический режим (ничего не делать)

Если расчёты уже запущены (`run_simulations.sh`), в фоне работает **`auto_finish.sh`**:
дождётся LAMMPS → построит графики → сделает скриншоты OVITO → обновит PowerPoint и откроет файл.

```bash
cd ~/Downloads/atomsk-polycrystal-tension
./auto_finish.sh   # или уже запущен в фоне
```

Скриншоты OVITO без ручного открытия программы:

```bash
python3 render_ovito_screenshots.py
```

## Быстрый старт (macOS)

```bash
cd ~/Downloads/atomsk-polycrystal-tension
chmod +x *.sh
./install_macos.sh      # если ещё не установлено
./build_models.sh       # модели ATOMSK (~1 мин)
./run_simulations.sh    # 6 расчётов LAMMPS (несколько часов)
python3 plot_stress_strain.py
python3 build_presentation.py
```

**OVITO:** https://www.ovito.org/download/ — откройте `models/poly/Cu_poly.cfg`, раскрасьте по свойству `grainID`.

## Что уже сделано на вашем Mac

- **LAMMPS** установлен (`brew install lammps`), исполняемый файл: `lmp_serial`
- **ATOMSK** собран в `tools/atomsk`
- Модели: `models/Cu_poly.data`, `models/Al_poly.data` (~18k и ~13k атомов)

## Структура проекта

| Папка/файл | Назначение |
|------------|------------|
| `build_models.sh` | Поликристалл 60×60×60 Å, 8 зёрен |
| `lammps/in.tension` | Минимизация, NPT, растяжение по X |
| `run_simulations.sh` | Cu/Al × 0/300/600 K |
| `results/` | Логи и `stress_strain_*.dat` |
| `figures/` | Графики PNG для отчёта и презентации |
| `presentation/` | PowerPoint |

## Температура 0 K

В классической MD нельзя задать ровно 0 K в термостате. В скриптах **0 K** соответствует **T = 1 K** после минимизации энергии — укажите это в отчёте.

## OVITO — визуализация

1. File → Load File → `models/poly/Cu_poly.cfg`
2. Add modification → **Color coding** → Property `grainID`
3. Для траектории: `results/Cu_T300K/dump_tension.lammpstrj`
4. Add → **Slice** или **Common neighbor analysis** для дефектов при растяжении

## Ускорение расчётов

- Уменьшите зёрна в `params/polycrystal_*.txt`: `random 4` и `box 40 40 40`
- В `lammps/in.tension` уменьшите `run 30000` → `run 10000`
- Используйте `lmp_mpi -np 4` вместо `lmp_serial`

## Литература для отчёта

- P. Hirel, Atomsk: https://atomsk.univ-lille.fr
- Mishin et al., EAM для Cu; Zhou et al. для Al (потенциалы из LAMMPS)
- Tschopp et al., uniaxial tension tutorial (ICME / Mississippi State)

## Презентация

`presentation/ATOMSK_курсовая.pptx` — откройте в PowerPoint, вставьте свои скриншоты OVITO и графики из `figures/`.
