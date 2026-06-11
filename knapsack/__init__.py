"""Навчальна реалізація та візуалізація задачі про рюкзак 0/1.

Пакет розділено на модулі:

* :mod:`knapsack.core` — самі алгоритми (повний перебір, жадібний, динамічне
  програмування), інструментовані версії з журналами кроків та відновлення
  обраного набору зворотним проходом по таблиці;
* :mod:`knapsack.visualization` — функції малювання предметів, таблиці ДП,
  перебору підмножин та покрокових кадрів (потребують ``matplotlib``);
* :mod:`knapsack.walkthrough` — покрокова візуалізація «код ↔ таблиця» з
  підсвічуванням активних рядків коду (потребує ``matplotlib``);
* :mod:`knapsack.animation` — збірка анімацій: GIF (Pillow) + MP4 (ffmpeg).

``core`` та ``i18n`` лишаються без важких залежностей, тож ``import knapsack``
не тягне ``matplotlib``; модулі малювання імпортують явно (``from
knapsack.visualization import …`` / ``… .walkthrough import …``).

Приклад::

    from knapsack import knapsack_dp, knapsack_dp_table, reconstruct_items

    weights, values, capacity = [10, 20, 30], [60, 100, 120], 50
    best = knapsack_dp(capacity, weights, values, len(values))        # 220
    K = knapsack_dp_table(capacity, weights, values, len(values))
    chosen = reconstruct_items(K, weights, capacity)                  # [1, 2]
"""

from .core import (
    Item,
    brute_force_steps,
    greedy_steps,
    knapsack_brute_force,
    knapsack_dp,
    knapsack_dp_steps,
    knapsack_dp_table,
    knapsack_greedy,
    knapsack_recursive,
    reconstruct_items,
    reconstruct_steps,
)
from .i18n import get_lang, set_lang, t

__all__ = [
    "Item",
    "knapsack_recursive",
    "knapsack_brute_force",
    "brute_force_steps",
    "knapsack_greedy",
    "greedy_steps",
    "knapsack_dp",
    "knapsack_dp_table",
    "knapsack_dp_steps",
    "reconstruct_items",
    "reconstruct_steps",
    # двомовні підписи (uk/en) — без важких залежностей, тож безпечно тут
    "t",
    "set_lang",
    "get_lang",
]

# Єдине джерело правди для версії пакета: pyproject.toml читає його звідси через
# [tool.setuptools.dynamic] version = { attr = "knapsack.__version__" }.
__version__ = "1.0.0"
