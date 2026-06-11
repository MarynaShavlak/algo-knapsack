"""Реалізації задачі про рюкзак 0/1 (повний перебір, жадібний, динамічне програмування).

Модуль містить три підходи «з конспекту» плюс навчально-інструментовані версії:

* :func:`knapsack_recursive` — повний перебір **рекурсією**: на кожному предметі
  гілка «взяти / не брати». Саме цей код README розбирає рядок за рядком.
* :func:`knapsack_brute_force` — повний перебір **явним переліком** усіх
  :math:`2^n` підмножин через ``itertools.combinations`` (повертає й сам набір).
* :func:`knapsack_greedy` (+ клас :class:`Item`) — жадібний метод за питомою
  цінністю ``value / weight``. Для задачі 0/1 **не гарантує оптимум** — це
  навчальний контрприклад, а не робочий розв'язок.
* :func:`knapsack_dp` — динамічне програмування: таблиця ``K[i][w]``.
* :func:`reconstruct_items` — відновлення обраного набору **зворотним проходом**
  по готовій таблиці (аналог відновлення шляху в алгоритмах на графах).

Інструментовані версії для візуалізацій (повертають журнал кроків):

* :func:`brute_force_steps` — журнал перебору: по одному запису на підмножину;
* :func:`greedy_steps` — журнал жадібного: по одному запису на предмет;
* :func:`knapsack_dp_steps` — журнал ДП: по одному запису на клітинку таблиці;
* :func:`reconstruct_steps` — журнал зворотного проходу: по запису на рядок.

У конспекті всі три підходи називаються однаково — ``knapSack``. У пакеті вони
мусять співіснувати, тож функціям дано різні імена; **тіла збережено дослівно**
(коментарі включно), щоб код у README збігався з кодом тут.

``core`` не залежить від графічних бібліотек — це чистий алгоритм, який можна
імпортувати будь-де.
"""

from __future__ import annotations

from itertools import combinations
from typing import Dict, List, Sequence, Tuple

#: Один запис журналу інструментованих версій (див. докстрінги функцій).
Step = Dict[str, object]
#: Таблиця ДП: ``(n+1) × (W+1)`` цілих значень.
Table = List[List[int]]


# ---------------------------------------------------------------------------
# Повний перебір — рекурсія «взяти / не брати» (код із конспекту)
# ---------------------------------------------------------------------------
def knapsack_recursive(W: int, wt: Sequence[int], val: Sequence[int], n: int) -> int:
    """Повний перебір рекурсією: максимальна вартість для перших ``n`` предметів.

    Код навмисно збережено у вигляді «з конспекту» (у конспекті функція
    називається ``knapSack``) — саме він розібраний у README рядок за рядком.
    На кожному предметі два рекурсивні виклики — «взяти» та «не брати», тому
    перевіряються всі :math:`2^n` комбінацій.

    :param W: поточна вільна місткість рюкзака.
    :param wt: список ваг предметів.
    :param val: список вартостей предметів.
    :param n: скільки предметів ще розглядаємо (рекурсія зменшує до 0).

    Складність: :math:`O(2^n)` часу та :math:`O(n)` пам'яті (глибина рекурсії).
    """
    # Базовий випадок
    if n == 0 or W == 0:
        return 0

    # Якщо вага n-го предмета більше, ніж місткість рюкзака, то цей предмет не можна включити у рюкзак
    if wt[n - 1] > W:
        return knapsack_recursive(W, wt, val, n - 1)

    # повертаємо максимум із двох випадків:
    # (1) n-ий предмет включено
    # (2) не включено
    else:
        return max(
            val[n - 1] + knapsack_recursive(W - wt[n - 1], wt, val, n - 1),
            knapsack_recursive(W, wt, val, n - 1),
        )


