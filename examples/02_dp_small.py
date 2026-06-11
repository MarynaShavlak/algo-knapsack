"""Приклад 2 — динамічне програмування на малому інстансі (таблиця 4×5).

Головний покроковий розбір README: порожня таблиця → заповнення рядок за рядком
(з повним консольним журналом, як у конспекті) → детальні кадри найцікавіших
клітинок (формула переходу «взяти проти не брати» прямо в кадрі) → фінальна
таблиця з відповіддю → відновлення набору зворотним проходом.

Запуск:  ``python examples/02_dp_small.py``        (українською → docs/images/)
         ``python examples/02_dp_small.py en``     (англійською → docs/images/en/)
"""

# _common ПЕРШИМ: налаштовує Agg, sys.path і мову до імпорту matplotlib.pyplot
from _common import describe_instance, print_saved_location, report_chosen, save_figure
from _items import SMALL

from knapsack.core import knapsack_dp_steps, reconstruct_steps  # noqa: E402
from knapsack.i18n import t  # noqa: E402
from knapsack.visualization import (  # noqa: E402
    configure_style,
    draw_backtrack,
    draw_dp_cell_frame,
    draw_dp_table_standalone,
    print_dp_log,
    print_dp_table,
)

#: Найпоказовіші клітинки для статичних кадрів «формула в кадрі»:
#: перше «взяти» (i=1, w=1), «взяти» з ненульовим залишком (i=2, w=3),
#: «влазить, але НЕ беремо» (i=3, w=3) та клітинка-відповідь (i=3, w=4).
SHOWCASE_CELLS = [(1, 1), (2, 3), (3, 3), (3, 4)]


def main() -> None:
    configure_style()
    ex = SMALL
    weights, values, capacity, n = ex.weights, ex.values, ex.capacity, ex.n
    names = ex.names

    describe_instance(ex)

    # 1) інструментоване ДП: таблиця + журнал по клітинках
    best, K, steps = knapsack_dp_steps(capacity, weights, values, n)
    print()
    print(t("Створили таблицю: {rows} рядків × {cols} стовпців, рядок i=0 — нулі.").format(
        rows=n + 1, cols=capacity + 1))

    # 2) порожня таблиця (лише базовий рядок) і стан після кожного рядка
    save_figure(draw_dp_table_standalone(
        K, weights, values, names, upto=(0, capacity),
        title=t("Старт: рядок i=0 — без предметів цінність 0"),
        note=t("стовпець w=0 теж завжди 0: без місця нічого не покладеш")),
        "dp_initial_small.png")
    for i in range(1, n + 1):
        save_figure(draw_dp_table_standalone(
            K, weights, values, names, upto=(i, capacity),
            title=t("Після рядка i={i}: дозволені предмети {first}…{name}").format(
                i=i, first=names[0], name=names[i - 1])),
            f"dp_row_small_{i}.png")

    # 3) повний журнал заповнення (формат — як у конспекті)
    print_dp_log(steps, weights, values, names)

    # 4) детальні кадри найпоказовіших клітинок (формула переходу в кадрі)
    for (i, w) in SHOWCASE_CELLS:
        save_figure(draw_dp_cell_frame(K, weights, values, names, i, w),
                    f"dp_cell_small_i{i}_w{w}.png")

    # 5) фінальна таблиця + текстова версія
    print()
    print_dp_table(K, names)
    print()
    print(t("ВІДПОВІДЬ = K[{n}][{W}] = {v}").format(n=n, W=capacity, v=best))
    save_figure(draw_dp_table_standalone(
        K, weights, values, names, answer=(n, capacity),
        title=t("Таблиця заповнена: відповідь у правому нижньому куті"),
        note=t("червона рамка — клітинка з відповіддю K[n][W]")),
        "dp_table_small.png")

    # 6) відновлення набору зворотним проходом
    chosen, recon = reconstruct_steps(K, weights, capacity)
    print()
    for s in recon:
        if s["taken"]:
            print(t("i={i}, w={w}: K[{i}][{w}]={v} ≠ K[{i1}][{w}]={a} → {name} УЗЯТО, w ← {wa}").format(
                i=s["i"], w=s["w"], v=s["value"], i1=s["i"] - 1, a=s["above"],
                name=names[s["i"] - 1], wa=s["w_after"]))
        else:
            print(t("i={i}, w={w}: K[{i}][{w}]={v} = K[{i1}][{w}]={a} → {name} не брали").format(
                i=s["i"], w=s["w"], v=s["value"], i1=s["i"] - 1, a=s["above"],
                name=names[s["i"] - 1]))
    print()
    report_chosen(chosen, ex)
    save_figure(draw_backtrack(
        K, weights, values, names, recon,
        title=t("Зворотний хід: жовтий шлях збирає відповідь {v}").format(v=best),
        note=t("зелена стрілка = предмет узято (стрибок ліворуч на його вагу), сіра = ні (рух прямо вгору)")),
        "backtrack_small.png")

    print_saved_location()


if __name__ == "__main__":
    main()
