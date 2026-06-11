# -*- coding: utf-8 -*-
"""Покрокова візуалізація «код ↔ таблиця» для задачі про рюкзак.

Кожен крок — це рядок із двох панелей: **ліворуч фрагмент коду ДП з підсвіченими
активними рядками**, **праворуч стан таблиці K** саме на цьому кроці. Колір
рядка коду кодує гілку, що спрацювала: «взяти» (зелений) чи «значення зверху»
(червоний — «не брати» перемогло або предмет не влазить).

Три незалежні блоки + композитор:

* **журнал** (:func:`build_overview_steps`, :func:`build_cell_steps`) — проганяє
  алгоритм і складає список **незмінних знімків**; знає алгоритм, нічого не малює;
* **кодова панель** (:func:`draw_code_panel`) — малює :data:`CODE` і підсвічує
  рядки за мапою ``{індекс: колір}`` зі знімка; нічого не знає про алгоритм;
* **панель стану** — повторно використовуємо :func:`visualization.draw_dp_table`;
* **композитор** (:func:`render_code_step`, :func:`draw_code_walkthrough_grid`) —
  складає панелі в одну фігуру / у високу сітку.

Два рівні деталізації (обидва будуються з одного журналу):

* **оглядовий** — один крок на рядок таблиці ``i`` (= на предмет); праворуч
  таблиця після заповнення рядка; :func:`build_overview_steps`;
* **по клітинках** — для одного обраного рядка ``i`` крок = одна клітинка
  ``(i, w)``; колір коду показує, **яка гілка** спрацювала;
  :func:`build_cell_steps`.

Двомовність: увесь видимий текст через :func:`knapsack.i18n.t`; кольори —
зі :mod:`knapsack.style`.
"""

from __future__ import annotations

from typing import Dict, List, Optional, Sequence, Tuple

import matplotlib.pyplot as plt
from matplotlib.patches import Patch, Rectangle

from .core import knapsack_dp_steps
from .i18n import t
from .style import (
    HL_ACTIVE,
    HL_TAKE,
    HL_COPY,
    GREEN_TXT,
    MUTED_TXT,
    TEXT_DARK,
    TEXT_FORMULA,
)
from .visualization import draw_dp_table

__all__ = [
    "CODE",
    "build_overview_steps",
    "build_cell_steps",
    "pick_illustrative",
    "best_focus_row",
    "draw_code_panel",
    "render_code_step",
    "draw_code_walkthrough_grid",
    "code_legend_handles",
]


# ---------------------------------------------------------------------------
# «Код як дані»: один елемент списку = один рядок коду. Індекси СТАБІЛЬНІ — саме
# на них посилається мапа підсвічування `hl`. Рядки дослівно повторюють
# `core.knapsack_dp` з ЄДИНИМ відхиленням: max(...) розгорнуто у take/skip, як
# у журнальній версії конспекту, щоб гілки «взяти»/«не брати» підсвічувались
# окремими рядками (саме це відхилення згадує й README).
# ---------------------------------------------------------------------------
CODE: List[str] = [
    "K = [[0 for w in range(W + 1)] for i in range(n + 1)]",  # 0  init: нулі
    "",                                                       # 1
    "for i in range(n + 1):",                          # 2  ← оглядовий крок (рядок)
    "    for w in range(W + 1):",                      # 3  ← скан місткостей
    "        if i == 0 or w == 0:",                    # 4  ← базовий випадок?
    "            K[i][w] = 0",                         # 5  ← база: нуль
    "        elif wt[i - 1] <= w:",                    # 6  ← предмет влазить?
    "            take = val[i - 1] + K[i - 1][w - wt[i - 1]]",  # 7 ← «взяти»
    "            skip = K[i - 1][w]",                  # 8  ← варіант «не брати»
    "            K[i][w] = max(take, skip)",           # 9  ← лишаємо більший
    "        else:",                                   # 10
    "            K[i][w] = K[i - 1][w]",               # 11 ← не влазить: згори
]

