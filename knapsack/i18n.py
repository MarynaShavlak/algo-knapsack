# -*- coding: utf-8 -*-
"""Двомовні підписи для візуалізацій (uk за замовчуванням / en).

Замість важкої інфраструктури ``gettext``/``.po`` тут застосовано прийом
**«вихідний рядок — це і є ключ»**: ключем у словнику перекладів виступає сам
український рядок. Наслідки:

* **Мова за замовчуванням лишається байт-у-байт незмінною.** Коли ``LANG == "uk"``,
  :func:`t` повертає аргумент *без жодного пошуку* — український вивід (і всі
  раніше згенеровані рисунки) ідентичні тим, що були б і без i18n узагалі.
* **Відсутній переклад «деградує» безпечно** до вихідного рядка (``_EN.get(s, s)``):
  забули перекласти — отримаєте український підпис, а не ``KeyError`` чи ``"???"``.
* **Нуль інфраструктури** — один Python-файл, жодних білд-кроків.

Оркестратор (скрипти ``examples/``) перемикає мову через :func:`set_lang`
(``"en"`` із аргументів CLI) і кладе рисунки в ``docs/images/en/``. Той самий код
малювання, той самий білдер — змінюється лише глобальний ``LANG``, і всі виклики
:func:`t` всередині повертають переклад. Жодна функція-фігура не знає про мову.

Правила вживання у коді фігур:

* обгортайте **шаблон**, а не результат: ``t("…{x}…").format(x=v)``, ніколи
  ``t(f"…{v}…")`` — інакше ключ щоразу інакший і переклад не знайдеться;
* ключ у :data:`_EN` має збігатися з рядком у коді **символ-у-символ**, включно з
  пробілами, переносами ``\\n``, тире (``–`` en-dash ≠ ``-`` дефіс) та стрілками
  (``→``);
* суто формульні/символьні рядки (без жодного українського слова — напр.
  ``"K[3][4] = max(16, 18) = 18"``) у словник НЕ заносимо: :func:`t` поверне їх
  незмінними, а виглядають вони однаково обома мовами.
"""

from __future__ import annotations

import re
from typing import Dict, Set

#: Мова за замовчуванням (= вихідна мова рядків-ключів у коді).
LANG = "uk"

#: Будь-яка кирилична літера — ознака «це український рядок, а не формула/символи».
_CYRILLIC = re.compile(r"[Ѐ-ӿ]")

#: Аудит повноти перекладу: рядки з кирилицею, які в режимі ``en`` НЕ знайшлися в
#: :data:`_EN` (тобто лишилися б українськими). Наповнюється на льоту в :func:`t`;
#: має бути порожнім після повного прогону ``en`` — це й перевіряють тести/збірка.
missing_translations: Set[str] = set()


def set_lang(lang: str) -> None:
    """Встановити мову підписів: ``"uk"`` (типово) або ``"en"``."""
    global LANG
    assert lang in ("uk", "en"), lang
    LANG = lang


def get_lang() -> str:
    """Повернути поточну мову підписів (``"uk"`` або ``"en"``)."""
    return LANG


def t(s: str) -> str:
    """Повернути підпис мовою :data:`LANG` (ключ — вихідний український рядок).

    Для ``LANG == "uk"`` повертає ``s`` без змін (нульовий ризик регресій); для
    ``"en"`` — переклад із :data:`_EN`, а якщо його немає — безпечно сам ``s``.
    Якщо в режимі ``en`` рядок містить кирилицю, але перекладу немає, він
    запам'ятовується в :data:`missing_translations` (мовчазний аудит — не падаємо,
    лише фіксуємо «забутий» ключ).
    """
    if LANG == "uk":
        return s                # мова за замовчуванням: жодного пошуку, байт-у-байт
    out = _EN.get(s)
    if out is None:
        if _CYRILLIC.search(s):
            missing_translations.add(s)   # забутий/неточний ключ — фіксуємо для аудиту
        return s                # відсутній ключ -> безпечно повертаємо вихідний рядок
    return out


