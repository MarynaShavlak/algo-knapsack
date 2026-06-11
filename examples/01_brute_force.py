"""Приклад 1 — повний перебір: усі 2^n підмножин і чому це «вибухає».

Відтворює розділ README про брутфорс: рекурсивна версія з конспекту, явний
перелік підмножин (таблиця всіх 8 комбінацій), дерево рекурсії «взяти / не
брати» та ціна питання — графік зростання 2^n проти n·W. Наприкінці — більший
інстанс на 20 предметів: мільйон підмножин проти ~тисячі клітинок ДП (із
вимірюванням часу на цій машині).

Запуск:  ``python examples/01_brute_force.py``        (українською → docs/images/)
         ``python examples/01_brute_force.py en``     (англійською → docs/images/en/)
"""

import time

# _common ПЕРШИМ: налаштовує Agg, sys.path і мову до імпорту matplotlib.pyplot
from _common import describe_instance, print_saved_location, save_figure
from _items import BIG, CLASSIC

from knapsack.core import (  # noqa: E402
    brute_force_steps,
    knapsack_brute_force,
    knapsack_dp,
    knapsack_recursive,
)
from knapsack.i18n import t  # noqa: E402
from knapsack.visualization import (  # noqa: E402
    configure_style,
    draw_growth,
    draw_recursion_tree,
    draw_subsets,
    format_combo,
    print_subsets,
)

BAR = "=" * 60


def main() -> None:
    configure_style()
    weights, values, capacity = CLASSIC.weights, CLASSIC.values, CLASSIC.capacity
    names = CLASSIC.names

    # 1) обидві реалізації з конспекту дають ту саму відповідь
    print(BAR)
    print(t("Повний перебір — інстанс «{label}»").format(label=t(CLASSIC.label)))
    print(BAR)
    describe_instance(CLASSIC)
    print()
    print(t("Рекурсивна версія (з конспекту):"), knapsack_recursive(capacity, weights, values, CLASSIC.n))
    best_value, best_combo = knapsack_brute_force(capacity, weights, values)
    print(t("Максимальна вартість:"), best_value)
    print(t("Обрані предмети (індекси):"), best_combo)
    print(t("Тобто набір {combo}: вага {w}, цінність {v}.").format(
        combo=format_combo(best_combo, names),
        w=sum(weights[i] for i in best_combo),
        v=sum(values[i] for i in best_combo)))

    # 2) усі 2^3 = 8 підмножин — таблицею в консоль і рисунком
    print()
    _, _, steps = brute_force_steps(capacity, weights, values)
    print_subsets(steps, names, capacity)
    save_figure(draw_subsets(steps, weights, values, names, capacity),
                "subsets_classic.png")

    # 3) дерево рекурсії: кожен рівень вирішує долю одного предмета
    save_figure(draw_recursion_tree(capacity, weights, values, names),
                "tree_classic.png")

    # 4) чому це вибухає: 2^n подвоюється з кожним предметом
    print()
    print(t("Зростання кількості підмножин 2^n:"))
    for n in (3, 10, 20, 30, 40, 50):
        print(t("  n = {n:>2}  →  2^{n} = {count} підмножин").format(
            n=n, count=f"{2 ** n:,}".replace(",", " ")))
    save_figure(draw_growth(n_max=30, dp_w=CLASSIC.capacity,
                            big=(BIG.n, BIG.capacity)),
                "growth_2n.png")

    # 5) більший інстанс: та сама відповідь, незрівнянна ціна
    print()
    print(BAR)
    print(t("Більший інстанс — «{label}» (n = {n}, W = {W})").format(
        label=t(BIG.label), n=BIG.n, W=BIG.capacity))
    print(BAR)
    subsets = 2 ** BIG.n
    cells = (BIG.n + 1) * (BIG.capacity + 1)
    print(t("Повний перебір мусить оглянути 2^{n} = {subsets} підмножин;").format(
        n=BIG.n, subsets=f"{subsets:,}".replace(",", " ")))
    print(t("ДП заповнює таблицю (n+1)×(W+1) = {rows}×{cols} = {cells} клітинок.").format(
        rows=BIG.n + 1, cols=BIG.capacity + 1,
        cells=f"{cells:,}".replace(",", " ")))

    t0 = time.perf_counter()
    bf_value, bf_combo = knapsack_brute_force(BIG.capacity, BIG.weights, BIG.values)
    t_bf = time.perf_counter() - t0
    t0 = time.perf_counter()
    dp_value = knapsack_dp(BIG.capacity, BIG.weights, BIG.values, BIG.n)
    t_dp = time.perf_counter() - t0

    print(t("Однакова відповідь: перебір = {bf}, ДП = {dp}  →  збіг: {ok}").format(
        bf=bf_value, dp=dp_value, ok=bf_value == dp_value))
    # час залежить від машини, тому цей рядок у README цитуємо лише приблизно
    print(t("Час на цій машині: перебір {bf:.2f} с проти ДП {dp:.4f} с (×{ratio:.0f})").format(
        bf=t_bf, dp=t_dp, ratio=t_bf / t_dp if t_dp else float("inf")))

    print_saved_location()


if __name__ == "__main__":
    main()