# Семантичні набори рядків для `hl` (значення — кольори зі style.py):
_HL_INIT = {0: HL_ACTIVE}                                    # створили таблицю
_HL_LOOPS = {2: HL_ACTIVE, 3: HL_ACTIVE}                     # «крутяться» цикли
_HL_BASE = {4: HL_ACTIVE, 5: HL_COPY}                        # базовий випадок → 0
_HL_TAKE_WINS = {6: HL_ACTIVE, 7: HL_TAKE, 8: HL_ACTIVE, 9: HL_TAKE}   # взяти >
_HL_SKIP_WINS = {6: HL_ACTIVE, 7: HL_ACTIVE, 8: HL_COPY, 9: HL_COPY}   # не брати ≥
_HL_NOFIT = {6: HL_ACTIVE, 10: HL_ACTIVE, 11: HL_COPY}       # не влазить → згори


# ---------------------------------------------------------------------------
# Дрібні допоміжні
# ---------------------------------------------------------------------------
def best_focus_row(W: int, wt: Sequence[int], val: Sequence[int], n: int) -> int:
    """Рядок таблиці з найрізноманітнішими гілками — найкращий для розбору.

    Рахуємо, скільки РІЗНИХ гілок (``nofit`` / ``take`` / ``skip``) трапляється
    в кожному рядку; за рівності беремо нижчий рядок (пізніший предмет).

    :raises ValueError: для виродженого інстансу (``n = 0`` або ``W = 0``) —
        кожна клітинка там базова, тож «показового» рядка не існує.
    """
    _, _, steps = knapsack_dp_steps(W, wt, val, n)
    kinds_per_row: Dict[int, set] = {}
    for s in steps:
        if s["i"] >= 1 and s["kind"] != "base":
            kinds_per_row.setdefault(s["i"], set()).add(s["kind"])
    if not kinds_per_row:
        raise ValueError(
            "best_focus_row: вироджений інстанс (немає предметів або W = 0) — "
            "жодної клітинки з рішенням «взяти / не брати».")
    return max(kinds_per_row, key=lambda i: (len(kinds_per_row[i]), i))


# ---------------------------------------------------------------------------
# Блок 1 — журнал кроків (таблиця ДП не переписує клітинок, тож знімок стану —
# це просто готова таблиця K + позиція «доки заповнено»)
# ---------------------------------------------------------------------------
def build_overview_steps(
    W: int, wt: Sequence[int], val: Sequence[int], n: int,
    names: Sequence[str],
) -> List[Dict]:
    """Оглядовий журнал: один крок на рядок таблиці ``i`` (= на предмет)."""
    _, K, cell_steps = knapsack_dp_steps(W, wt, val, n)
    steps: List[Dict] = [{
        "kind": "init",
        "hl": dict(_HL_INIT),
        "K": K, "upto": (0, W), "current": None,
        "title": t("Рядок i=0: база (нулі)"),
        "caption": t("Створили таблицю (n+1)×(W+1); рядок i=0 — «нуль предметів» → нулі"),
    }]
    for i in range(1, n + 1):
        taken = sum(1 for s in cell_steps if s["i"] == i and s["kind"] == "take")
        steps.append({
            "kind": "row",
            "hl": dict(_HL_LOOPS),
            "K": K, "upto": (i, W), "current": None,
            "title": t("Після рядка i={i} (+{name})").format(i=i, name=names[i - 1]),
            "caption": t("Рядок i={i}: предмет {name} (вага {w}, цінність {v}); гілка «взяти» перемогла у {c} клітинках").format(
                i=i, name=names[i - 1], w=wt[i - 1], v=val[i - 1], c=taken),
        })
    steps.append({
        "kind": "final",
        "hl": {},
        "K": K, "upto": (n, W), "current": None, "answer": (n, W),
        "title": t("Таблицю заповнено"),
        "caption": t("Відповідь — у правому нижньому куті: K[{n}][{W}] = {v}").format(
            n=n, W=W, v=K[n][W]),
    })
    return steps


