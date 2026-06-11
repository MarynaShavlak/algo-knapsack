"""Приклад 6 — покрокова візуалізація «код ↔ таблиця».

Кожен крок = рядок із двох панелей: ліворуч код ДП з **підсвіченими активними
рядками** (колір показує, яка гілка спрацювала: «взяти» чи «значення зверху»),
праворуч — **стан таблиці K** саме на цьому кроці. Логіку див. у
``knapsack/walkthrough.py``.

Два рівні деталізації:

* **огляд** (``code_steps_*.png``) — один крок на рядок таблиці (= на предмет);
* **по клітинках** для найпоказовішого рядка — статична кураторська сітка
  (``code_walk_small_i{N}.png``) і повна анімація скану всіх клітинок рядка
  (``.gif`` + ``.mp4``).

Запуск:  ``python examples/06_code_walkthrough.py``      (українською → docs/images/)
         ``python examples/06_code_walkthrough.py en``   (англійською → docs/images/en/)
"""

# _common ПЕРШИМ: налаштовує Agg, sys.path і мову до імпорту matplotlib.pyplot
from _common import print_saved_location, save_anim, save_figure
from _items import CLASSIC, SMALL

import matplotlib.pyplot as plt  # noqa: E402

from knapsack.i18n import t  # noqa: E402
from knapsack.visualization import configure_style  # noqa: E402
from knapsack.walkthrough import (  # noqa: E402
    best_focus_row,
    build_cell_steps,
    build_overview_steps,
    draw_code_walkthrough_grid,
    pick_illustrative,
    render_code_step,
)

# Тривалість кадру анімації за типом кроку (мс): рішення «взяти/не брати»
# тримаємо довше, базові й структурні кроки прогортуємо швидше.
_DUR = {"row": 1700, "base": 900, "nofit": 1400, "take": 2400, "skip": 2400,
        "final": 3000}


def main() -> None:
    configure_style()
    print(t("Генерую покрокові панелі «код ↔ таблиця»…"))

    # 1) огляд по рядках — малий інстанс (таблиця 4×5 повністю в кадрі)
    ex = SMALL
    steps = build_overview_steps(ex.capacity, ex.weights, ex.values, ex.n, ex.names)
    fig = draw_code_walkthrough_grid(
        steps, ex.weights, ex.values, ex.names,
        t("Код ↔ таблиця K: огляд по рядках (предмет за предметом)"))
    save_figure(fig, "code_steps_small.png")
    plt.close(fig)
    print(t("  {name}: огляд, {n} кроків").format(name="code_steps_small", n=len(steps)))

    # 2) детально по клітинках — найпоказовіший рядок добираємо автоматично
    focus = best_focus_row(ex.capacity, ex.weights, ex.values, ex.n)
    cells = build_cell_steps(ex.capacity, ex.weights, ex.values, ex.n, focus, ex.names)

    grid = draw_code_walkthrough_grid(
        pick_illustrative(cells), ex.weights, ex.values, ex.names,
        t("Код ↔ таблиця K по клітинках (рядок i = {i})").format(i=focus))
    save_figure(grid, f"code_walk_small_i{focus}.png")
    plt.close(grid)

    figures = [render_code_step(s, ex.weights, ex.values, ex.names) for s in cells]
    durations = [_DUR.get(s["kind"], 1200) for s in cells]
    save_anim(figures, f"code_walk_small_i{focus}", durations)
    print(t("  {name}: по клітинках, {n} кадрів (рядок i = {i})").format(
        name=f"code_walk_small_i{focus}", n=len(figures), i=focus))

    # 3) огляд по рядках — класичний інстанс (зведені стовпці, кратні 10)
    ex = CLASSIC
    cols = list(range(0, ex.capacity + 1, 10))
    steps = build_overview_steps(ex.capacity, ex.weights, ex.values, ex.n, ex.names)
    fig = draw_code_walkthrough_grid(
        steps, ex.weights, ex.values, ex.names,
        t("Код ↔ таблиця K: огляд по рядках (класичний інстанс, стовпці кратні 10)"),
        cols=cols)
    save_figure(fig, "code_steps_classic.png")
    plt.close(fig)
    print(t("  {name}: огляд, {n} кроків").format(name="code_steps_classic", n=len(steps)))

    print_saved_location()


if __name__ == "__main__":
    main()
