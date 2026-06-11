"""Спільні утиліти для прикладів (``examples/``).

Кожен приклад потребує того самого boilerplate: перемикання matplotlib на
``Agg``, додавання кореня репозиторію в ``sys.path``, обчислення шляху до
``docs/images`` та однаковісінькі функції збереження фігур і друку шляхів.
Тут це зведено в одне місце.

Імпортуйте цей модуль ПЕРШИМ у прикладі — він налаштовує ``Agg`` до того, як
буде імпортовано ``matplotlib.pyplot``.
"""

from __future__ import annotations

import os
import sys
from dataclasses import dataclass
from typing import List, Sequence

import matplotlib

matplotlib.use("Agg")  # зберігаємо у файли без графічного дисплея

import matplotlib.pyplot as plt  # noqa: E402  (після use("Agg") — навмисно)

# корінь репозиторію в sys.path — дозволяє запуск без `pip install -e .`
_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from knapsack.animation import save_animation as _save_animation  # noqa: E402
from knapsack.i18n import set_lang, t  # noqa: E402
from knapsack.style import FIGURE_DPI  # noqa: E402
from knapsack.visualization import item_names  # noqa: E402

# --- вибір мови підписів із аргументів CLI ---------------------------------
# Передайте "en" аргументом (``python examples/01_brute_force.py en``), щоб
# малювати англійською. Імпортуйте _common ПЕРШИМ: тут одразу перемикається мова
# t() і маршрут теки виводу, тож усі подальші виклики малювання знають мову.
LANG: str = "en" if "en" in sys.argv[1:] else "uk"
set_lang(LANG)

#: Тека, куди приклади зберігають усі рисунки (англійською → у підтеку ``en/``).
IMG_DIR = (
    os.path.join(_ROOT, "docs", "images", "en") if LANG == "en"
    else os.path.join(_ROOT, "docs", "images")
)
os.makedirs(IMG_DIR, exist_ok=True)


@dataclass(frozen=True)
class KnapsackExample:
    """Дані одного навчального інстансу задачі про рюкзак.

    :param slug: коротка латинська назва — йде в імена файлів рисунків.
    :param label: людська назва інстансу (укр.; перекладається через ``t``).
    :param weights: ваги предметів.
    :param values: вартості предметів.
    :param capacity: місткість рюкзака ``W``.
    """

    slug: str
    label: str
    weights: List[int]
    values: List[int]
    capacity: int

    @property
    def n(self) -> int:
        """Кількість предметів."""
        return len(self.weights)

    @property
    def names(self) -> List[str]:
        """Підписи предметів поточною мовою (``П1…`` / ``I1…``)."""
        return item_names(self.n)


def save_figure(fig, name: str) -> None:
    """Зберігає фігуру у :data:`IMG_DIR` під іменем ``name`` і **закриває** її.

    Закриття тут — щоб приклади не накопичували відкриті Agg-полотна (по кілька
    мегабайтів кожне): жоден скрипт після збереження фігуру не використовує.
    """
    fig.savefig(os.path.join(IMG_DIR, name), bbox_inches="tight", dpi=FIGURE_DPI)
    plt.close(fig)


def save_anim(figures, basename: str, durations, **kwargs):
    """Зберігає анімацію у :data:`IMG_DIR`: GIF завжди + MP4 за наявності ffmpeg.

    :param figures: список фігур-кадрів (будуть закриті під час рендера).
    :param basename: ім'я файлу БЕЗ розширення — ``.gif`` і ``.mp4`` додаються самі.
    :param durations: тривалість кадру(ів) у мс (число або послідовність).
    :param kwargs: додаткові параметри :func:`knapsack.animation.save_animation`;
        зокрема ``mp4_path=None`` вимикає MP4 (типово він кладеться поруч із GIF).
    :returns: шлях до MP4, якщо його записано, інакше ``None`` (GIF є завжди).
    """
    gif = os.path.join(IMG_DIR, basename + ".gif")
    kwargs.setdefault("mp4_path", os.path.join(IMG_DIR, basename + ".mp4"))
    return _save_animation(figures, gif, durations, **kwargs)


def describe_instance(example: KnapsackExample) -> None:
    """Друкує умову інстансу: місткість і список предметів."""
    print(t("Інстанс «{label}»: місткість W = {W}, предметів n = {n}").format(
        label=t(example.label), W=example.capacity, n=example.n))
    names = example.names
    for i in range(example.n):
        print(t("  {name}: вага {w}, цінність {v}").format(
            name=names[i], w=example.weights[i], v=example.values[i]))


def report_chosen(chosen: Sequence[int], example: KnapsackExample) -> None:
    """Друкує відновлений набір предметів у форматі конспекту.

    :param chosen: 0-базові індекси обраних предметів (від ``reconstruct_items``).
    """
    names = example.names
    chosen_names = [names[i] for i in chosen]
    print(t("Обрані предмети: {items}").format(items=chosen_names))
    print(t("Сумарна вага:    {w}").format(
        w=sum(example.weights[i] for i in chosen)))
    print(t("Сумарна вартість: {v}").format(
        v=sum(example.values[i] for i in chosen)))


def print_saved_location() -> None:
    """Друкує підсумкове повідомлення про теку зі збереженими рисунками."""
    print(t("\nРисунки збережено у: {path}").format(path=IMG_DIR))
