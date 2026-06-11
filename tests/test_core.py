"""Тести коректності алгоритмів задачі про рюкзак.

Покривають головні обіцянки README:

* повний перебір (обидві версії) і ДП дають **однакову відповідь** — на обох
  навчальних інстансах із конспекту та на серії випадкових інстансів (тут
  еталоном слугує сам перебір: для малих ``n`` він гарантовано точний);
* відновлення набору зворотним проходом повертає **допустимий** набір рівно
  тієї вартості, яку обіцяє таблиця;
* жадібний метод на класичному інстансі дає 160 — документований контрприклад
  (і ніколи не перевищує оптимум на випадкових інстансах);
* крайові випадки: порожній список предметів, нульова місткість, предмет
  важчий за рюкзак, предмет рівно в місткість, «усе влазить».

Запуск::

    pytest                       # якщо встановлено pytest
    python tests/test_core.py    # без pytest (вбудований раннер)
"""

from __future__ import annotations

import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from knapsack import (  # noqa: E402
    Item,
    brute_force_steps,
    greedy_steps,
    knapsack_brute_force,
    knapsack_dp,
    knapsack_dp_steps,
    knapsack_dp_table,
    knapsack_greedy,
    knapsack_recursive,
    reconstruct_items,
    reconstruct_steps,
)

# --- навчальні інстанси з конспекту (ті самі числа, що в examples/_items.py) ---
CLASSIC = {"weights": [10, 20, 30], "values": [60, 100, 120], "capacity": 50}
SMALL = {"weights": [1, 2, 3], "values": [6, 10, 12], "capacity": 4}


def _all_methods(weights, values, capacity):
    """Відповіді трьох точних реалізацій для одного інстансу."""
    n = len(weights)
    rec = knapsack_recursive(capacity, weights, values, n)
    bf, combo = knapsack_brute_force(capacity, weights, values)
    dp = knapsack_dp(capacity, weights, values, n)
    return rec, bf, combo, dp


def _check_reconstruction(weights, values, capacity):
    """Відновлений набір допустимий і дає рівно вартість із таблиці."""
    n = len(weights)
    K = knapsack_dp_table(capacity, weights, values, n)
    chosen = reconstruct_items(K, weights, capacity)
    total_w = sum(weights[i] for i in chosen)
    total_v = sum(values[i] for i in chosen)
    assert total_w <= capacity, f"набір {chosen} не влазить: {total_w} > {capacity}"
    assert total_v == K[n][capacity], (
        f"відновлений набір дає {total_v}, а таблиця обіцяє {K[n][capacity]}")
    assert chosen == sorted(set(chosen)), "індекси мають бути зростаючі й без повторів"
    return chosen


def test_classic_instance_all_methods_agree():
    """Класичний інстанс: 220, набір {П2, П3} (індекси 1 і 2)."""
    rec, bf, combo, dp = _all_methods(**CLASSIC)
    assert rec == bf == dp == 220
    assert combo == (1, 2)
    chosen = _check_reconstruction(**CLASSIC)
    assert chosen == [1, 2]


def test_small_instance_all_methods_agree():
    """Малий інстанс: 18, набір {П1, П3} (індекси 0 і 2)."""
    rec, bf, combo, dp = _all_methods(**SMALL)
    assert rec == bf == dp == 18
    assert combo == (0, 2)
    chosen = _check_reconstruction(**SMALL)
    assert chosen == [0, 2]


def test_greedy_counterexample_on_classic():
    """Жадібний на класичному інстансі дає 160 < 220 — контрприклад із README."""
    items = [Item(w, v) for w, v in zip(CLASSIC["weights"], CLASSIC["values"])]
    assert knapsack_greedy(items, CLASSIC["capacity"]) == 160

    total, steps = greedy_steps(
        list(zip(CLASSIC["weights"], CLASSIC["values"])), CLASSIC["capacity"])
    assert total == 160
    # порядок за ratio: П1 (6.0) взято, П2 (5.0) взято, П3 (4.0) пропущено
    assert [s["index"] for s in steps] == [0, 1, 2]
    assert [s["taken"] for s in steps] == [True, True, False]


