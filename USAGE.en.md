# Quick start

[🇺🇦 Українська](USAGE.md)  ·  **🇬🇧 English**

> Part of the documentation of [“The Knapsack Problem: Brute Force and Dynamic Programming”](README.en.md). This page covers installation, running the examples and the tests. For the repository layout see [PROJECT_STRUCTURE.en.md](PROJECT_STRUCTURE.en.md).

> **Python ≥ 3.8 required.** The code uses `from __future__ import annotations`, so it runs on 3.8+ (developed and tested on 3.12).

```bash
# 1. Dependencies
pip install -r requirements.txt
# or install the package in development mode:
pip install -e .
# (optional) MP4 animations without root — brings ffmpeg via the imageio-ffmpeg package:
pip install -e ".[video]"

# 2. Reproduce all figures and console outputs (Ukrainian → docs/images/)
python examples/00_intro_items.py          # the problem: items and capacity
python examples/01_brute_force.py          # brute force + the 2^n explosion
python examples/02_dp_small.py             # the DP table cell by cell + reconstruction
python examples/03_dp_classic.py           # DP on the classic instance + comparison
python examples/04_greedy_limitation.py    # the greedy counterexample (160 vs 220)
python examples/05_animations.py           # GIF+MP4 animations
python examples/06_code_walkthrough.py     # code ↔ table panels

# 3. The same in English (→ docs/images/en/) — add the `en` argument:
python examples/01_brute_force.py en
python examples/05_animations.py en
```

The seven scripts together generate **22 static figures** (`.png`), **5 GIF animations** (`.gif`) and **5 MP4 videos** (`.mp4`) in [`docs/images/`](docs/images) and print text outputs to the console; with the `en` argument the same media in English go to [`docs/images/en/`](docs/images/en). They finish in a few seconds (the brute force over the 20-item instance in `01` deliberately "thinks" for ~1–2 seconds — that is the point of the demonstration). **MP4** files are encoded only when `ffmpeg` is available (system-wide or from `imageio-ffmpeg`); without it only GIFs are built — the build never fails.

Check the correctness of the algorithms (brute force itself serves as the reference — for small `n` it is exact by construction):

```bash
python tests/test_core.py     # core correctness (no extra dependencies)
python tests/test_smoke.py    # smoke: rendering, GIF and i18n do not crash (matplotlib, pillow)
# or both via pytest (pip install -e ".[dev]"):
pytest
```

The `test_core.py` tests cover the agreement of both brute-force versions and DP on the two teaching instances and on a series of random ones, the feasibility and exactness of the reconstructed set, the journals of the instrumented versions, the greedy counterexample (160 on the classic instance) and the edge cases: an empty item list, zero capacity, an item heavier than the knapsack, "everything fits". The `test_smoke.py` tests verify that every drawing function and the GIF assembly run without errors, and that **every Cyrillic label has an English translation** (the dynamic `missing_translations` audit plus a static AST audit of `t("…")` literals).

Minimal use as a library:

```python
from knapsack import knapsack_dp, knapsack_dp_table, reconstruct_items

weights, values, capacity = [10, 20, 30], [60, 100, 120], 50
best = knapsack_dp(capacity, weights, values, len(values))       # 220
K = knapsack_dp_table(capacity, weights, values, len(values))
chosen = reconstruct_items(K, weights, capacity)                 # [1, 2] → I2 and I3
```
