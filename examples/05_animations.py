"""Приклад 5 — анімації GIF (+ MP4 за наявності ffmpeg).

Чотири сюжети, кожен зібрано з тих самих функцій малювання, що й статичні
рисунки:

* ``subsets_classic`` — повний перебір: підмножини з'являються по одній,
  лідер підсвічується;
* ``dp_fill_small`` — заповнення таблиці ДП клітинка за клітинкою з формулою
  переходу в кадрі;
* ``dp_evolution_small`` — таблиця «дозріває» рядок за рядком (+ статична
  зведена сітка);
* ``backtrack_small`` — зворотний хід: як із готової таблиці виймається набір.

Запуск:  ``python examples/05_animations.py``        (українською → docs/images/)
         ``python examples/05_animations.py en``     (англійською → docs/images/en/)
"""

# _common ПЕРШИМ: налаштовує Agg, sys.path і мову до імпорту matplotlib.pyplot
from _common import print_saved_location, save_anim, save_figure
from _items import CLASSIC, SMALL

from knapsack.core import brute_force_steps, knapsack_dp_steps, reconstruct_steps  # noqa: E402
from knapsack.i18n import t  # noqa: E402
from knapsack.visualization import (  # noqa: E402
    configure_style,
    draw_backtrack_frame,
    draw_dp_cell_frame,
    draw_dp_evolution,
    draw_dp_table_standalone,
    draw_subsets,
)


def animate_subsets() -> None:
    """Перебір підмножин класичного інстансу: кадр = одна підмножина."""
    ex = CLASSIC
    _, _, steps = brute_force_steps(ex.capacity, ex.weights, ex.values)
    figures, durations = [], []
    for k, s in enumerate(steps):
        figures.append(draw_subsets(steps, ex.weights, ex.values, ex.names,
                                    ex.capacity, upto=k))
        durations.append(1900 if s["improved"] else 1100)
    durations[-1] = 3200   # фінальний стан тримаємо найдовше
    save_anim(figures, "subsets_classic", durations)
    print(t("  {name}: {n} кадрів").format(name="subsets_classic", n=len(durations)))


def animate_dp_fill() -> None:
    """Заповнення таблиці ДП малого інстансу: кадр = одна клітинка з формулою."""
    ex = SMALL
    _, K, steps = knapsack_dp_steps(ex.capacity, ex.weights, ex.values, ex.n)
    figures, durations = [], []
    dur = {"base": 750, "nofit": 1500, "take": 2300, "skip": 2300}
    for s in steps:
        if s["i"] == 0:
            continue          # базовий рядок нулів окремих кадрів не вартий
        figures.append(draw_dp_cell_frame(K, ex.weights, ex.values, ex.names,
                                          s["i"], s["w"]))
        durations.append(dur[s["kind"]])
    durations[-1] = 3500      # клітинка-відповідь
    save_anim(figures, "dp_fill_small", durations)
    print(t("  {name}: {n} кадрів").format(name="dp_fill_small", n=len(durations)))


def animate_dp_evolution() -> None:
    """Таблиця «дозріває» рядок за рядком: кадр = один заповнений рядок."""
    ex = SMALL
    _, K, _ = knapsack_dp_steps(ex.capacity, ex.weights, ex.values, ex.n)

    # статична зведена сітка всіх станів
    save_figure(draw_dp_evolution(
        K, ex.weights, ex.values, ex.names,
        t("Еволюція таблиці K: рядок за рядком (малий інстанс)")),
        "dp_evolution_small.png")

    figures, durations = [], []
    for i in range(ex.n + 1):
        title = (t("Рядок i=0: база (нулі)") if i == 0
                 else t("Після рядка i={i} (+{name})").format(i=i, name=ex.names[i - 1]))
        figures.append(draw_dp_table_standalone(
            K, ex.weights, ex.values, ex.names, upto=(i, ex.capacity), title=title,
            answer=(ex.n, ex.capacity) if i == ex.n else None))
        durations.append(1800)
    durations[-1] = 3200
    save_anim(figures, "dp_evolution_small", durations)
    print(t("  {name}: {n} кадрів").format(name="dp_evolution_small", n=len(durations)))


def animate_backtrack() -> None:
    """Зворотний хід по готовій таблиці: кадр = одне порівняння зі «зверху»."""
    ex = SMALL
    _, K, _ = knapsack_dp_steps(ex.capacity, ex.weights, ex.values, ex.n)
    _, recon = reconstruct_steps(K, ex.weights, ex.capacity)
    figures = [draw_backtrack_frame(K, ex.weights, ex.values, ex.names, recon, k)
               for k in range(len(recon))]
    durations = [2600] * len(figures)
    durations[-1] = 3400
    save_anim(figures, "backtrack_small", durations)
    print(t("  {name}: {n} кадрів").format(name="backtrack_small", n=len(durations)))


def main() -> None:
    configure_style()
    print(t("Генерую GIF-анімації (та MP4, якщо доступний ffmpeg)…"))
    animate_subsets()
    animate_dp_fill()
    animate_dp_evolution()
    animate_backtrack()
    print_saved_location()


if __name__ == "__main__":
    main()