def test_random_instances_brute_equals_dp():
    """Серія випадкових інстансів: перебір (еталон) і ДП збігаються завжди."""
    rng = random.Random(20260611)
    for _ in range(150):
        n = rng.randint(0, 9)
        weights = [rng.randint(1, 15) for _ in range(n)]
        values = [rng.randint(0, 30) for _ in range(n)]
        capacity = rng.randint(0, 40)

        rec = knapsack_recursive(capacity, weights, values, n)
        bf, _ = knapsack_brute_force(capacity, weights, values)
        dp = knapsack_dp(capacity, weights, values, n)
        assert rec == bf == dp, (
            f"розбіжність на n={n}, W={capacity}, wt={weights}, val={values}: "
            f"рекурсія={rec}, перебір={bf}, ДП={dp}")
        _check_reconstruction(weights, values, capacity)


def test_greedy_never_beats_optimum():
    """Жадібний — евристика: ніколи не перевищує точну відповідь."""
    rng = random.Random(42)
    for _ in range(100):
        n = rng.randint(1, 9)
        weights = [rng.randint(1, 15) for _ in range(n)]
        values = [rng.randint(1, 30) for _ in range(n)]
        capacity = rng.randint(1, 40)
        greedy = knapsack_greedy(
            [Item(w, v) for w, v in zip(weights, values)], capacity)
        optimum = knapsack_dp(capacity, weights, values, n)
        assert greedy <= optimum


def test_empty_items_and_zero_capacity():
    """Порожній рюкзак і порожній список предметів: відповідь 0, набір порожній."""
    # жодного предмета
    assert knapsack_recursive(10, [], [], 0) == 0
    assert knapsack_brute_force(10, [], []) == (0, ())
    assert knapsack_dp(10, [], [], 0) == 0
    K = knapsack_dp_table(10, [], [], 0)
    assert reconstruct_items(K, [], 10) == []
    # нульова місткість
    w, v = CLASSIC["weights"], CLASSIC["values"]
    assert knapsack_recursive(0, w, v, 3) == 0
    assert knapsack_brute_force(0, w, v)[0] == 0
    assert knapsack_dp(0, w, v, 3) == 0
    K = knapsack_dp_table(0, w, v, 3)
    assert reconstruct_items(K, w, 0) == []


def test_single_item_edge_cases():
    """Один предмет: важчий за місткість → 0; рівно в місткість → береться."""
    # важчий за рюкзак
    assert knapsack_dp(5, [7], [100], 1) == 0
    assert knapsack_recursive(5, [7], [100], 1) == 0
    K = knapsack_dp_table(5, [7], [100], 1)
    assert reconstruct_items(K, [7], 5) == []
    # рівно в місткість
    assert knapsack_dp(7, [7], [100], 1) == 100
    K = knapsack_dp_table(7, [7], [100], 1)
    assert reconstruct_items(K, [7], 7) == [0]


def test_all_items_fit():
    """Якщо все влазить — беремо все (сумарна вага ≤ W)."""
    weights, values, capacity = [2, 3, 4], [5, 6, 7], 20
    assert knapsack_dp(capacity, weights, values, 3) == 18
    K = knapsack_dp_table(capacity, weights, values, 3)
    assert reconstruct_items(K, weights, capacity) == [0, 1, 2]


def test_tie_breaking_prefers_skip():
    """Конвенція нічиїх: take == skip → «не брати» (узгоджено в усіх шарах).

    Журнал позначає таку клітинку kind="skip", зворотний прохід предмет не
    бере — і саме цю конвенцію наслідує зелений шлях дерева рекурсії.
    """
    wt, val, W = [1, 1], [5, 5], 1
    _, K, steps = knapsack_dp_steps(W, wt, val, 2)
    cell = next(s for s in steps if (s["i"], s["w"]) == (2, 1))
    assert cell["kind"] == "skip" and cell["take"] == cell["skip"] == 5
    assert reconstruct_items(K, wt, W) == [0]