# ---------------------------------------------------------------------------
# Повний перебір — явний перелік підмножин (код із конспекту)
# ---------------------------------------------------------------------------
def knapsack_brute_force(
    W: int, wt: Sequence[int], val: Sequence[int]
) -> Tuple[int, Tuple[int, ...]]:
    """Повний перебір явним переліком усіх :math:`2^n` підмножин предметів.

    Та сама ідея, що й у :func:`knapsack_recursive`, але без рекурсії: підмножини
    генерує ``itertools.combinations``. Бонус проти рекурсивної версії — повертає
    не лише вартість, а й **сам набір** (індекси обраних предметів).

    :returns: кортеж ``(best_value, best_combo)``, де ``best_combo`` — кортеж
        індексів обраних предметів (порожній, якщо нічого не влазить).

    Складність: :math:`O(n \\cdot 2^n)` часу (кожну підмножину підсумовуємо).
    """
    n = len(val)
    best_value = 0
    best_combo: Tuple[int, ...] = ()

    # перебираємо всі можливі підмножини предметів (2^n штук)
    for r in range(n + 1):
        for combo in combinations(range(n), r):
            total_weight = sum(wt[i] for i in combo)
            total_value = sum(val[i] for i in combo)
            # враховуємо лише ті, що влазять у рюкзак
            if total_weight <= W and total_value > best_value:
                best_value = total_value
                best_combo = combo

    return best_value, best_combo


def brute_force_steps(
    W: int, wt: Sequence[int], val: Sequence[int]
) -> Tuple[int, Tuple[int, ...], List[Step]]:
    """Інструментований повний перебір: журнал по одному запису на підмножину.

    Повторює :func:`knapsack_brute_force` **дія в дію** (той самий порядок
    перебору, та сама умова оновлення лідера), але після кожної підмножини кладе
    у журнал знімок. Саме з цих знімків зібрані таблиця перебору та анімація.

    :returns: кортеж ``(best_value, best_combo, steps)``; кожен крок — словник:

        * ``combo`` — підмножина (кортеж індексів предметів);
        * ``weight`` / ``value`` — її сумарна вага та вартість;
        * ``fits`` — чи влазить у рюкзак (``weight <= W``);
        * ``improved`` — чи стала ця підмножина новим лідером;
        * ``best_value`` / ``best_combo`` — лідер ПІСЛЯ цього кроку.
    """
    n = len(val)
    best_value = 0
    best_combo: Tuple[int, ...] = ()
    steps: List[Step] = []

    for r in range(n + 1):
        for combo in combinations(range(n), r):
            total_weight = sum(wt[i] for i in combo)
            total_value = sum(val[i] for i in combo)
            fits = total_weight <= W
            improved = fits and total_value > best_value
            if improved:
                best_value = total_value
                best_combo = combo
            steps.append({
                "combo": combo,
                "weight": total_weight,
                "value": total_value,
                "fits": fits,
                "improved": improved,
                "best_value": best_value,
                "best_combo": best_combo,
            })

    return best_value, best_combo, steps


# ---------------------------------------------------------------------------
# Жадібний метод (код із конспекту) — навчальний контрприклад для задачі 0/1
# ---------------------------------------------------------------------------
class Item:
    """Один предмет для жадібного методу: вага, вартість і питома цінність."""

    def __init__(self, weight, value):
        self.weight = weight
        self.value = value
        self.ratio = value / weight


def knapsack_greedy(items: "list[Item]", capacity: int) -> int:
    """Жадібний метод: сортуємо за ``ratio`` і беремо, поки вміщається.

    Код навмисно збережено у вигляді «з конспекту» (у конспекті функція
    називається ``knapSack``). Для задачі **0/1 не гарантує оптимум** — на
    навчальному інстансі дає 160 замість 220 (контрприклад у README); оптимальний
    він лише для *дробової* задачі. Увага: сортує переданий список **на місці**.

    Складність: :math:`O(n \\log n)` часу (сортування).
    """
    items.sort(key=lambda x: x.ratio, reverse=True)
    total_value = 0
    for item in items:
        if capacity >= item.weight:
            capacity -= item.weight
            total_value += item.value
    return total_value


