"""Приклад 3 — ДП на класичному інстансі (W = 50) + порівняння трьох підходів.

Таблиця тут уже 4×51 — над кожною клітинкою сидіти не будемо. Показуємо зведену
картину (стовпці, кратні 10: між ними значення не змінюються, бо всі ваги кратні
10), відповідь 220, відновлення набору {П2, П3} і чесне порівняння на ОДНОМУ
інстансі: повний перебір і ДП дають ту саму відповідь, жадібний — ні.

Запуск:  ``python examples/03_dp_classic.py``        (українською → docs/images/)
         ``python examples/03_dp_classic.py en``     (англійською → docs/images/en/)
"""

# _common ПЕРШИМ: налаштовує Agg, sys.path і мову до імпорту matplotlib.pyplot
from _common import describe_instance, print_saved_location, report_chosen, save_figure
from _items import CLASSIC

from knapsack.core import (  # noqa: E402
    Item,
    knapsack_brute_force,
    knapsack_dp_steps,
    knapsack_greedy,
    knapsack_recursive,
    reconstruct_steps,
)
from knapsack.i18n import t  # noqa: E402
from knapsack.visualization import (  # noqa: E402
    configure_style,
    draw_backtrack,
    draw_dp_table_standalone,
    format_combo,
    print_dp_table,
)

#: Стовпці зведеної таблиці: усі ваги кратні 10, тож значення змінюються лише тут.
COLS = [0, 10, 20, 30, 40, 50]


def main() -> None:
    configure_style()
    ex = CLASSIC
    weights, values, capacity, n = ex.weights, ex.values, ex.capacity, ex.n
    names = ex.names

    describe_instance(ex)

    # 1) повна таблиця (51 стовпець) + зведена текстова версія
    best, K, steps = knapsack_dp_steps(capacity, weights, values, n)
    print()
    print(t("Таблиця має {rows} рядки × {cols} стовпець (w = 0…{W}); показуємо кратні 10:").format(
        rows=n + 1, cols=capacity + 1, W=capacity))
    print()
    print_dp_table(K, names, cols=COLS)
    print()
    print(t("ВІДПОВІДЬ = K[{n}][{W}] = {v}").format(n=n, W=capacity, v=best))

    save_figure(draw_dp_table_standalone(
        K, weights, values, names, cols=COLS, answer=(n, capacity),
        title=t("Таблиця K для W = 50 (зведено до стовпців, кратних 10)"),
        note=t("між показаними стовпцями значення не змінюються: всі ваги кратні 10")),
        "dp_table_classic.png")

    # 2) відновлення набору зворотним проходом (усі зупинки — на кратних 10)
    chosen, recon = reconstruct_steps(K, weights, capacity)
    print()
    report_chosen(chosen, ex)
    save_figure(draw_backtrack(
        K, weights, values, names, recon, cols=COLS,
        title=t("Зворотний хід по зведеній таблиці: {v} = 120 + 100").format(v=best),
        note=t("шлях зупиняється на w = 50 → 20 → 0 — всі зупинки потрапляють у показані стовпці")),
        "backtrack_classic.png")

    # 3) порівняння трьох підходів на одному інстансі
    print()
    print("=" * 60)
    print(t("Порівняння підходів на інстансі «{label}»").format(label=t(ex.label)))
    print("=" * 60)
    rec = knapsack_recursive(capacity, weights, values, n)
    bf_value, bf_combo = knapsack_brute_force(capacity, weights, values)
    greedy = knapsack_greedy([Item(w, v) for w, v in zip(weights, values)], capacity)
    print(t("Повний перебір (рекурсія):   {v}").format(v=rec))
    print(t("Повний перебір (itertools):  {v}, набір {combo}").format(
        v=bf_value, combo=format_combo(bf_combo, names)))
    print(t("Динамічне програмування:     {v}, набір {combo}").format(
        v=best, combo=format_combo(chosen, names)))
    print(t("Жадібний метод:              {v}  ← НЕ оптимум (втрачає {d})").format(
        v=greedy, d=best - greedy))

    print_saved_location()


if __name__ == "__main__":
    main()