def build_cell_steps(
    W: int, wt: Sequence[int], val: Sequence[int], n: int,
    focus_row: int,
    names: Sequence[str],
) -> List[Dict]:
    """Детальний журнал для одного рядка ``focus_row``: крок = одна клітинка.

    Колір коду в кожному знімку відповідає гілці, що реально спрацювала в
    :func:`core.knapsack_dp_steps` (звіряємось із його журналом).
    """
    _, K, cell_steps = knapsack_dp_steps(W, wt, val, n)
    name = names[focus_row - 1]
    wi, vi = wt[focus_row - 1], val[focus_row - 1]

    steps: List[Dict] = [{
        "kind": "row",
        "hl": dict(_HL_LOOPS),
        "K": K, "upto": (focus_row - 1, W), "current": None,
        "title": t("Рядок i={i}: стан до заповнення").format(i=focus_row),
        "caption": t("Беремося за предмет {name} (вага {w}, цінність {v}); внутрішній цикл пройде w = 0…{W}").format(
            name=name, w=wi, v=vi, W=W),
    }]

    for s in cell_steps:
        if s["i"] != focus_row:
            continue
        w = s["w"]
        kind = s["kind"]
        if kind == "base":
            hl, caption = dict(_HL_BASE), t("w=0: місця немає — базовий випадок, K[{i}][0] = 0").format(i=focus_row)
        elif kind == "nofit":
            hl = dict(_HL_NOFIT)
            caption = t("w={w}: вага {wi} > {w} — не влазить → K[{i}][{w}] = K[{i1}][{w}] = {v}").format(
                w=w, wi=wi, i=focus_row, i1=focus_row - 1, v=s["value"])
        elif kind == "take":
            hl = dict(_HL_TAKE_WINS)
            caption = t("w={w}: max(взяти {take}, не брати {skip}) = {v}  ✔ беремо {name}").format(
                w=w, take=s["take"], skip=s["skip"], v=s["value"], name=name)
        else:
            hl = dict(_HL_SKIP_WINS)
            caption = t("w={w}: max(взяти {take}, не брати {skip}) = {v}  — вигідніше без {name}").format(
                w=w, take=s["take"], skip=s["skip"], v=s["value"], name=name)
        steps.append({
            "kind": kind, "hl": hl,
            "K": K, "upto": (focus_row, w), "current": (focus_row, w),
            "show_sources": kind in ("take", "skip"),
            "title": t("Рядок i={i}: клітинка w={w}").format(i=focus_row, w=w),
            "caption": caption,
        })

    taken = sum(1 for s in cell_steps if s["i"] == focus_row and s["kind"] == "take")
    steps.append({
        "kind": "final",
        "hl": {},
        "K": K, "upto": (focus_row, W), "current": None,
        "title": t("Рядок i={i} готовий").format(i=focus_row),
        "caption": t("Підсумок рядка: «взяти {name}» перемогло у {c} клітинках").format(
            name=name, c=taken),
    })
    return steps


def pick_illustrative(steps: List[Dict]) -> List[Dict]:
    """Кураторський зріз журналу по клітинках для СТАТИЧНОЇ сітки.

    Лишає контекст-крок рядка, по одному показовому прикладу кожної гілки
    (база / не влазить / «не брати») , УСІ кроки «взяти» та підсумок — щоб
    сітка була читомою. Повний журнал (усі клітинки) лишаємо для анімації.
    """
    out: List[Dict] = []
    seen = {"base": 0, "nofit": 0, "skip": 0}
    for s in steps:
        kind = s["kind"]
        if kind in ("init", "row", "take", "final"):
            out.append(s)
        elif kind in seen and seen[kind] < 1:
            out.append(s)
            seen[kind] += 1
    return out


# ---------------------------------------------------------------------------
# Блок 2 — кодова панель (ліворуч)
# ---------------------------------------------------------------------------
def draw_code_panel(ax, highlights: Dict[int, str], code: Sequence[str] = CODE,
                    *, fontsize: float = 10.0) -> None:
    """Малює ``code`` на осі ``ax`` і підсвічує рядки за мапою ``highlights``.

    :param highlights: ``{індекс_рядка: колір_заливки}`` зі знімка журналу.
    Рендер **чистий**: та сама мапа → та сама картинка, без знання про алгоритм.
    """
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    nlines = len(code)
    line_h = 1.0 / nlines
    for i, line in enumerate(code):
        y = 1.0 - (i + 0.5) * line_h
        if i in highlights:
            ax.add_patch(Rectangle((0, y - line_h * 0.46), 1, line_h * 0.92,
                                   facecolor=highlights[i], edgecolor="none", zorder=0))
        ax.text(0.02, y, line, family="monospace", fontsize=fontsize,
                va="center", ha="left", color=TEXT_DARK, zorder=2)