def greedy_steps(
    items: Sequence[Tuple[int, int]], capacity: int
) -> Tuple[int, List[Step]]:
    """Інструментований жадібний метод: журнал по одному запису на предмет.

    Повторює :func:`knapsack_greedy` дія в дію, але працює з кортежами
    ``(вага, вартість)`` (вхід не мутує) і пам'ятає вихідні індекси предметів.

    :returns: кортеж ``(total_value, steps)``; кожен крок — словник:

        * ``index`` — вихідний індекс предмета (до сортування);
        * ``weight`` / ``value`` / ``ratio`` — параметри предмета;
        * ``taken`` — чи взято предмет;
        * ``free_before`` / ``free_after`` — вільне місце до та після кроку;
        * ``total_after`` — накопичена вартість після кроку.
    """
    order = sorted(range(len(items)), key=lambda i: items[i][1] / items[i][0], reverse=True)
    steps: List[Step] = []
    total_value = 0
    free = capacity
    for i in order:
        weight, value = items[i]
        taken = free >= weight
        free_before = free
        if taken:
            free -= weight
            total_value += value
        steps.append({
            "index": i,
            "weight": weight,
            "value": value,
            "ratio": value / weight,
            "taken": taken,
            "free_before": free_before,
            "free_after": free,
            "total_after": total_value,
        })
    return total_value, steps


# ---------------------------------------------------------------------------
# Динамічне програмування — таблиця K[i][w] (код із конспекту)
# ---------------------------------------------------------------------------
def knapsack_dp(W: int, wt: Sequence[int], val: Sequence[int], n: int) -> int:
    """Динамічне програмування: максимальна вартість через таблицю ``K[i][w]``.

    Код навмисно збережено у вигляді «з конспекту» (у конспекті функція
    називається ``knapSack``) — саме він розібраний у README рядок за рядком.
    ``K[i][w]`` — найбільша вартість для перших ``i`` предметів і місткості ``w``;
    відповідь — у правому нижньому куті ``K[n][W]``.

    Складність: :math:`O(n \\cdot W)` часу та пам'яті (псевдополіноміальна —
    залежить від *числа* ``W``, а не лише від кількості предметів).
    """
    # створюємо таблицю K для зберігання оптимальних значень підзадач
    K = [[0 for w in range(W + 1)] for i in range(n + 1)]

    # будуємо таблицю K знизу вгору
    for i in range(n + 1):
        for w in range(W + 1):
            if i == 0 or w == 0:
                K[i][w] = 0
            elif wt[i - 1] <= w:
                K[i][w] = max(val[i - 1] + K[i - 1][w - wt[i - 1]], K[i - 1][w])
            else:
                K[i][w] = K[i - 1][w]

    return K[n][W]


def knapsack_dp_table(W: int, wt: Sequence[int], val: Sequence[int], n: int) -> Table:
    """Та сама побудова, що й :func:`knapsack_dp`, але повертає **всю таблицю**.

    Повна таблиця потрібна для відновлення набору (:func:`reconstruct_items`)
    та для всіх візуалізацій. ``knapsack_dp(...) == knapsack_dp_table(...)[n][W]``.
    """
    K = [[0 for w in range(W + 1)] for i in range(n + 1)]
    for i in range(n + 1):
        for w in range(W + 1):
            if i == 0 or w == 0:
                K[i][w] = 0
            elif wt[i - 1] <= w:
                K[i][w] = max(val[i - 1] + K[i - 1][w - wt[i - 1]], K[i - 1][w])
            else:
                K[i][w] = K[i - 1][w]
    return K


