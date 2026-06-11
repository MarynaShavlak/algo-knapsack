"""Приклад 0 — умова задачі: предмети та місткість рюкзака.

Малює «вітрину» обох навчальних інстансів із конспекту: предмети (ширина картки
пропорційна вазі) та смугу місткості рюкзака. Одразу видно головний конфлікт
задачі: разом усі предмети НЕ влазять, тож доведеться обирати.

Запуск:  ``python examples/00_intro_items.py``        (українською → docs/images/)
         ``python examples/00_intro_items.py en``     (англійською → docs/images/en/)
"""

# _common ПЕРШИМ: налаштовує Agg, sys.path і мову до імпорту matplotlib.pyplot
from _common import describe_instance, print_saved_location, save_figure
from _items import CLASSIC, SMALL

from knapsack.i18n import t  # noqa: E402
from knapsack.visualization import configure_style, draw_items  # noqa: E402


def main() -> None:
    configure_style()

    # 1) класичний інстанс із конспекту (на ньому працюють перебір і жадібний)
    describe_instance(CLASSIC)
    print(t("Мета: обрати предмети так, щоб сумарна вага ≤ {W}, а цінність — максимальна.").format(
        W=CLASSIC.capacity))
    fig = draw_items(CLASSIC.weights, CLASSIC.values, CLASSIC.names, CLASSIC.capacity,
                     title=t("Класичний інстанс: що покласти в рюкзак на {W}?").format(
                         W=CLASSIC.capacity))
    save_figure(fig, "items_classic.png")

    # 2) малий інстанс (на ньому розбиратимемо таблицю ДП по клітинках)
    print()
    describe_instance(SMALL)
    fig = draw_items(SMALL.weights, SMALL.values, SMALL.names, SMALL.capacity,
                     title=t("Малий інстанс: рюкзак на {W} — таблиця ДП поміститься на екран").format(
                         W=SMALL.capacity))
    save_figure(fig, "items_small.png")

    print_saved_location()


if __name__ == "__main__":
    main()
