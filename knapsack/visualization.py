"""Візуалізації для навчального розбору задачі про рюкзак 0/1.

Центральний об'єкт — **таблиця ДП** ``K[i][w]``: рядок = «скільки предметів
дозволено», стовпець = місткість. Усі функції малювання параметризовані вагами,
вартостями та підписами предметів, тож однаково працюють для будь-якого інстансу:

* :func:`draw_items` — «вітрина» задачі: предмети та місткість рюкзака;
* :func:`draw_subsets` — повний перебір: усі :math:`2^n` підмножин таблицею
  (вона ж — кадри анімації через ``upto``/``current``);
* :func:`draw_recursion_tree` — дерево рекурсії «взяти / не брати»;
* :func:`draw_growth` — чому перебір «вибухає»: :math:`2^n` проти :math:`n
  \\cdot W` на лог-шкалі;
* :func:`draw_dp_table` — таблиця ДП на заданій осі (підсвічування: поточна
  клітинка, джерела «взяти»/«не брати», шлях відновлення, відповідь);
* :func:`draw_dp_table_standalone` — те саме, але створює власну фігуру;
* :func:`draw_dp_cell_frame` — «детальний кадр»: таблиця + повна формула
  переходу для однієї клітинки (гілка «взяти» проти «не брати»);
* :func:`draw_dp_evolution` — зведена сітка: таблиця після кожного рядка ``i``;
* :func:`draw_backtrack` / :func:`draw_backtrack_frame` — відновлення набору
  зворотним проходом (статична картина та кадри для анімації);
* :func:`draw_fill_plans` — смуги заповнення рюкзака (жадібний проти оптимуму).

Кольорова схема (єдина для всіх візуалізацій, див. :mod:`knapsack.style`):

* 🟧 помаранчевий — поточна клітинка ``(i, w)``;
* 🟩 зелений — гілка/джерело «взяти» (вартість предмета увійшла в клітинку);
* 🟦 синій — гілка/джерело «не брати» (значення перенесено зверху);
* 🟨 жовтий — клітинки шляху відновлення;
* 🔴 червоний — відповідь (клітинка ``K[n][W]``, найкраща підмножина).
"""

from __future__ import annotations

from typing import Dict, List, Optional, Sequence, Set, Tuple

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Patch

from .core import Step, Table, knapsack_recursive
from .i18n import t
from .style import (
    FIGURE_DPI,
    configure_style,
    GREEN_FILL,
    GREEN_EDGE,
    GREEN_TXT,
    BLUE_FILL,
    BLUE_EDGE,
    CURRENT_FILL,
    CURRENT_EDGE,
    PATH_FILL,
    PATH_EDGE,
    ANSWER_EDGE,
    GRID_EDGE,
    EMPTY_FILL,
    BASE_FILL,
    ITEM_COLOR,
    SLACK_FILL,
    NEUTRAL_GRAY,
    HEADER_TXT,
    SUBLABEL_TXT,
    MUTED_TXT,
    TEXT_DARK,
    TEXT_FORMULA,
    TEXT_RESULT,
)

# :func:`configure_style` лишається доступною з цього модуля задля зручності
# (приклади імпортують її саме звідси), але визначена в :mod:`knapsack.style`.

__all__ = [
    "configure_style",
    "format_combo",
    "item_names",
    "draw_items",
    "draw_subsets",
    "draw_recursion_tree",
    "draw_growth",
    "draw_dp_table",
    "draw_dp_table_standalone",
    "draw_dp_cell_frame",
    "draw_dp_evolution",
    "draw_backtrack",
    "draw_backtrack_frame",
    "draw_fill_plans",
    "dp_cell_log_line",
    "print_dp_log",
    "print_dp_table",
    "print_subsets",
]

#: Кольори предметів на «вітрині» та смугах підмножин (за індексом предмета).
ITEM_PALETTE = ["#1f77b4", "#7F77DD", "#1D9E75", "#C77B3F", "#B5588C", "#5B8FA8"]


# ---------------------------------------------------------------------------
# Допоміжні форматувальники
# ---------------------------------------------------------------------------
def item_names(n: int) -> List[str]:
    """Підписи предметів ``П1 … Пn`` поточною мовою (en: ``I1 … In``)."""
    return [t("П{i}").format(i=i + 1) for i in range(n)]


def format_combo(combo: Sequence[int], names: Sequence[str]) -> str:
    """Підмножина як текст: ``(1, 2)`` → ``{П2, П3}``; порожня → ``{ }``."""
    if not combo:
        return "{ }"
    return "{" + ", ".join(names[i] for i in combo) + "}"


def _item_color(i: int) -> str:
    return ITEM_PALETTE[i % len(ITEM_PALETTE)]