def test_dp_steps_journal_consistency():
    """Журнал ДП: покриває всі клітинки, гілки відповідають числам у таблиці."""
    w, v, W = SMALL["weights"], SMALL["values"], SMALL["capacity"]
    n = len(w)
    best, K, steps = knapsack_dp_steps(W, w, v, n)
    assert best == K[n][W] == knapsack_dp(W, w, v, n)
    assert K == knapsack_dp_table(W, w, v, n)
    # рівно по одному запису на клітинку, в порядку заповнення
    assert [(s["i"], s["w"]) for s in steps] == [
        (i, ww) for i in range(n + 1) for ww in range(W + 1)]
    for s in steps:
        i, ww = s["i"], s["w"]
        assert s["value"] == K[i][ww]
        if i == 0 or ww == 0:
            assert s["kind"] == "base"
        elif w[i - 1] > ww:
            assert s["kind"] == "nofit" and s["take"] is None
            assert s["value"] == K[i - 1][ww]
        else:
            take = v[i - 1] + K[i - 1][ww - w[i - 1]]
            skip = K[i - 1][ww]
            assert s["take"] == take and s["skip"] == skip
            assert s["kind"] == ("take" if take > skip else "skip")
            assert s["value"] == max(take, skip)
    # конкретна клітинка з конспекту: K[3][3] — влазить, але вигідніше НЕ брати
    cell = next(s for s in steps if (s["i"], s["w"]) == (3, 3))
    assert cell["kind"] == "skip" and cell["take"] == 12 and cell["skip"] == 16


def test_reconstruct_steps_journal():
    """Журнал зворотного проходу узгоджений із reconstruct_items."""
    w, v, W = SMALL["weights"], SMALL["values"], SMALL["capacity"]
    n = len(w)
    K = knapsack_dp_table(W, w, v, n)
    chosen, steps = reconstruct_steps(K, w, W)
    assert chosen == reconstruct_items(K, w, W) == [0, 2]
    # один крок на рядок, знизу вгору; стовпець меншає лише на вагу взятого
    assert [s["i"] for s in steps] == [3, 2, 1]
    assert steps[0]["w"] == W
    for s in steps:
        assert s["taken"] == (s["value"] != s["above"])
        expected_after = s["w"] - (w[s["i"] - 1] if s["taken"] else 0)
        assert s["w_after"] == expected_after


def test_brute_force_steps_journal():
    """Журнал перебору: 2^n записів, лідер монотонно не спадає."""
    w, v, W = CLASSIC["weights"], CLASSIC["values"], CLASSIC["capacity"]
    best, combo, steps = brute_force_steps(W, w, v)
    assert (best, combo) == knapsack_brute_force(W, w, v)
    assert len(steps) == 2 ** len(w)
    assert steps[0]["combo"] == ()                  # перебір стартує з порожньої
    leader = 0
    for s in steps:
        assert s["fits"] == (s["weight"] <= W)
        assert s["best_value"] >= leader
        leader = s["best_value"]
        if s["improved"]:
            assert s["fits"] and s["best_combo"] == s["combo"]
    assert steps[-1]["best_value"] == best


def _run_without_pytest():
    """Мінімальний раннер на випадок, якщо pytest не встановлено."""
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    failures = 0
    for test in tests:
        try:
            test()
            print(f"PASS  {test.__name__}")
        except AssertionError as exc:
            failures += 1
            print(f"FAIL  {test.__name__}: {exc}")
    print(f"\n{len(tests) - failures}/{len(tests)} тестів пройдено")
    return failures


if __name__ == "__main__":
    sys.exit(1 if _run_without_pytest() else 0)