# ---------------------------------------------------------------------------
# Словник перекладів (uk -> en).
#
# Згруповано за місцем появи. Шаблони з {плейсхолдерами} перекладені цілком — у
# коді їх викликають як t(шаблон).format(...). НЕ перейменовуйте плейсхолдери:
# їхні імена мусять збігатися з тими, що у виклику .format().
# ---------------------------------------------------------------------------
_EN: Dict[str, str] = {
    # --- спільне: імена предметів ---------------------------------------------
    "П{i}": "I{i}",

    # --- visualization.draw_items («вітрина» задачі) ---------------------------
    "вага {w}": "weight {w}",
    "цінність {v}": "value {v}",
    "рюкзак: місткість {W}": "knapsack: capacity {W}",
    "разом: вага {tw}, цінність {tv}": "total: weight {tw}, value {tv}",
    "Задача про рюкзак: предмети та місткість":
        "The knapsack problem: items and capacity",

    # --- visualization.draw_subsets (повний перебір) ---------------------------
    "місткість {W}": "capacity {W}",
    "вага {w} · цінність {v}": "weight {w} · value {v}",
    "✗ не влазить ({w} > {W})": "✗ does not fit ({w} > {W})",
    "★ найкраща: {v}": "★ best: {v}",
    "Повний перебір: усі {m} підмножин ({n} предметів → 2^{n})":
        "Brute force: all {m} subsets ({n} items → 2^{n})",

    # --- visualization.draw_recursion_tree -------------------------------------
    "взяти {name} +{v}": "take {name} +{v}",
    "не брати {name}": "skip {name}",
    "Дерево рекурсії — повний перебір (зелене = оптимальний шлях)":
        "Recursion tree — brute force (green = the optimal path)",

    # --- visualization.draw_growth («чому це вибухає») -------------------------
    "повний перебір: 2ⁿ підмножин": "brute force: 2ⁿ subsets",
    "ДП: n·W клітинок (W = {W})": "DP: n·W cells (W = {W})",
    "2¹⁰ ≈ тисяча": "2¹⁰ ≈ a thousand",
    "2²⁰ ≈ мільйон": "2²⁰ ≈ a million",
    "2³⁰ ≈ мільярд": "2³⁰ ≈ a billion",
    "кількість предметів n": "number of items n",
    "обсяг роботи (лог-шкала)": "amount of work (log scale)",
    "Кожен новий предмет подвоює перебір": "Each new item doubles the search",
    "перебір": "brute force",
    "ДП": "DP",
    "Інстанс: n = {n}, W = {W}": "Instance: n = {n}, W = {W}",
    "підмножин / клітинок (лог-шкала)": "subsets / cells (log scale)",

    # --- visualization.draw_dp_table (підписи рядків) --------------------------
    "{i}: {name} (в={w}, ц={v})": "{i}: {name} (w={w}, v={v})",
    "Рядок i=0: база (нулі)": "Row i=0: base case (zeros)",
    "Після рядка i={i} (+{name})": "After row i={i} (+{name})",

    # --- visualization.draw_dp_cell_frame (формула переходу) -------------------
    "Вага {name} = {wi}  ≤  w = {w}   → вміщується":
        "Weight of {name} = {wi}  ≤  w = {w}   → it fits",
    "не брати : K[{i1}][{w}] = {skip}": "skip it : K[{i1}][{w}] = {skip}",
    "взяти    : {vi} + K[{i1}][{wleft}] = {vi}+{rest} = {take}":
        "take it : {vi} + K[{i1}][{wleft}] = {vi}+{rest} = {take}",
    "   ← перемагає": "   ← wins",
    "Вага {name} = {wi}  >  w = {w}": "Weight of {name} = {wi}  >  w = {w}",
    "→ предмет НЕ вміщується": "→ the item does NOT fit",
    "→ копіюємо значення згори": "→ copy the value from above",
    "помаранчевий — поточна клітинка": "orange — the current cell",
    "синій — джерело «не брати»": "blue — the “skip” source",
    "зелений — джерело «взяти»": "green — the “take” source",
    "Заповнення клітинки K[{i}][{w}] (предмет {name}, місткість w={w})":
        "Filling cell K[{i}][{w}] (item {name}, capacity w={w})",

    # --- visualization.draw_backtrack (відновлення набору) ---------------------
    "Зворотний хід: рядок i={i}, місткість w={w}":
        "Backward pass: row i={i}, capacity w={w}",
    "{name} ні": "{name}: no",
    "K[{i}][{w}]={v} ≠ K[{i1}][{w}]={a} → {name} УЗЯТО, w: {w} → {wa}":
        "K[{i}][{w}]={v} ≠ K[{i1}][{w}]={a} → {name} TAKEN, w: {w} → {wa}",
    "K[{i}][{w}]={v} = K[{i1}][{w}]={a} → {name} не брали, w лишається {w}":
        "K[{i}][{w}]={v} = K[{i1}][{w}]={a} → {name} not taken, w stays {w}",

    # --- visualization.draw_fill_plans (смуги заповнення) -----------------------
    "{name} ({w})": "{name} ({w})",
    "порожньо ({s})": "empty ({s})",

    # --- visualization: текстові журнали (консоль) ------------------------------
    "K[{i}][{w}]: базовий випадок (i=0 або w=0)  =>  0":
        "K[{i}][{w}]: base case (i=0 or w=0)  =>  0",
    "K[{i}][{w}]: вага {wi} > {w} -> не вміщується -> беремо згори K[{i1}][{w}]={skip}  =>  {val}":
        "K[{i}][{w}]: weight {wi} > {w} -> does not fit -> take from above K[{i1}][{w}]={skip}  =>  {val}",
    "K[{i}][{w}]: вага {wi} <= {w} -> вміщується -> max(не брати={skip}, взяти {vi}+K[{i1}][{wleft}]={take})  =>  {val}":
        "K[{i}][{w}]: weight {wi} <= {w} -> fits -> max(skip={skip}, take {vi}+K[{i1}][{wleft}]={take})  =>  {val}",
    "\n=== Рядок i={i}  ({name}: вага={w}, вартість={v}) ===":
        "\n=== Row i={i}  ({name}: weight={w}, value={v}) ===",
    "K[{i}][{w}]: базовий випадок (w=0)  =>  0":
        "K[{i}][{w}]: base case (w=0)  =>  0",
    "{combo}  {w}  {v}  підсумок": "{combo}  {w}  {v}  verdict",
    "підмножина": "subset",
    "вага": "weight",
    "вартість": "value",
    "не влазить ({w} > {W})": "does not fit ({w} > {W})",
    "влазить — нова найкраща ★": "fits — new best ★",
    "влазить": "fits",

    # --- walkthrough.py (панелі «код ↔ таблиця») --------------------------------
    "Створили таблицю (n+1)×(W+1); рядок i=0 — «нуль предметів» → нулі":
        "Created the (n+1)×(W+1) table; row i=0 — “zero items” → zeros",
    "Рядок i={i}: предмет {name} (вага {w}, цінність {v}); гілка «взяти» перемогла у {c} клітинках":
        "Row i={i}: item {name} (weight {w}, value {v}); the “take” branch won in {c} cells",
    "Таблицю заповнено": "The table is complete",
    "Відповідь — у правому нижньому куті: K[{n}][{W}] = {v}":
        "The answer sits in the bottom-right corner: K[{n}][{W}] = {v}",
    "Рядок i={i}: стан до заповнення": "Row i={i}: state before filling",
    "Беремося за предмет {name} (вага {w}, цінність {v}); внутрішній цикл пройде w = 0…{W}":
        "Processing item {name} (weight {w}, value {v}); the inner loop sweeps w = 0…{W}",
    "w=0: місця немає — базовий випадок, K[{i}][0] = 0":
        "w=0: no space — the base case, K[{i}][0] = 0",
    "w={w}: вага {wi} > {w} — не влазить → K[{i}][{w}] = K[{i1}][{w}] = {v}":
        "w={w}: weight {wi} > {w} — does not fit → K[{i}][{w}] = K[{i1}][{w}] = {v}",
    "w={w}: max(взяти {take}, не брати {skip}) = {v}  ✔ беремо {name}":
        "w={w}: max(take {take}, skip {skip}) = {v}  ✔ taking {name}",
    "w={w}: max(взяти {take}, не брати {skip}) = {v}  — вигідніше без {name}":
        "w={w}: max(take {take}, skip {skip}) = {v}  — better without {name}",
    "Рядок i={i}: клітинка w={w}": "Row i={i}: cell w={w}",
    "Рядок i={i} готовий": "Row i={i} done",
    "Підсумок рядка: «взяти {name}» перемогло у {c} клітинках":
        "Row summary: “take {name}” won in {c} cells",
    "активний рядок": "active line",
    "гілка «взяти» перемогла": "the “take” branch won",
    "значення зверху (не брати / не влазить)": "value from above (skip / does not fit)",

    # --- animation.save_animation (діагностика MP4, рідкісні шляхи) ------------
    "  ({name} пропущено — ffmpeg недоступний; pip install imageio-ffmpeg для відео)":
        "  ({name} skipped — ffmpeg unavailable; pip install imageio-ffmpeg for video)",
    "  ({name} пропущено: {err})": "  ({name} skipped: {err})",

    # --- examples/_common + назви інстансів (_items) ---------------------------
    "Інстанс «{label}»: місткість W = {W}, предметів n = {n}":
        "Instance “{label}”: capacity W = {W}, items n = {n}",
    "  {name}: вага {w}, цінність {v}": "  {name}: weight {w}, value {v}",
    "Обрані предмети: {items}": "Chosen items: {items}",
    "Сумарна вага:    {w}": "Total weight:    {w}",
    "Сумарна вартість: {v}": "Total value: {v}",
    "\nРисунки збережено у: {path}": "\nFigures saved to: {path}",
    "класичний": "classic",
    "малий": "small",
    "великий": "big",

    # --- examples/00_intro_items ------------------------------------------------
    "Мета: обрати предмети так, щоб сумарна вага ≤ {W}, а цінність — максимальна.":
        "Goal: pick items so that the total weight is ≤ {W} and the total value is maximal.",
    "Класичний інстанс: що покласти в рюкзак на {W}?":
        "The classic instance: what goes into a knapsack of capacity {W}?",
    "Малий інстанс: рюкзак на {W} — таблиця ДП поміститься на екран":
        "The small instance: capacity {W} — the DP table fits on screen",

    # --- examples/01_brute_force -------------------------------------------------
    "Повний перебір — інстанс «{label}»": "Brute force — the “{label}” instance",
    "Рекурсивна версія (з конспекту):": "Recursive version (from the lecture notes):",
    "Максимальна вартість:": "Maximum value:",
    "Обрані предмети (індекси):": "Chosen items (indices):",
    "Тобто набір {combo}: вага {w}, цінність {v}.":
        "That is, the set {combo}: weight {w}, value {v}.",
    "Зростання кількості підмножин 2^n:": "Growth of the number of subsets 2^n:",
    "  n = {n:>2}  →  2^{n} = {count} підмножин":
        "  n = {n:>2}  →  2^{n} = {count} subsets",
    "Більший інстанс — «{label}» (n = {n}, W = {W})":
        "A bigger instance — “{label}” (n = {n}, W = {W})",
    "Повний перебір мусить оглянути 2^{n} = {subsets} підмножин;":
        "Brute force must inspect 2^{n} = {subsets} subsets;",
    "ДП заповнює таблицю (n+1)×(W+1) = {rows}×{cols} = {cells} клітинок.":
        "DP fills a table of (n+1)×(W+1) = {rows}×{cols} = {cells} cells.",
    "Однакова відповідь: перебір = {bf}, ДП = {dp}  →  збіг: {ok}":
        "Same answer: brute force = {bf}, DP = {dp}  →  match: {ok}",
    "Час на цій машині: перебір {bf:.2f} с проти ДП {dp:.4f} с (×{ratio:.0f})":
        "Time on this machine: brute force {bf:.2f} s vs DP {dp:.4f} s (×{ratio:.0f})",

    # --- examples/02_dp_small -----------------------------------------------------
    "Створили таблицю: {rows} рядків × {cols} стовпців, рядок i=0 — нулі.":
        "Created the table: {rows} rows × {cols} columns; row i=0 is all zeros.",
    "Старт: рядок i=0 — без предметів цінність 0":
        "Start: row i=0 — with no items the value is 0",
    "стовпець w=0 теж завжди 0: без місця нічого не покладеш":
        "column w=0 is always 0 too: with no space nothing fits",
    "Після рядка i={i}: дозволені предмети {first}…{name}":
        "After row i={i}: items {first}…{name} allowed",
    "ВІДПОВІДЬ = K[{n}][{W}] = {v}": "ANSWER = K[{n}][{W}] = {v}",
    "Таблиця заповнена: відповідь у правому нижньому куті":
        "The table is filled: the answer sits in the bottom-right corner",
    "червона рамка — клітинка з відповіддю K[n][W]":
        "red frame — the answer cell K[n][W]",
    "i={i}, w={w}: K[{i}][{w}]={v} ≠ K[{i1}][{w}]={a} → {name} УЗЯТО, w ← {wa}":
        "i={i}, w={w}: K[{i}][{w}]={v} ≠ K[{i1}][{w}]={a} → {name} TAKEN, w ← {wa}",
    "i={i}, w={w}: K[{i}][{w}]={v} = K[{i1}][{w}]={a} → {name} не брали":
        "i={i}, w={w}: K[{i}][{w}]={v} = K[{i1}][{w}]={a} → {name} not taken",
    "Зворотний хід: жовтий шлях збирає відповідь {v}":
        "Backward pass: the yellow path assembles the answer {v}",
    "зелена стрілка = предмет узято (стрибок ліворуч на його вагу), сіра = ні (рух прямо вгору)":
        "green arrow = item taken (jump left by its weight), gray = not taken (straight up)",

    # --- examples/03_dp_classic ----------------------------------------------------
    "Таблиця має {rows} рядки × {cols} стовпець (w = 0…{W}); показуємо кратні 10:":
        "The table has {rows} rows × {cols} columns (w = 0…{W}); showing multiples of 10:",
    "Таблиця K для W = 50 (зведено до стовпців, кратних 10)":
        "Table K for W = 50 (condensed to columns that are multiples of 10)",
    "між показаними стовпцями значення не змінюються: всі ваги кратні 10":
        "values do not change between the shown columns: all weights are multiples of 10",
    "Зворотний хід по зведеній таблиці: {v} = 120 + 100":
        "Backward pass over the condensed table: {v} = 120 + 100",
    "шлях зупиняється на w = 50 → 20 → 0 — всі зупинки потрапляють у показані стовпці":
        "the path stops at w = 50 → 20 → 0 — every stop lands on a shown column",
    "Порівняння підходів на інстансі «{label}»":
        "Comparing the approaches on the “{label}” instance",
    "Повний перебір (рекурсія):   {v}": "Brute force (recursion):     {v}",
    "Повний перебір (itertools):  {v}, набір {combo}":
        "Brute force (itertools):     {v}, set {combo}",
    "Динамічне програмування:     {v}, набір {combo}":
        "Dynamic programming:         {v}, set {combo}",
    "Жадібний метод:              {v}  ← НЕ оптимум (втрачає {d})":
        "Greedy method:               {v}  ← NOT optimal (loses {d})",

    # --- examples/04_greedy_limitation ----------------------------------------------
    "Питома цінність (вартість / вага):": "Value density (value / weight):",
    "Хід жадібного (за спаданням ratio):": "Greedy run (by decreasing ratio):",
    "  {name} (вага {w}): взято   → вільно {b} → {a}, цінність {tot}":
        "  {name} (weight {w}): taken   → free {b} → {a}, value {tot}",
    "  {name} (вага {w}): пропуск (треба {w} > вільно {b})":
        "  {name} (weight {w}): skipped (needs {w} > free {b})",
    "Результат жадібного методу: {v}": "Greedy result: {v}",
    "Оптимум (ДП на тому самому інстансі): {v}": "Optimum (DP on the same instance): {v}",
    "Жадібний втратив {d}: дешевий «вигідний за грам» {first} заблокував пару {pair}.":
        "Greedy lost {d}: the cheap “best per unit” {first} blocked the pair {pair}.",
    "Жадібний": "Greedy",
    "Оптимум": "Optimum",
    "Жадібний ({g}) недозаповнює рюкзак; оптимум ({o}) — рівно {W}":
        "Greedy ({g}) underfills the knapsack; the optimum ({o}) packs exactly {W}",

    # --- examples/05_animations -------------------------------------------------------
    "Генерую GIF-анімації (та MP4, якщо доступний ffmpeg)…":
        "Generating GIF animations (and MP4 when ffmpeg is available)…",
    "  {name}: {n} кадрів": "  {name}: {n} frames",
    "Еволюція таблиці K: рядок за рядком (малий інстанс)":
        "Evolution of table K, row by row (the small instance)",

    # --- examples/06_code_walkthrough ----------------------------------------------
    "Генерую покрокові панелі «код ↔ таблиця»…":
        "Generating step-by-step code ↔ table panels…",
    "Код ↔ таблиця K: огляд по рядках (предмет за предметом)":
        "Code ↔ table K: overview by rows (item by item)",
    "  {name}: огляд, {n} кроків": "  {name}: overview, {n} steps",
    "Код ↔ таблиця K по клітинках (рядок i = {i})":
        "Code ↔ table K cell by cell (row i = {i})",
    "  {name}: по клітинках, {n} кадрів (рядок i = {i})":
        "  {name}: cell by cell, {n} frames (row i = {i})",
    "Код ↔ таблиця K: огляд по рядках (класичний інстанс, стовпці кратні 10)":
        "Code ↔ table K: overview by rows (the classic instance, columns at multiples of 10)",
}