# ---------------------------------------------------------------------------
# «Вітрина» задачі: предмети + місткість рюкзака
# ---------------------------------------------------------------------------
def draw_items(
    weights: Sequence[int],
    values: Sequence[int],
    names: Sequence[str],
    capacity: int,
    title: Optional[str] = None,
):
    """Малює умову задачі: предмети (ширина = вага) та смугу місткості рюкзака.

    Ширина кожної картки пропорційна вазі предмета, тож одразу видно, що всі
    разом вони можуть і не влазити (сумарна вага проти місткості).

    :returns: об'єкт ``Figure``.
    """
    n = len(weights)
    gap = capacity * 0.04
    total_w = sum(weights) + gap * (n - 1)
    xmax = max(total_w, capacity) * 1.02

    fig, ax = plt.subplots(figsize=(10, 3.6))
    ax.set_xlim(-xmax * 0.01, xmax)
    ax.set_ylim(-0.9, 2.4)
    ax.axis("off")

    # предмети: картки в ряд, ширина = вага
    x = 0.0
    for i in range(n):
        w, v = weights[i], values[i]
        ax.add_patch(plt.Rectangle((x, 1.0), w, 0.9, facecolor=_item_color(i),
                                   edgecolor="white", linewidth=1.5))
        ax.text(x + w / 2, 1.62, names[i], ha="center", va="center",
                color="white", fontweight="bold", fontsize=12)
        ax.text(x + w / 2, 1.28, t("вага {w}").format(w=w), ha="center", va="center",
                color="white", fontsize=9.5)
        ax.text(x + w / 2, 0.78, t("цінність {v}").format(v=v), ha="center", va="center",
                color=_item_color(i), fontsize=10, fontweight="bold")
        x += w + gap

    # рюкзак: смуга місткості
    ax.add_patch(plt.Rectangle((0, -0.55), capacity, 0.62, facecolor="white",
                               edgecolor=TEXT_DARK, linewidth=1.8, linestyle="--"))
    ax.text(capacity / 2, -0.24, t("рюкзак: місткість {W}").format(W=capacity),
            ha="center", va="center", fontsize=11, color=TEXT_DARK)
    ax.annotate("", xy=(capacity, 0.18), xytext=(0, 0.18),
                arrowprops=dict(arrowstyle="<|-|>", color=NEUTRAL_GRAY, lw=1.4))
    total = sum(weights)
    ax.text(xmax * 0.99, -0.24,
            t("разом: вага {tw}, цінність {tv}").format(tw=total, tv=sum(values)),
            ha="right", va="center", fontsize=10, color=SUBLABEL_TXT, style="italic")

    ax.set_title(title if title is not None
                 else t("Задача про рюкзак: предмети та місткість"), fontsize=13, pad=10)
    fig.tight_layout()
    return fig


# ---------------------------------------------------------------------------
# Повний перебір: таблиця всіх підмножин (статична + кадри анімації)
# ---------------------------------------------------------------------------
def draw_subsets(
    steps: List[Step],
    weights: Sequence[int],
    values: Sequence[int],
    names: Sequence[str],
    capacity: int,
    title: Optional[str] = None,
    upto: Optional[int] = None,
    figsize: Optional[Tuple[float, float]] = None,
):
    """Усі підмножини перебору одним списком: смуга ваги + вартість + вердикт.

    :param steps: журнал :func:`knapsack.core.brute_force_steps`.
    :param upto: якщо задано — показуються лише підмножини ``0..upto`` (кадр для
        анімації); поточна (``upto``) підсвічується, найкраща «поки що» — рамкою.
        ``None`` — статична картина: показано все, рамка на фінальній відповіді.
    :returns: об'єкт ``Figure``.
    """
    rows = len(steps)
    last = rows - 1 if upto is None else upto
    best_combo = steps[last]["best_combo"]
    # індекс рядка-лідера станом на кадр `last` (останній improved серед 0..last)
    best_idx = max((k for k in range(last + 1) if steps[k]["improved"]), default=None)

    max_w = max(max(s["weight"] for s in steps), capacity)
    label_w = capacity * 0.46
    info_w = capacity * 1.12          # дві колонки: числа + вердикт
    verdict_x = capacity * 0.52       # зсув колонки вердикту від краю смуг
    xmax = max_w * 1.03

    if figsize is None:
        figsize = (10.5, 0.56 * rows + 1.7)
    fig, ax = plt.subplots(figsize=figsize)
    ax.set_xlim(-label_w, xmax + info_w)
    ax.set_ylim(-0.7, rows + 0.8)
    ax.axis("off")

    # вертикальна межа місткості
    ax.plot([capacity, capacity], [-0.35, rows], color=ANSWER_EDGE,
            linestyle="--", linewidth=1.6, zorder=1)
    ax.text(capacity, rows + 0.12, t("місткість {W}").format(W=capacity),
            ha="center", va="bottom", fontsize=10, color=ANSWER_EDGE)

    for k, s in enumerate(steps):
        y = rows - 1 - k   # перша підмножина — угорі
        combo = s["combo"]
        label = format_combo(combo, names)
        shown = k <= last

        if not shown:
            ax.text(-label_w * 0.04, y + 0.5, label, ha="right", va="center",
                    fontsize=10.5, color="#DDDDDD")
            continue

        if upto is not None and k == upto:
            ax.add_patch(plt.Rectangle((-label_w, y + 0.04), label_w + xmax + info_w, 0.92,
                                       facecolor=CURRENT_FILL, edgecolor="none", zorder=0))
        ax.text(-label_w * 0.04, y + 0.5, label, ha="right", va="center",
                fontsize=10.5, color=TEXT_DARK,
                fontweight="bold" if combo == best_combo and s["improved"] or k == best_idx else "normal")

        # смуга ваги: сегменти предметів
        x = 0.0
        for i in combo:
            wseg = weights[i]
            ax.add_patch(plt.Rectangle((x, y + 0.18), wseg, 0.64,
                                       facecolor=_item_color(i), edgecolor="white",
                                       linewidth=1.0, zorder=2))
            if wseg >= max_w * 0.045:
                ax.text(x + wseg / 2, y + 0.5, names[i], ha="center", va="center",
                        fontsize=8.5, color="white", fontweight="bold", zorder=3)
            x += wseg

        # числа та вердикт — двома окремими колонками праворуч
        fits = s["fits"]
        ax.text(xmax + capacity * 0.03, y + 0.5,
                t("вага {w} · цінність {v}").format(w=s["weight"], v=s["value"]),
                ha="left", va="center", fontsize=9.5, color=TEXT_FORMULA)
        vx = xmax + verdict_x
        if not fits:
            ax.text(vx, y + 0.5, t("✗ не влазить ({w} > {W})").format(
                w=s["weight"], W=capacity),
                ha="left", va="center", fontsize=9.5, color=ANSWER_EDGE)
        elif k == best_idx:
            ax.text(vx, y + 0.5, t("★ найкраща: {v}").format(v=s["best_value"]),
                    ha="left", va="center", fontsize=10, color=ANSWER_EDGE,
                    fontweight="bold")
        else:
            ax.text(vx, y + 0.5, "✓", ha="left", va="center",
                    fontsize=11, color=GREEN_TXT)

        if k == best_idx:
            ax.add_patch(plt.Rectangle((-label_w, y + 0.02), label_w + xmax + info_w, 0.96,
                                       fill=False, edgecolor=ANSWER_EDGE, linewidth=2.2,
                                       zorder=4))

    if title is None:
        title = t("Повний перебір: усі {m} підмножин ({n} предметів → 2^{n})").format(
            m=rows, n=len(weights))
    ax.set_title(title, fontsize=13, pad=14)
    fig.tight_layout()
    return fig


