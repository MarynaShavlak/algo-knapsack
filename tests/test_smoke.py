"""Smoke-тести: візуалізація, збірка GIF та i18n виконуються без помилок.

На відміну від ``test_core.py`` (який перевіряє ЧИСЛА), ці тести не звіряють
«правильність картинки» — лише що кожна функція малювання повертає фігуру й не
кидає винятків, що ``save_gif`` збирає валідний GIF, що панелі «код ↔ таблиця»
будуються, а ВСІ кириличні підписи (і пакета, і прикладів) мають англійський
переклад: динамічний аудит ``missing_translations`` після повного рендера в
режимі ``en`` плюс статичний AST-аудит літералів ``t("…")`` у вихідних файлах.

Потребують ``matplotlib`` і ``pillow``.

Запуск::

    pytest
    python tests/test_smoke.py    # вбудований раннер, без pytest
"""

from __future__ import annotations

import ast
import io
import os
import sys
import tempfile
from contextlib import redirect_stdout

import matplotlib

matplotlib.use("Agg")  # без графічного дисплея — ДО імпорту pyplot

import matplotlib.pyplot as plt  # noqa: E402

# корінь репозиторію та examples/ у sys.path
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in (_ROOT, os.path.join(_ROOT, "examples")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

from knapsack.animation import save_animation, save_gif  # noqa: E402
from knapsack.core import (  # noqa: E402
    brute_force_steps,
    knapsack_dp_steps,
    reconstruct_steps,
)
from knapsack.i18n import _CYRILLIC, _EN, missing_translations, set_lang  # noqa: E402
from knapsack.visualization import (  # noqa: E402
    configure_style,
    dp_cell_log_line,
    draw_backtrack,
    draw_backtrack_frame,
    draw_dp_cell_frame,
    draw_dp_evolution,
    draw_dp_table,
    draw_dp_table_standalone,
    draw_fill_plans,
    draw_growth,
    draw_items,
    draw_recursion_tree,
    draw_subsets,
    format_combo,
    item_names,
    print_dp_log,
    print_dp_table,
    print_subsets,
)

# Малий інстанс із конспекту: у рядку 3 трапляються ВСІ гілки переходу
# (база, «не влазить», «не брати» перемогло, «взяти» перемогло).
_W, _WT, _VAL = 4, [1, 2, 3], [6, 10, 12]
_N = len(_WT)


def _render_everything() -> None:
    """Повний рендер усіх фігур і текстів пакета (для аудиту перекладів)."""
    configure_style()
    names = item_names(_N)
    best, K, steps = knapsack_dp_steps(_W, _WT, _VAL, _N)
    _, _, bf_steps = brute_force_steps(_W, _WT, _VAL)
    chosen, recon = reconstruct_steps(K, _WT, _W)

    plt.close(draw_items(_WT, _VAL, names, _W))
    plt.close(draw_subsets(bf_steps, _WT, _VAL, names, _W))
    plt.close(draw_subsets(bf_steps, _WT, _VAL, names, _W, upto=3))
    plt.close(draw_recursion_tree(_W, _WT, _VAL, names))
    plt.close(draw_growth(n_max=12, dp_w=_W, big=(10, 20)))
    plt.close(draw_growth(n_max=12, dp_w=_W))

    fig, ax = plt.subplots()
    draw_dp_table(ax, K, _WT, _VAL, names, title="t", current=(2, 3),
                  show_sources=True, upto=(2, 3))
    plt.close(fig)
    plt.close(draw_dp_table_standalone(K, _WT, _VAL, names, answer=(_N, _W),
                                       note="t", take_cells={(1, 1)}))
    plt.close(draw_dp_table_standalone(K, _WT, _VAL, names, cols=[0, 2, 4]))
    for i, w in ((1, 1), (3, 3), (3, 4), (2, 1)):   # взяти / не брати / не влазить
        plt.close(draw_dp_cell_frame(K, _WT, _VAL, names, i, w))
    plt.close(draw_dp_evolution(K, _WT, _VAL, names, "t"))
    plt.close(draw_backtrack(K, _WT, _VAL, names, recon, note="t"))
    for k in range(len(recon)):
        plt.close(draw_backtrack_frame(K, _WT, _VAL, names, recon, k))
    plt.close(draw_fill_plans(
        [{"label": "t", "items": chosen, "weights": _WT, "values": _VAL,
          "names": names, "total": best, "best": True}], _W, "t"))

    buf = io.StringIO()
    with redirect_stdout(buf):
        print_dp_log(steps, _WT, _VAL, names)
        print_dp_table(K, names, cols=[0, 2, 4])
        print_subsets(bf_steps, names, _W)
    for s in steps:
        if s["kind"] != "base":
            dp_cell_log_line(s, _WT, _VAL)

    from knapsack.walkthrough import (  # noqa: E402
        best_focus_row,
        build_cell_steps,
        build_overview_steps,
        draw_code_walkthrough_grid,
        pick_illustrative,
        render_code_step,
    )
    overview = build_overview_steps(_W, _WT, _VAL, _N, names)
    cells = build_cell_steps(_W, _WT, _VAL, _N, best_focus_row(_W, _WT, _VAL, _N), names)
    plt.close(draw_code_walkthrough_grid(pick_illustrative(cells), _WT, _VAL, names, "t"))
    plt.close(draw_code_walkthrough_grid(overview, _WT, _VAL, names, "t",
                                         cols=[0, 2, 4]))
    for s in cells:
        plt.close(render_code_step(s, _WT, _VAL, names))


def test_draw_functions_return_figures():
    """Кожна функція малювання відпрацьовує без винятків (повний прохід)."""
    _render_everything()


def test_subsets_helpers():
    """format_combo та таблиця перебору обробляють порожню підмножину."""
    names = item_names(3)
    assert format_combo((), names) == "{ }"
    assert format_combo((1, 2), names).startswith("{")
    _, _, steps = brute_force_steps(_W, _WT, _VAL)
    buf = io.StringIO()
    with redirect_stdout(buf):
        print_subsets(steps, names, _W)
    out = buf.getvalue()
    assert "{ }" in out and "★" in out


def test_save_gif_creates_valid_gif():
    """save_gif збирає багатокадровий GIF із кількох фігур."""
    from PIL import Image

    frames = []
    for i in range(3):
        fig, ax = plt.subplots(figsize=(2, 2))
        ax.plot([0, 1], [0, i + 1])   # кадри РІЗНІ, інакше GIF злив би їх в один
        ax.set_title(str(i))
        frames.append(fig)

    with tempfile.TemporaryDirectory() as d:
        out = os.path.join(d, "smoke.gif")
        save_gif(frames, out, [200, 200, 200])
        assert os.path.exists(out)
        with Image.open(out) as im:
            assert im.n_frames == 3
            assert im.info.get("loop") == 0


def test_save_gif_rejects_empty():
    """Порожній список кадрів має давати зрозумілий ValueError, а не падати глибше."""
    with tempfile.TemporaryDirectory() as d:
        raised = False
        try:
            save_gif([], os.path.join(d, "x.gif"), 100)
        except ValueError:
            raised = True
        assert raised, "save_gif мав кинути ValueError на порожньому списку"


def test_save_animation_writes_gif_and_maybe_mp4():
    """save_animation: GIF збирається ЗАВЖДИ; MP4 — лише якщо доступний ffmpeg."""
    from PIL import Image

    frames = []
    for i in range(3):
        fig, ax = plt.subplots(figsize=(2.5, 2))   # непарні пікселі — перевірка парного паддингу MP4
        ax.plot([0, 1], [0, i + 1])                # кадри різні, інакше відео «злило» б їх
        ax.set_title(str(i))
        frames.append(fig)

    with tempfile.TemporaryDirectory() as d:
        gif = os.path.join(d, "anim.gif")
        mp4 = os.path.join(d, "anim.mp4")
        result = save_animation(frames, gif, [200, 200, 200], mp4_path=mp4)

        assert os.path.exists(gif)                  # GIF — гарантований формат
        with Image.open(gif) as im:
            assert im.n_frames == 3
        # MP4 — best-effort: якщо ffmpeg є, save_animation повертає шлях і файл існує;
        # якщо немає — повертає None і GIF усе одно зібрано (білд не падає).
        if result is not None:
            assert result == mp4
            assert os.path.exists(mp4) and os.path.getsize(mp4) > 0


def test_walkthrough_builds_and_renders():
    """walkthrough «код ↔ таблиця»: журнал будується, обидва рівні рендеряться."""
    from knapsack.walkthrough import (  # noqa: E402
        CODE,
        best_focus_row,
        build_cell_steps,
        build_overview_steps,
        pick_illustrative,
    )

    names = item_names(_N)
    # огляд: init + по одному кроку на рядок + фінал
    overview = build_overview_steps(_W, _WT, _VAL, _N, names)
    assert len(overview) == _N + 2
    assert overview[0]["kind"] == "init" and overview[-1]["kind"] == "final"

    # найпоказовіший рядок малого інстансу — третій (є всі гілки переходу)
    focus = best_focus_row(_W, _WT, _VAL, _N)
    assert focus == 3
    cells = build_cell_steps(_W, _WT, _VAL, _N, focus, names)
    kinds = {s["kind"] for s in cells}
    assert {"row", "base", "nofit", "skip", "take", "final"} <= kinds
    assert any(s["hl"] for s in cells)      # десь є підсвічування рядків коду
    assert len(pick_illustrative(cells)) < len(cells)
    assert all(isinstance(line, str) for line in CODE)


def test_dp_log_lines_format():
    """Текстовий журнал містить ключові пояснення для кожного типу клітинки."""
    _, _, steps = knapsack_dp_steps(_W, _WT, _VAL, _N)
    by_kind = {s["kind"]: s for s in steps if s["i"] >= 1}
    assert "не вміщується" in dp_cell_log_line(by_kind["nofit"], _WT, _VAL)
    assert "max(" in dp_cell_log_line(by_kind["take"], _WT, _VAL)
    assert "вміщується" in dp_cell_log_line(by_kind["skip"], _WT, _VAL)


def test_english_labels_complete():
    """Аудит i18n (динамічний): ПОВНИЙ рендер у режимі en не лишає кирилиці.

    Якщо якийсь кириличний рядок не знайшов перекладу, він опиниться в
    ``missing_translations`` — і тест назве його поіменно.
    """
    set_lang("en")
    missing_translations.clear()
    try:
        _render_everything()
        assert not missing_translations, \
            f"бракує перекладів: {sorted(missing_translations)}"
    finally:
        set_lang("uk")
        missing_translations.clear()


def test_source_t_literals_have_translations():
    """Аудит i18n (статичний): кожен літерал ``t("…")`` з кирилицею є у словнику.

    Динамічний аудит бачить лише рядки, що реально рендерилися; цей — парсить
    AST усіх файлів пакета й прикладів, тож ловить і рідкісні гілки (наприклад,
    діагностику відсутнього ffmpeg чи підписи разових прикладів).
    """
    missing = {}
    for folder in ("knapsack", "examples"):
        base = os.path.join(_ROOT, folder)
        for fname in sorted(os.listdir(base)):
            if not fname.endswith(".py"):
                continue
            path = os.path.join(base, fname)
            with open(path, encoding="utf-8") as fh:
                tree = ast.parse(fh.read(), filename=path)
            for node in ast.walk(tree):
                if (isinstance(node, ast.Call)
                        and isinstance(node.func, ast.Name)
                        and node.func.id == "t"
                        and node.args
                        and isinstance(node.args[0], ast.Constant)
                        and isinstance(node.args[0].value, str)):
                    key = node.args[0].value
                    if _CYRILLIC.search(key) and key not in _EN:
                        missing.setdefault(f"{folder}/{fname}", []).append(key)
    assert not missing, f"літерали без перекладу: {missing}"


def _run_without_pytest():
    """Мінімальний раннер; на відміну від ядра, ловить БУДЬ-ЯКИЙ виняток."""
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    failures = 0
    for test in tests:
        try:
            test()
            print(f"PASS  {test.__name__}")
        except Exception as exc:  # noqa: BLE001 — smoke: будь-яка помилка = провал
            failures += 1
            print(f"FAIL  {test.__name__}: {type(exc).__name__}: {exc}")
    print(f"\n{len(tests) - failures}/{len(tests)} smoke-тестів пройдено")
    return failures


if __name__ == "__main__":
    sys.exit(1 if _run_without_pytest() else 0)