def knapsack_dp_steps(
    W: int, wt: Sequence[int], val: Sequence[int], n: int
) -> Tuple[int, Table, List[Step]]:
    """Інструментоване ДП: журнал по одному запису на клітинку таблиці.

    Повторює :func:`knapsack_dp` дія в дію (той самий порядок заповнення), але
    для кожної клітинки запам'ятовує, **яка гілка спрацювала і з яких чисел
    зібрався максимум**. Таблиця ДП ніколи не переписує вже заповнені клітинки,
    тож знімків-копій не потрібно: стан на будь-який момент відновлюється з
    готової таблиці ``K`` та позиції поточної клітинки.

    :returns: кортеж ``(best_value, K, steps)``; кожен крок — словник:

        * ``i`` / ``w`` — координати клітинки (рядок = предмет, стовпець = місткість);
        * ``kind`` — гілка, що спрацювала:

          - ``"base"`` — базовий випадок (``i == 0`` або ``w == 0``) → 0;
          - ``"nofit"`` — предмет не вміщається (``wt[i-1] > w``) → значення зверху;
          - ``"take"`` — вміщається, «взяти» перемогло (``take > skip``);
          - ``"skip"`` — вміщається, «не брати» перемогло (``take <= skip``);

        * ``take`` — вартість варіанта «взяти» (``None``, якщо не вміщається);
        * ``skip`` — вартість варіанта «не брати» = значення зверху (``None`` у базі);
        * ``value`` — підсумкове значення клітинки ``K[i][w]``.
    """
    K: Table = [[0 for w in range(W + 1)] for i in range(n + 1)]
    steps: List[Step] = []

    for i in range(n + 1):
        for w in range(W + 1):
            if i == 0 or w == 0:
                K[i][w] = 0
                steps.append({"i": i, "w": w, "kind": "base",
                              "take": None, "skip": None, "value": 0})
            elif wt[i - 1] <= w:
                take = val[i - 1] + K[i - 1][w - wt[i - 1]]
                skip = K[i - 1][w]
                K[i][w] = max(take, skip)
                steps.append({"i": i, "w": w,
                              "kind": "take" if take > skip else "skip",
                              "take": take, "skip": skip, "value": K[i][w]})
            else:
                K[i][w] = K[i - 1][w]
                steps.append({"i": i, "w": w, "kind": "nofit",
                              "take": None, "skip": K[i - 1][w], "value": K[i][w]})

    return K[n][W], K, steps


# ---------------------------------------------------------------------------
# Відновлення набору зворотним проходом по таблиці
# ---------------------------------------------------------------------------
def reconstruct_items(K: Table, wt: Sequence[int], W: int) -> List[int]:
    """Відновлює **набір обраних предметів** зворотним проходом по таблиці ``K``.

    Таблиця каже лише, *скільки* коштує оптимум (``K[n][W]``), а не *з чого* він
    складається. Відновлення йде з правого нижнього кута вгору (код із конспекту):
    якщо ``K[i][w] != K[i-1][w]``, значення в рядку ``i`` могло взятися лише з
    гілки «взяти» — отже, предмет ``i`` у наборі, і ми «звільняємо» його вагу.

    :param K: повна таблиця ДП (із :func:`knapsack_dp_table` або
        :func:`knapsack_dp_steps`).
    :returns: список **0-базових індексів** обраних предметів у порядку зростання.

    Складність: :math:`O(n)` — по одному погляду на рядок.
    """
    n = len(K) - 1
    # Зворотний хід: відновлюємо набір предметів
    w = W
    chosen: List[int] = []
    for i in range(n, 0, -1):
        if K[i][w] != K[i - 1][w]:        # значення змінилось -> предмет i був узятий
            chosen.append(i - 1)
            w -= wt[i - 1]                # звільняємо вагу, яку зайняв предмет
    chosen.reverse()
    return chosen


def reconstruct_steps(K: Table, wt: Sequence[int], W: int) -> Tuple[List[int], List[Step]]:
    """Інструментоване відновлення: журнал по одному запису на рядок таблиці.

    Повторює :func:`reconstruct_items` дія в дію, фіксуючи кожне порівняння
    «клітинка проти клітинки зверху» — для покрокової візуалізації та анімації.

    :returns: кортеж ``(chosen, steps)``; кожен крок — словник:

        * ``i`` / ``w`` — поточні рядок і стовпець (клітинка ``K[i][w]``);
        * ``taken`` — чи взято предмет ``i`` (``K[i][w] != K[i-1][w]``);
        * ``value`` / ``above`` — значення ``K[i][w]`` та ``K[i-1][w]``;
        * ``w_after`` — стовпець після кроку (зменшується на вагу взятого).
    """
    n = len(K) - 1
    w = W
    chosen: List[int] = []
    steps: List[Step] = []
    for i in range(n, 0, -1):
        taken = K[i][w] != K[i - 1][w]
        w_after = w - wt[i - 1] if taken else w
        steps.append({"i": i, "w": w, "taken": taken,
                      "value": K[i][w], "above": K[i - 1][w], "w_after": w_after})
        if taken:
            chosen.append(i - 1)
        w = w_after
    chosen.reverse()
    return chosen, steps
