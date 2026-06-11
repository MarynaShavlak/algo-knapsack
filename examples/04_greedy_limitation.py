"""Приклад 4 — обмеження: чому жадібний метод НЕ розв'язує задачу 0/1.

Жадібна стратегія «бери найвигідніше за грам, поки влазить» працює для
ДРОБОВОГО рюкзака, але для задачі 0/1 — це лише швидка евристика. Тут — повний
хід жадібного на класичному інстансі (160) проти оптимуму (220) та рисунок-
контрприклад: жадібний лишає 20 одиниць місткості порожніми.

Запуск:  ``python examples/04_greedy_limitation.py``      (українською → docs/images/)
         ``python examples/04_greedy_limitation.py en``   (англійською → docs/images/en/)
"""

# _common ПЕРШИМ: налаштовує Agg, sys.path і мову до імпорту matplotlib.pyplot
from _common import describe_instance, print_saved_location, save_figure
from _items import CLASSIC

from knapsack.core import (  # noqa: E402
    Item,
    greedy_steps,
    knapsack_dp_table,
    knapsack_greedy,
    reconstruct_items,
)
from knapsack.i18n import t  # noqa: E402
from knapsack.visualization import configure_style, draw_fill_plans  # noqa: E402


def main() -> None:
    configure_style()
    ex = CLASSIC
    weights, values, capacity, n = ex.weights, ex.values, ex.capacity, ex.n
    names = ex.names

    describe_instance(ex)

    # 1) крок 1 жадібного: питома цінність (вартість / вага)
    print()
    print(t("Питома цінність (вартість / вага):"))
    for i in range(n):
        print(t("  {name}: {v} / {w} = {r}").format(
            name=names[i], v=values[i], w=weights[i], r=values[i] / weights[i]))

    # 2) хід жадібного: сортуємо за ratio і беремо, поки влазить
    total, steps = greedy_steps(list(zip(weights, values)), capacity)
    print()
    print(t("Хід жадібного (за спаданням ratio):"))
    for s in steps:
        name = names[s["index"]]
        if s["taken"]:
            print(t("  {name} (вага {w}): взято   → вільно {b} → {a}, цінність {tot}").format(
                name=name, w=s["weight"], b=s["free_before"], a=s["free_after"],
                tot=s["total_after"]))
        else:
            print(t("  {name} (вага {w}): пропуск (треба {w} > вільно {b})").format(
                name=name, w=s["weight"], b=s["free_before"]))

    # 3) той самий результат дає й код із конспекту (клас Item)
    greedy_value = knapsack_greedy([Item(w, v) for w, v in zip(weights, values)], capacity)
    print()
    print(t("Результат жадібного методу: {v}").format(v=greedy_value))

    # 4) контрприклад: жадібний проти оптимуму на смугах заповнення
    K = knapsack_dp_table(capacity, weights, values, n)
    optimum = K[n][capacity]
    chosen = reconstruct_items(K, weights, capacity)
    greedy_items = [s["index"] for s in steps if s["taken"]]
    print(t("Оптимум (ДП на тому самому інстансі): {v}").format(v=optimum))
    print(t("Жадібний втратив {d}: дешевий «вигідний за грам» {first} заблокував пару {pair}.").format(
        d=optimum - greedy_value, first=names[steps[0]["index"]],
        pair="{" + ", ".join(names[i] for i in chosen) + "}"))

    plans = [
        {"label": t("Жадібний"), "items": greedy_items, "weights": weights,
         "values": values, "names": names, "total": greedy_value},
        {"label": t("Оптимум"), "items": chosen, "weights": weights,
         "values": values, "names": names, "total": optimum, "best": True},
    ]
    save_figure(draw_fill_plans(
        plans, capacity,
        title=t("Жадібний ({g}) недозаповнює рюкзак; оптимум ({o}) — рівно {W}").format(
            g=greedy_value, o=optimum, W=capacity)),
        "greedy_fill_classic.png")

    print_saved_location()


if __name__ == "__main__":
    main()
