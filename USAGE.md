# Швидкий старт

**🇺🇦 Українська**  ·  [🇬🇧 English](USAGE.en.md)

> Частина документації проєкту [«Задача про рюкзак: повний перебір та динамічне програмування»](README.md). Тут — команди встановлення, запуску прикладів і тестів. Структуру репозиторію див. у [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md).

> **Потрібен Python ≥ 3.8.** Код використовує `from __future__ import annotations`, тож працює на 3.8+ (розробляється й тестується на 3.12).

```bash
# 1. Залежності
pip install -r requirements.txt
# або встановити пакет у режимі розробки:
pip install -e .
# (опційно) MP4-відео анімацій без root — додає ffmpeg із пакета imageio-ffmpeg:
pip install -e ".[video]"

# 2. Відтворити всі рисунки й текстові виводи (українською → docs/images/)
python examples/00_intro_items.py          # умова задачі: предмети та місткість
python examples/01_brute_force.py          # повний перебір + вибух 2^n
python examples/02_dp_small.py             # таблиця ДП по клітинках + відновлення
python examples/03_dp_classic.py           # ДП на класичному інстансі + порівняння
python examples/04_greedy_limitation.py    # жадібний контрприклад (160 проти 220)
python examples/05_animations.py           # анімації GIF+MP4
python examples/06_code_walkthrough.py     # панелі «код ↔ таблиця»

# 3. Те саме англійською (→ docs/images/en/) — додайте аргумент `en`:
python examples/01_brute_force.py en
python examples/05_animations.py en
```

Сім скриптів разом генерують **22 статичні рисунки** (`.png`), **5 GIF-анімацій** (`.gif`) і **5 MP4-відео** (`.mp4`) у [`docs/images/`](docs/images) та друкують текстові виводи в консоль; з аргументом `en` ті самі медіа англійською потрапляють у [`docs/images/en/`](docs/images/en). Виконуються за кілька секунд (повний перебір інстансу на 20 предметів у `01` свідомо «думає» ~1–2 секунди — у цьому й суть демонстрації). **MP4** кодуються лише за наявності `ffmpeg` (системного або з `imageio-ffmpeg`); без нього збираються самі GIF — збірка не падає.

Перевірити коректність алгоритмів (еталоном слугує сам повний перебір — для малих `n` він гарантовано точний):

```bash
python tests/test_core.py     # коректність ядра (без додаткових залежностей)
python tests/test_smoke.py    # smoke: рендер, GIF та i18n не падають (matplotlib, pillow)
# або обидва через pytest (pip install -e ".[dev]"):
pytest
```

Тести `test_core.py` покривають збіг відповідей повного перебору (обох версій) і ДП на двох навчальних інстансах та на серії випадкових, допустимість і точність відновленого набору, журнал інструментованих версій, жадібний контрприклад (160 на класичному інстансі) та крайові випадки: порожній список предметів, нульову місткість, предмет важчий за рюкзак, «усе влазить». Smoke-тести `test_smoke.py` перевіряють, що всі функції малювання і збірка GIF виконуються без помилок, а **всі кириличні підписи мають англійський переклад** (динамічний аудит `missing_translations` + статичний AST-аудит літералів `t("…")`).

Мінімальне використання як бібліотеки:

```python
from knapsack import knapsack_dp, knapsack_dp_table, reconstruct_items

weights, values, capacity = [10, 20, 30], [60, 100, 120], 50
best = knapsack_dp(capacity, weights, values, len(values))       # 220
K = knapsack_dp_table(capacity, weights, values, len(values))
chosen = reconstruct_items(K, weights, capacity)                 # [1, 2] → П2 і П3
```