def code_legend_handles() -> List[Patch]:
    """Хендли легенди підсвічування коду (для ``fig.legend``)."""
    return [
        Patch(facecolor=HL_ACTIVE, edgecolor="none", label=t("активний рядок")),
        Patch(facecolor=HL_TAKE, edgecolor="none", label=t("гілка «взяти» перемогла")),
        Patch(facecolor=HL_COPY, edgecolor="none", label=t("значення зверху (не брати / не влазить)")),
    ]


def _caption_color(kind: str) -> str:
    """Колір підпису-вердикту за типом кроку."""
    if kind == "take":
        return GREEN_TXT
    if kind in ("nofit", "base"):
        return MUTED_TXT
    return TEXT_FORMULA


def _draw_state(ax, step: Dict, weights: Sequence[int], values: Sequence[int],
                names: Sequence[str], cols: Optional[Sequence[int]]) -> None:
    """Права панель: стан таблиці зі знімка журналу."""
    draw_dp_table(
        ax, step["K"], weights, values, names,
        title=step["title"], cols=cols,
        upto=step["upto"], current=step.get("current"),
        show_sources=step.get("show_sources", False),
        answer=step.get("answer"),
        value_fontsize=10.5,
    )


# ---------------------------------------------------------------------------
# Композитор — одна фігура на крок (анімація) + повна сітка (статика)
# ---------------------------------------------------------------------------
def render_code_step(
    step: Dict,
    weights: Sequence[int],
    values: Sequence[int],
    names: Sequence[str],
    cols: Optional[Sequence[int]] = None,
    figsize: Tuple[float, float] = (11.0, 3.6),
):
    """Один крок → одна фігура ``[код | таблиця]`` (кадр для анімації).

    :returns: об'єкт ``Figure``.
    """
    fig, (axc, axr) = plt.subplots(1, 2, figsize=figsize,
                                   gridspec_kw={"width_ratios": [1.05, 1]})
    draw_code_panel(axc, step["hl"])
    _draw_state(axr, step, weights, values, names, cols)
    if step.get("caption"):
        fig.text(0.5, 0.025, step["caption"], ha="center", va="bottom",
                 fontsize=9.5, family="monospace", color=_caption_color(step["kind"]))
    fig.subplots_adjust(left=0.03, right=0.97, top=0.92, bottom=0.13, wspace=0.06)
    return fig


def draw_code_walkthrough_grid(
    steps: List[Dict],
    weights: Sequence[int],
    values: Sequence[int],
    names: Sequence[str],
    suptitle: str,
    cols: Optional[Sequence[int]] = None,
    row_h: float = 3.3,
    width: float = 11.0,
    legend: bool = True,
):
    """Усі ``steps`` у ОДНІЙ високій сітці: рядок = ``[код | таблиця]``.

    :param steps: журнал (повний або кураторський зріз :func:`pick_illustrative`).
    :returns: об'єкт ``Figure``.
    """
    nrow = len(steps)
    fig, axes = plt.subplots(nrow, 2, figsize=(width, row_h * nrow),
                             gridspec_kw={"width_ratios": [1.05, 1]})
    if nrow == 1:
        axes = [axes]
    for r, step in enumerate(steps):
        axc, axr = axes[r]
        draw_code_panel(axc, step["hl"])
        _draw_state(axr, step, weights, values, names, cols)
        if step.get("caption"):
            axr.text(0.5, -0.09, step["caption"], transform=axr.transAxes,
                     ha="center", va="top", fontsize=8.6, family="monospace",
                     color=_caption_color(step["kind"]), clip_on=False)

    fig.suptitle(suptitle, fontsize=14, fontweight="bold")
    bottom = 0.04 if legend else 0.01
    if legend:
        fig.legend(handles=code_legend_handles(), loc="lower center", ncol=3,
                   frameon=False, fontsize=10, bbox_to_anchor=(0.5, 0.002))
    fig.tight_layout(rect=(0, bottom, 1, 0.985), h_pad=5.0)
    return fig