# ---------------------------------------------------------------------------
# Дерево рекурсії «взяти / не брати»
# ---------------------------------------------------------------------------
def draw_recursion_tree(
    W: int,
    weights: Sequence[int],
    values: Sequence[int],
    names: Sequence[str],
    title: Optional[str] = None,
):
    """Дерево рекурсивного перебору: кожен рівень вирішує долю одного предмета.

    Вузол — підзадача ``knapSack(W, n)`` зі своєю відповіддю; гілки — «взяти»
    (суцільна, з ``+вартість``) та «не брати» (пунктирна). Листки — підзадачі з
    одним предметом. Зелений шлях — рішення, з яких реально зібрано оптимум.

    Розраховане на малі ``n`` (3–4 предмети) — далі дерево не вміщається, і саме
    в цьому суть експоненційного вибуху.

    :returns: об'єкт ``Figure``.
    """
    n = len(weights)

    def build(w_free: int, m: int) -> Dict:
        node: Dict = {"W": w_free, "n": m,
                      "value": knapsack_recursive(w_free, weights, values, m)}
        if m > 1:
            if weights[m - 1] <= w_free:
                node["take"] = build(w_free - weights[m - 1], m - 1)
            node["skip"] = build(w_free, m - 1)
        return node

    root = build(W, n)

    # координати: листки рівномірно, внутрішні вузли по центру нащадків
    leaf_step = 3.0
    counter = [0.0]

    def place(node: Dict, level: int) -> None:
        node["y"] = level * 2.6
        kids = [node[k] for k in ("take", "skip") if k in node]
        if not kids:
            node["x"] = counter[0]
            counter[0] += leaf_step
            return
        for kid in kids:
            place(kid, level - 1)
        node["x"] = sum(k["x"] for k in kids) / len(kids)

    place(root, n - 1)

    # оптимальний шлях: повторюємо вибір max(взяти, не брати) самого коду
    on_path = {id(root)}
    node = root
    while node["n"] > 1:
        take = node.get("take")
        if take is not None and values[node["n"] - 1] + take["value"] >= node["skip"]["value"]:
            node = take
        else:
            node = node["skip"]
        on_path.add(id(node))

    green, purple, gray = "#1D9E75", "#7F77DD", "#9a9a9a"
    xs: List[float] = []

    def draw_node(node: Dict) -> None:
        x, y = node["x"], node["y"]
        xs.append(x)
        col = green if id(node) in on_path else purple
        for key, dashed in (("take", False), ("skip", True)):
            kid = node.get(key)
            if kid is None:
                continue
            child_on_path = id(node) in on_path and id(kid) in on_path and (
                (key == "take") == _took_branch(node))
            ecol = green if child_on_path else gray
            lw = 2.4 if child_on_path else 1.3
            x2, y2 = kid["x"], kid["y"]
            ax.annotate("", xy=(x2, y2 + 0.5), xytext=(x, y - 0.5),
                        arrowprops=dict(arrowstyle="-|>", color=ecol, lw=lw,
                                        linestyle="--" if dashed else "-"))
            label = (t("взяти {name} +{v}").format(name=names[node["n"] - 1],
                                                   v=values[node["n"] - 1])
                     if key == "take" else
                     t("не брати {name}").format(name=names[node["n"] - 1]))
            ax.text((x + x2) / 2, (y - 0.5 + y2 + 0.5) / 2, label, fontsize=8.5,
                    color=ecol, ha="center", va="center",
                    bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none"))
            draw_node(kid)

        from matplotlib.colors import to_rgba
        ax.add_patch(FancyBboxPatch((x - 1.05, y - 0.45), 2.1, 0.9,
                                    boxstyle="round,pad=0.02,rounding_size=0.12",
                                    linewidth=1.3, edgecolor=col,
                                    facecolor=to_rgba(col, 0.16)))
        ax.text(x, y + 0.13, f"W={node['W']}, n={node['n']}", ha="center",
                va="center", fontsize=10.5, fontweight="bold")
        ax.text(x, y - 0.2, f"= {node['value']}", ha="center", va="center",
                fontsize=9.5, color="#333333")

    def _took_branch(node: Dict) -> bool:
        take = node.get("take")
        return take is not None and (
            values[node["n"] - 1] + take["value"] >= node["skip"]["value"])

    width = max(8.0, counter[0] + leaf_step)
    fig, ax = plt.subplots(figsize=(width * 0.92, 1.9 * n + 0.8))
    ax.set_xlim(-leaf_step * 0.55, counter[0] + leaf_step * 0.1)
    ax.set_ylim(-1.2, (n - 1) * 2.6 + 1.3)
    ax.axis("off")
    draw_node(root)

    ax.set_title(title if title is not None
                 else t("Дерево рекурсії — повний перебір (зелене = оптимальний шлях)"),
                 fontsize=12.5, pad=8)
    fig.tight_layout()
    return fig


# ---------------------------------------------------------------------------
# Чому перебір «вибухає»: 2^n проти n·W
# ---------------------------------------------------------------------------
def draw_growth(
    n_max: int = 30,
    dp_w: int = 50,
    big: Optional[Tuple[int, int]] = None,
):
    """Лог-графік зростання: :math:`2^n` (перебір) проти :math:`n \\cdot W` (ДП).

    :param dp_w: місткість ``W`` для прямої ДП (підпис у легенді).
    :param big: пара ``(n, W)`` конкретного інстансу — додає праву панель із
        двома стовпчиками: скільки підмножин перебирає брутфорс і скільки
        клітинок заповнює ДП для цього інстансу.
    :returns: об'єкт ``Figure``.
    """
    ns = list(range(1, n_max + 1))
    if big is None:
        fig, ax = plt.subplots(figsize=(7.6, 4.6))
        axes = [ax]
    else:
        fig, axes = plt.subplots(1, 2, figsize=(11.5, 4.6),
                                 gridspec_kw={"width_ratios": [1.7, 1]})

    ax = axes[0]
    ax.semilogy(ns, [2 ** v for v in ns], color=ANSWER_EDGE, lw=2.4,
                label=t("повний перебір: 2ⁿ підмножин"))
    ax.semilogy(ns, [v * dp_w for v in ns], color=GREEN_EDGE, lw=2.4,
                label=t("ДП: n·W клітинок (W = {W})").format(W=dp_w))
    for mark, txt in ((10, t("2¹⁰ ≈ тисяча")), (20, t("2²⁰ ≈ мільйон")),
                      (30, t("2³⁰ ≈ мільярд"))):
        if mark <= n_max:
            # останню позначку опускаємо ПІД криву, щоб текст не різало краєм осей
            dy = 2.4 if mark < n_max else 0.012
            ax.annotate(txt, xy=(mark, 2 ** mark), xytext=(mark - 8.6, 2 ** mark * dy),
                        fontsize=9.5, color=ANSWER_EDGE,
                        arrowprops=dict(arrowstyle="-|>", color=ANSWER_EDGE, lw=1.1))
    ax.set_xlabel(t("кількість предметів n"))
    ax.set_ylabel(t("обсяг роботи (лог-шкала)"))
    ax.set_axisbelow(True)
    ax.grid(True, which="both", alpha=0.25)
    ax.legend(loc="lower right", fontsize=9.5)
    ax.set_title(t("Кожен новий предмет подвоює перебір"), fontsize=12)

    if big is not None:
        bn, bw = big
        subsets = 2 ** bn
        cells = (bn + 1) * (bw + 1)
        ax2 = axes[1]
        bars = ax2.bar([0, 1], [subsets, cells],
                       color=[ANSWER_EDGE, GREEN_EDGE], width=0.55)
        ax2.set_yscale("log")
        ax2.set_xticks([0, 1])
        ax2.set_xticklabels([t("перебір"), t("ДП")])
        for bar, count in zip(bars, (subsets, cells)):
            ax2.text(bar.get_x() + bar.get_width() / 2, count * 1.25,
                     f"{count:,}".replace(",", " "), ha="center", va="bottom",
                     fontsize=10.5, fontweight="bold")
        ax2.set_ylim(1, subsets * 30)
        ax2.set_axisbelow(True)
        ax2.grid(True, axis="y", which="major", alpha=0.25)
        ax2.set_title(t("Інстанс: n = {n}, W = {W}").format(n=bn, W=bw), fontsize=12)
        ax2.set_ylabel(t("підмножин / клітинок (лог-шкала)"))

    fig.tight_layout()
    return fig


# ---------------------------------------------------------------------------
# Таблиця ДП (центральна візуалізація)
# ---------------------------------------------------------------------------
def _row_label(i: int, weights: Sequence[int], values: Sequence[int],
               names: Sequence[str]) -> str:
    """Підпис рядка таблиці: ``0: —`` або ``2: П2 (в=2, ц=10)``."""
    if i == 0:
        return "0: —"
    return t("{i}: {name} (в={w}, ц={v})").format(
        i=i, name=names[i - 1], w=weights[i - 1], v=values[i - 1])


def draw_dp_table(
    ax,
    K: Table,
    weights: Sequence[int],
    values: Sequence[int],
    names: Sequence[str],
    title: Optional[str] = None,
    cols: Optional[Sequence[int]] = None,
    upto: Optional[Tuple[int, int]] = None,
    current: Optional[Tuple[int, int]] = None,
    show_sources: bool = False,
    path: Optional[Set[Tuple[int, int]]] = None,
    take_cells: Optional[Set[Tuple[int, int]]] = None,
    answer: Optional[Tuple[int, int]] = None,
    compare: Optional[Tuple[int, int]] = None,
    value_fontsize: float = 12,
) -> None:
    """Малює таблицю ДП ``K[i][w]`` на заданій осі ``ax``.

    :param cols: які стовпці (місткості ``w``) показувати; ``None`` — усі.
        Зручно для широких таблиць (``W = 50`` → показуємо кратні 10).
    :param upto: клітинка ``(i, w)``, до якої (включно, у порядку заповнення
        рядок-за-рядком) таблиця вже заповнена; решта — порожні. ``None`` — вся.
    :param current: поточна клітинка — помаранчева рамка.
    :param show_sources: підсвітити джерела поточної клітинки: 🟦 «не брати»
        (клітинка прямо над) та 🟩 «взяти» (рядок вище, лівіше на вагу предмета),
        зі стрілками до поточної.
    :param path: клітинки шляху відновлення — жовта заливка.
    :param take_cells: клітинки, де перемогла гілка «взяти» — легка зелена
        заливка (для «карти рішень» фінальної таблиці).
    :param answer: клітинка відповіді — червона рамка.
    :param compare: клітинка, з якою поточну порівнює зворотний прохід
        (``K[i-1][w]``) — синя рамка без заливки.
    """
    n = len(K) - 1
    all_cols = list(range(len(K[0])))
    cols = all_cols if cols is None else list(cols)
    ncols, nrows = len(cols), n + 1
    col_x = {w: j for j, w in enumerate(cols)}
    path = path or set()
    take_cells = take_cells or set()

    label_pad = 0.18
    ax.set_xlim(-4.0, ncols)
    ax.set_ylim(-0.25, nrows + 0.95)
    ax.set_aspect("equal")
    ax.axis("off")
    if title:
        ax.set_title(title, fontsize=12, pad=10)

    def y_top(i: int) -> float:
        return nrows - 1 - i  # рядок 0 — угорі

    def filled(i: int, w: int) -> bool:
        if upto is None:
            return True
        ui, uw = upto
        return i < ui or (i == ui and w <= uw)

    # підписи стовпців і рядків
    for w in cols:
        ax.text(col_x[w] + 0.5, nrows + 0.16, f"w={w}", ha="center", va="bottom",
                fontsize=9.5, color=HEADER_TXT)
    ax.text(-label_pad, nrows + 0.16, "i \\ w", ha="right", va="bottom",
            fontsize=9, color=MUTED_TXT)
    for i in range(nrows):
        ax.text(-label_pad, y_top(i) + 0.5, _row_label(i, weights, values, names),
                ha="right", va="center", fontsize=9.5, color=HEADER_TXT)

    # джерела поточної клітинки
    take_src = skip_src = None
    if show_sources and current is not None:
        ci, cw = current
        if ci >= 1:
            skip_src = (ci - 1, cw)
            if weights[ci - 1] <= cw:
                take_src = (ci - 1, cw - weights[ci - 1])

    # клітинки
    for i in range(nrows):
        for w in cols:
            x, y = col_x[w], y_top(i)
            is_filled = filled(i, w)
            face, edge, lw = "white", GRID_EDGE, 1.0
            if not is_filled:
                face = EMPTY_FILL
            elif (i, w) in path:
                face = PATH_FILL
            elif take_src == (i, w):
                face, edge, lw = GREEN_FILL, GREEN_EDGE, 2.2
            elif skip_src == (i, w):
                face, edge, lw = BLUE_FILL, BLUE_EDGE, 2.2
            elif current == (i, w):
                face, edge, lw = CURRENT_FILL, CURRENT_EDGE, 2.6
            elif (i, w) in take_cells:
                face = GREEN_FILL
            elif i == 0 or w == 0:
                face = BASE_FILL
            ax.add_patch(plt.Rectangle((x, y), 1, 1, facecolor=face,
                                       edgecolor=edge, linewidth=lw,
                                       zorder=3 if lw > 1 else 2))
            if is_filled:
                base_cell = (i == 0 or w == 0)
                color = MUTED_TXT if (base_cell and K[i][w] == 0) else TEXT_DARK
                if (i, w) in path:
                    color = "#7A5E00"
                ax.text(x + 0.5, y + 0.5, str(K[i][w]), ha="center", va="center",
                        fontsize=value_fontsize, color=color,
                        fontweight="bold" if (i, w) in path or current == (i, w)
                        else "normal", zorder=4)

    # рамки поверх заливок
    if current is not None and current[1] in col_x:
        ci, cw = current
        ax.add_patch(plt.Rectangle((col_x[cw], y_top(ci)), 1, 1, fill=False,
                                   edgecolor=CURRENT_EDGE, linewidth=2.6, zorder=5))
    if compare is not None and compare[1] in col_x:
        bi, bw = compare
        ax.add_patch(plt.Rectangle((col_x[bw], y_top(bi)), 1, 1, fill=False,
                                   edgecolor=BLUE_EDGE, linewidth=2.4, zorder=5))
    if answer is not None and answer[1] in col_x:
        ai, aw = answer
        ax.add_patch(plt.Rectangle((col_x[aw], y_top(ai)), 1, 1, fill=False,
                                   edgecolor=ANSWER_EDGE, linewidth=2.8, zorder=6))

    # стрілки від джерел до поточної клітинки
    if show_sources and current is not None:
        ci, cw = current
        cur_c = (col_x[cw] + 0.5, y_top(ci) + 0.5)
        if skip_src is not None and skip_src[1] in col_x:
            src_c = (col_x[skip_src[1]] + 0.5, y_top(skip_src[0]) + 0.5)
            ax.annotate("", xy=cur_c, xytext=src_c, zorder=7,
                        arrowprops=dict(arrowstyle="-|>", color=BLUE_EDGE, lw=2.2,
                                        shrinkA=14, shrinkB=14))
        if take_src is not None and take_src[1] in col_x and take_src != skip_src:
            src_c = (col_x[take_src[1]] + 0.5, y_top(take_src[0]) + 0.5)
            ax.annotate("", xy=cur_c, xytext=src_c, zorder=7,
                        arrowprops=dict(arrowstyle="-|>", color=GREEN_EDGE, lw=2.2,
                                        shrinkA=14, shrinkB=14,
                                        connectionstyle="arc3,rad=0.25"))


def _table_figsize(nrows: int, ncols: int, scale: float = 0.72) -> Tuple[float, float]:
    """Розмір фігури під таблицю з підписами рядків ліворуч і заголовком."""
    return ((ncols + 4.6) * scale, (nrows + 2.1) * scale)


def draw_dp_table_standalone(
    K: Table,
    weights: Sequence[int],
    values: Sequence[int],
    names: Sequence[str],
    title: Optional[str] = None,
    note: Optional[str] = None,
    **kwargs,
):
    """Таблиця ДП у власній фігурі (обгортка над :func:`draw_dp_table`).

    :param note: необов'язковий рядок-примітка під таблицею (сірим курсивом).
    :returns: об'єкт ``Figure``.
    """
    n = len(K) - 1
    cols = kwargs.get("cols")
    ncols = len(cols) if cols is not None else len(K[0])
    fig, ax = plt.subplots(figsize=_table_figsize(n + 1, ncols))
    draw_dp_table(ax, K, weights, values, names, title=title, **kwargs)
    if note:
        fig.text(0.5, 0.015, note, ha="center", va="bottom", fontsize=9,
                 color=MUTED_TXT, style="italic")
    fig.tight_layout(rect=(0, 0.04 if note else 0, 1, 1))
    return fig


# ---------------------------------------------------------------------------
# Детальний кадр однієї клітинки (формула переходу в кадрі)
# ---------------------------------------------------------------------------
def draw_dp_cell_frame(
    K: Table,
    weights: Sequence[int],
    values: Sequence[int],
    names: Sequence[str],
    i: int,
    w: int,
    cols: Optional[Sequence[int]] = None,
    title: Optional[str] = None,
):
    """«Детальний кадр»: таблиця + повна формула переходу для клітинки ``(i, w)``.

    Угорі — таблиця, заповнена до ``(i, w)``: поточна клітинка помаранчева,
    джерело «не брати» — синє (прямо над), джерело «взяти» — зелене (рядок вище,
    лівіше на вагу предмета). Унизу — формула: яка гілка спрацювала і чому.

    :returns: об'єкт ``Figure``.
    """
    n = len(K) - 1
    all_cols = list(range(len(K[0])))
    cols = all_cols if cols is None else list(cols)
    ncols = len(cols)

    fw, fh = _table_figsize(n + 1, ncols)
    fig, (ax, axf) = plt.subplots(
        2, 1, figsize=(max(fw, 8.6), fh + 2.35),
        gridspec_kw={"height_ratios": [fh, 2.1]})
    draw_dp_table(ax, K, weights, values, names, cols=cols, upto=(i, w),
                  current=(i, w), show_sources=True)

    axf.axis("off")
    wi, vi = weights[i - 1], values[i - 1]
    fits = wi <= w
    if fits:
        skip = K[i - 1][w]
        take = vi + K[i - 1][w - wi]
        took = take > skip
        win = t("   ← перемагає")
        formula = (
            t("Вага {name} = {wi}  ≤  w = {w}   → вміщується").format(
                name=names[i - 1], wi=wi, w=w) + "\n\n"
            + t("не брати : K[{i1}][{w}] = {skip}").format(i1=i - 1, w=w, skip=skip)
            + (win if not took else "") + "\n"
            + t("взяти    : {vi} + K[{i1}][{wleft}] = {vi}+{rest} = {take}").format(
                vi=vi, i1=i - 1, wleft=w - wi, rest=K[i - 1][w - wi], take=take)
            + (win if took else "") + "\n\n"
            + f"K[{i}][{w}] = max({skip}, {take}) = {K[i][w]}"
        )
        box = "#e8f5e9" if took else "#e3f2fd"
    else:
        formula = (
            t("Вага {name} = {wi}  >  w = {w}").format(name=names[i - 1], wi=wi, w=w)
            + "\n" + t("→ предмет НЕ вміщується")
            + "\n" + t("→ копіюємо значення згори") + "\n\n"
            + f"K[{i}][{w}] = K[{i - 1}][{w}] = {K[i][w]}"
        )
        box = "#fff3e0"
    axf.text(0.02, 0.92, formula, ha="left", va="top", fontsize=11,
             family="monospace", color=TEXT_FORMULA, transform=axf.transAxes,
             bbox=dict(boxstyle="round,pad=0.6", facecolor=box, edgecolor="#888"))

    legend = (t("помаранчевий — поточна клітинка") + "\n"
              + t("синій — джерело «не брати»") + "\n"
              + t("зелений — джерело «взяти»"))
    axf.text(0.99, 0.92, legend, ha="right", va="top", fontsize=8.5,
             color="#444", transform=axf.transAxes,
             bbox=dict(boxstyle="round,pad=0.4", facecolor="#fafafa", edgecolor="#ccc"))

    fig.suptitle(title if title is not None
                 else t("Заповнення клітинки K[{i}][{w}] (предмет {name}, місткість w={w})").format(
                     i=i, w=w, name=names[i - 1]),
                 fontsize=12.5, fontweight="bold")
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    return fig


# ---------------------------------------------------------------------------
# Зведена сітка: таблиця після кожного рядка
# ---------------------------------------------------------------------------
def draw_dp_evolution(
    K: Table,
    weights: Sequence[int],
    values: Sequence[int],
    names: Sequence[str],
    suptitle: str,
    cols: Optional[Sequence[int]] = None,
    ncols_grid: int = 2,
):
    """Зведена сітка: стан таблиці після заповнення кожного рядка ``i``.

    Таблиця ДП ніколи не переписує готові клітинки, тож «знімок після рядка
    ``i``» — це просто таблиця, заповнена до кінця цього рядка (``upto``).

    :returns: об'єкт ``Figure``.
    """
    n = len(K) - 1
    W = len(K[0]) - 1
    panels = n + 1
    nrow_grid = (panels + ncols_grid - 1) // ncols_grid
    cw = len(cols) if cols is not None else W + 1
    pw, ph = _table_figsize(n + 1, cw, scale=0.62)
    fig, axes = plt.subplots(nrow_grid, ncols_grid,
                             figsize=(pw * ncols_grid, ph * nrow_grid + 0.5))
    flat = axes.flatten() if hasattr(axes, "flatten") else [axes]

    for i in range(panels):
        title = (t("Рядок i=0: база (нулі)") if i == 0
                 else t("Після рядка i={i} (+{name})").format(i=i, name=names[i - 1]))
        draw_dp_table(flat[i], K, weights, values, names, title=title, cols=cols,
                      upto=(i, W), value_fontsize=10.5,
                      answer=(n, W) if i == n else None)
    for extra in range(panels, len(flat)):
        flat[extra].axis("off")

    fig.suptitle(suptitle, fontsize=14)
    fig.tight_layout(rect=(0, 0, 1, 0.97))
    return fig


# ---------------------------------------------------------------------------
# Відновлення набору зворотним проходом
# ---------------------------------------------------------------------------
def _path_cells(recon_steps: List[Step]) -> Set[Tuple[int, int]]:
    """Клітинки, через які проходить зворотний хід (для жовтої заливки)."""
    return {(s["i"], s["w"]) for s in recon_steps}


def draw_backtrack(
    K: Table,
    weights: Sequence[int],
    values: Sequence[int],
    names: Sequence[str],
    recon_steps: List[Step],
    cols: Optional[Sequence[int]] = None,
    title: Optional[str] = None,
    note: Optional[str] = None,
):
    """Статична картина відновлення: шлях зворотного проходу на фінальній таблиці.

    Жовті клітинки — шлях; зелені стрілки з підписом «+Пі» — предмет узято
    (хід ліворуч-угору на його вагу), сірі пунктирні — ні (хід прямо вгору).

    :param recon_steps: журнал :func:`knapsack.core.reconstruct_steps`.
    :returns: об'єкт ``Figure``.
    """
    n = len(K) - 1
    W = len(K[0]) - 1
    all_cols = list(range(len(K[0])))
    cols = all_cols if cols is None else list(cols)
    col_x = {w: j for j, w in enumerate(cols)}
    nrows = n + 1

    fig, ax = plt.subplots(figsize=_table_figsize(nrows, len(cols)))
    draw_dp_table(ax, K, weights, values, names, title=title, cols=cols,
                  path=_path_cells(recon_steps), answer=(n, W))

    def center(i: int, w: int) -> Tuple[float, float]:
        return col_x[w] + 0.5, (nrows - 1 - i) + 0.5

    for s in recon_steps:
        i, w, taken, w_after = s["i"], s["w"], s["taken"], s["w_after"]
        if w not in col_x or w_after not in col_x:
            continue
        src = center(i, w)
        dst = center(i - 1, w_after)
        color = GREEN_EDGE if taken else NEUTRAL_GRAY
        ax.annotate("", xy=dst, xytext=src, zorder=8,
                    arrowprops=dict(arrowstyle="-|>", color=color,
                                    lw=2.6 if taken else 1.6,
                                    linestyle="-" if taken else "--",
                                    shrinkA=13, shrinkB=13,
                                    connectionstyle="arc3,rad=0.18" if taken else None))
        label = (t("+{name}").format(name=names[i - 1]) if taken
                 else t("{name} ні").format(name=names[i - 1]))
        ax.text((src[0] + dst[0]) / 2 + (0.12 if taken else 0.06),
                (src[1] + dst[1]) / 2, label, fontsize=9, zorder=9,
                color=GREEN_EDGE if taken else NEUTRAL_GRAY, fontweight="bold",
                ha="left", va="center",
                bbox=dict(boxstyle="round,pad=0.13", fc="white", ec="none", alpha=0.9))
    if note:
        fig.text(0.5, 0.015, note, ha="center", va="bottom", fontsize=9,
                 color=MUTED_TXT, style="italic")
    fig.tight_layout(rect=(0, 0.05 if note else 0, 1, 1))
    return fig


def draw_backtrack_frame(
    K: Table,
    weights: Sequence[int],
    values: Sequence[int],
    names: Sequence[str],
    recon_steps: List[Step],
    upto_step: int,
    cols: Optional[Sequence[int]] = None,
):
    """Один кадр анімації відновлення: порівняння ``K[i][w]`` із клітинкою зверху.

    Поточна клітинка — помаранчева, клітинка зверху (``K[i-1][w]``) — у синій
    рамці; пройдена частина шляху — жовта. Підпис унизу — вердикт кроку.

    :param upto_step: індекс поточного кроку в ``recon_steps``.
    :returns: об'єкт ``Figure``.
    """
    n = len(K) - 1
    W = len(K[0]) - 1
    s = recon_steps[upto_step]
    i, w, taken = s["i"], s["w"], s["taken"]
    done = _path_cells(recon_steps[:upto_step])

    all_cols = list(range(len(K[0])))
    cols = all_cols if cols is None else list(cols)
    fw, fh = _table_figsize(n + 1, len(cols))
    fig, ax = plt.subplots(figsize=(max(fw, 7.2), fh + 0.75))
    draw_dp_table(ax, K, weights, values, names, cols=cols, path=done,
                  current=(i, w), compare=(i - 1, w), answer=(n, W),
                  title=t("Зворотний хід: рядок i={i}, місткість w={w}").format(i=i, w=w))

    if taken:
        caption = t("K[{i}][{w}]={v} ≠ K[{i1}][{w}]={a} → {name} УЗЯТО, w: {w} → {wa}").format(
            i=i, w=w, v=s["value"], i1=i - 1, a=s["above"],
            name=names[i - 1], wa=s["w_after"])
        color = GREEN_TXT
    else:
        caption = t("K[{i}][{w}]={v} = K[{i1}][{w}]={a} → {name} не брали, w лишається {w}").format(
            i=i, w=w, v=s["value"], i1=i - 1, a=s["above"], name=names[i - 1])
        color = SUBLABEL_TXT
    fig.text(0.5, 0.03, caption, ha="center", va="bottom", fontsize=10.5,
             family="monospace", color=color)
    fig.tight_layout(rect=(0, 0.07, 1, 1))
    return fig


# ---------------------------------------------------------------------------
# Смуги заповнення рюкзака (жадібний проти оптимуму)
# ---------------------------------------------------------------------------
def draw_fill_plans(
    plans: List[Dict],
    capacity: int,
    title: str,
):
    """Порівнює варіанти заповнення рюкзака горизонтальними смугами.

    :param plans: список планів; кожен — словник:

        * ``label`` — підпис ліворуч (наприклад, «Жадібний»);
        * ``items`` — індекси предметів у порядку пакування;
        * ``weights`` / ``values`` / ``names`` — параметри предметів;
        * ``total`` — підсумкова вартість (підпис праворуч).

    Невикористане місце домальовується сірим сегментом «порожньо».
    :returns: об'єкт ``Figure``.
    """
    rows = len(plans)
    fig, ax = plt.subplots(figsize=(10, 1.5 + rows * 1.05))
    ax.set_xlim(0, capacity * 1.24)
    ax.set_ylim(-0.65, rows - 0.2)
    ax.axis("off")

    ax.plot([capacity, capacity], [-0.5, rows - 0.42], color=ANSWER_EDGE,
            linestyle="--", linewidth=1.5)
    ax.text(capacity, rows - 0.36, t("місткість {W}").format(W=capacity),
            ha="center", va="bottom", fontsize=10, color=ANSWER_EDGE)

    for r, plan in enumerate(plans):
        y = rows - 1 - r
        weights, names = plan["weights"], plan["names"]
        x = 0.0
        for i in plan["items"]:
            wseg = weights[i]
            ax.add_patch(plt.Rectangle((x, y - 0.3), wseg, 0.6,
                                       facecolor=_item_color(i), edgecolor="white"))
            ax.text(x + wseg / 2, y, t("{name} ({w})").format(name=names[i], w=wseg),
                    ha="center", va="center", fontsize=9.5, color="white",
                    fontweight="bold")
            x += wseg
        slack = capacity - x
        if slack > 0:
            ax.add_patch(plt.Rectangle((x, y - 0.3), slack, 0.6,
                                       facecolor=SLACK_FILL, edgecolor="white"))
            ax.text(x + slack / 2, y, t("порожньо ({s})").format(s=int(slack)),
                    ha="center", va="center", fontsize=9.5, color="#666")
        ax.text(-capacity * 0.012, y, plan["label"], ha="right", va="center",
                fontsize=11)
        ax.text(capacity * 1.015, y, f"= {plan['total']}", ha="left", va="center",
                fontsize=11.5, fontweight="bold",
                color=GREEN_TXT if plan.get("best") else TEXT_DARK)

    ax.set_title(title, fontsize=12.5, pad=10)
    fig.tight_layout()
    return fig


# ---------------------------------------------------------------------------
# Текстові підсумки (консоль)
# ---------------------------------------------------------------------------
def dp_cell_log_line(step: Step, weights: Sequence[int], values: Sequence[int]) -> str:
    """Один рядок журналу заповнення для клітинки (формат — як у конспекті)."""
    i, w = step["i"], step["w"]
    if step["kind"] == "base":
        return t("K[{i}][{w}]: базовий випадок (i=0 або w=0)  =>  0").format(i=i, w=w)
    wi, vi = weights[i - 1], values[i - 1]
    if step["kind"] == "nofit":
        return t("K[{i}][{w}]: вага {wi} > {w} -> не вміщується -> беремо згори K[{i1}][{w}]={skip}  =>  {val}").format(
            i=i, w=w, wi=wi, i1=i - 1, skip=step["skip"], val=step["value"])
    return t("K[{i}][{w}]: вага {wi} <= {w} -> вміщується -> max(не брати={skip}, взяти {vi}+K[{i1}][{wleft}]={take})  =>  {val}").format(
        i=i, w=w, wi=wi, skip=step["skip"], vi=vi, i1=i - 1,
        wleft=w - wi, take=step["take"], val=step["value"])


def print_dp_log(
    steps: List[Step],
    weights: Sequence[int],
    values: Sequence[int],
    names: Sequence[str],
    skip_base: bool = True,
) -> None:
    """Друкує повний журнал заповнення таблиці, рядок за рядком (= предмет за предметом).

    :param skip_base: не друкувати клітинки базового рядка ``i = 0`` (усі нулі).
    """
    current_row = None
    for s in steps:
        i = s["i"]
        if skip_base and i == 0:
            continue
        if i != current_row:
            current_row = i
            print(t("\n=== Рядок i={i}  ({name}: вага={w}, вартість={v}) ===").format(
                i=i, name=names[i - 1], w=weights[i - 1], v=values[i - 1]))
        if skip_base and s["kind"] == "base":
            print(t("K[{i}][{w}]: базовий випадок (w=0)  =>  0").format(i=i, w=s["w"]))
            continue
        print(dp_cell_log_line(s, weights, values))


def print_dp_table(
    K: Table,
    names: Sequence[str],
    cols: Optional[Sequence[int]] = None,
) -> None:
    """Друкує таблицю ``K`` вирівняним текстом (``cols`` — підмножина стовпців)."""
    n = len(K) - 1
    cols = list(range(len(K[0]))) if cols is None else list(cols)
    width = max(3, max(len(str(K[i][w])) for i in range(n + 1) for w in cols))
    row_titles = ["0 (—)"] + [t("{i} +{name}").format(i=i, name=names[i - 1])
                              for i in range(1, n + 1)]
    title_w = max(len(rt) for rt in row_titles)
    header = " i \\ w".ljust(title_w + 2) + "|" + "".join(
        f"{w:>{width + 1}}" for w in cols)
    print(header)
    print("-" * (title_w + 2) + "+" + "-" * ((width + 1) * len(cols)))
    for i in range(n + 1):
        print(" " + row_titles[i].ljust(title_w + 1) + "|" + "".join(
            f"{K[i][w]:>{width + 1}}" for w in cols))


def print_subsets(
    steps: List[Step],
    names: Sequence[str],
    capacity: int,
) -> None:
    """Друкує таблицю перебору: підмножина, вага, вартість, вердикт."""
    label_w = max(len(format_combo(s["combo"], names)) for s in steps) + 2
    print(t("{combo}  {w}  {v}  підсумок").format(
        combo=t("підмножина").ljust(label_w), w=t("вага").rjust(5),
        v=t("вартість").rjust(9)))
    print("-" * (label_w + 2 + 5 + 2 + 9 + 2 + 24))
    for s in steps:
        combo = format_combo(s["combo"], names).ljust(label_w)
        if not s["fits"]:
            verdict = t("не влазить ({w} > {W})").format(w=s["weight"], W=capacity)
        elif s["improved"]:
            verdict = t("влазить — нова найкраща ★")
        else:
            verdict = t("влазить")
        print(f"{combo}  {s['weight']:>5}  {s['value']:>9}  {verdict}")
