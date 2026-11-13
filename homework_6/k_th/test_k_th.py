"""Тесты к задаче 3 "K-th".

Запуск из папки задачи: python -m unittest -v
Из корня репозитория: python -m unittest discover -v
"""

import inspect
import io
import itertools
import os
import random
import subprocess
import sys
import unittest
from collections import Counter
from contextlib import redirect_stdout
from unittest.mock import patch

try:
    from homework_6.k_th import main
except ModuleNotFoundError:
    import main

find_kth_largest = main.find_kth_largest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))


def oracle(nums, k):
    return sorted(nums, reverse=True)[k - 1]


def adversarial_input(n):
    """Массив, на котором при k = 1 средний элемент отрезка каждый раз - минимум отрезка.

    Значения назначаются по ходу работы алгоритма: очередной pivot получает
    следующее по возрастанию значение, а элементы без значения при разбиении
    считаются больше него. Разбиение моделируется той же partition3 на парах
    (0 - pivot, 1 - остальные; номер элемента), поэтому перестановки совпадают
    с настоящими. Порядок сравнений на готовом массиве будет тем же.
    """
    pairs = [(1, i) for i in range(n)]
    value = [0] * n
    low = 0
    for next_value in range(n):
        mid = (low + n - 1) // 2
        pivot_id = pairs[mid][1]
        value[pivot_id] = next_value
        pairs[mid] = (0, pivot_id)
        main.partition3(pairs, low, n - 1, (0, pivot_id))
        low += 1
    return value


class TestExamples(unittest.TestCase):
    def test_statement(self):
        self.assertEqual(find_kth_largest([3, 2, 1, 5, 6, 4], 2), 5)
        self.assertEqual(find_kth_largest([3, 2, 3, 1, 2, 4, 5, 5, 6], 4), 4)
        self.assertEqual(find_kth_largest([5, 5, 3, 1], 2), 5)

    def test_duplicates_are_separate_positions(self):
        nums = [3, 2, 3, 1, 2, 4, 5, 5, 6]
        self.assertEqual([find_kth_largest(nums, k) for k in range(1, 10)],
                         [6, 5, 5, 4, 3, 3, 2, 2, 1])

    def test_bounds_of_k(self):
        nums = [4, -1, 9, 0, 9, -5]
        self.assertEqual(find_kth_largest(nums, 1), 9)
        self.assertEqual(find_kth_largest(nums, len(nums)), -5)

    def test_small_cases(self):
        cases = [
            ([7], 1, 7),
            ([2, 2, 2, 2], 3, 2),
            ([9, 1, 9, 9, 1], 3, 9),
            ([9, 1, 9, 9, 1], 4, 1),
            ([-3, -1, -2], 1, -1),
            ([-3, -1, -2], 3, -3),
            ([0, -1, 0, 1], 2, 0),
            ([1, 2, 3, 4, 5], 2, 4),
            ([5, 4, 3, 2, 1], 4, 2),
            ([1.5, 2.5, -0.5], 2, 1.5),
        ]
        for nums, k, expected in cases:
            with self.subTest(nums=nums, k=k):
                self.assertEqual(find_kth_largest(nums, k), expected)

    def test_invalid_k(self):
        for nums, k in (([1, 2, 3], 0), ([1, 2, 3], -1), ([1, 2, 3], 4), ([], 1), ([], 0)):
            with self.subTest(nums=nums, k=k):
                with self.assertRaises(ValueError):
                    find_kth_largest(nums, k)

    def test_input_not_modified(self):
        nums = [3, 2, 3, 1, 2, 4, 5, 5, 6]
        original = list(nums)
        find_kth_largest(nums, 4)
        self.assertEqual(nums, original)


class TestAgainstOracle(unittest.TestCase):
    def test_all_small_arrays_all_k(self):
        # Все массивы длины 1..6 из значений 0..2 и все k: много повторов
        for n in range(1, 7):
            for nums in itertools.product(range(3), repeat=n):
                for k in range(1, n + 1):
                    self.assertEqual(find_kth_largest(list(nums), k), oracle(nums, k), (nums, k))

    def test_all_permutations(self):
        for n in range(1, 8):
            for nums in itertools.permutations(range(n)):
                for k in range(1, n + 1):
                    self.assertEqual(find_kth_largest(list(nums), k), n - k)

    def test_random_with_many_duplicates(self):
        rng = random.Random(2026)
        for _ in range(300):
            n = rng.randint(1, 80)
            nums = [rng.randint(-5, 5) for _ in range(n)]
            k = rng.randint(1, n)
            self.assertEqual(find_kth_largest(nums, k), oracle(nums, k))

    def test_big_inputs(self):
        rng = random.Random(1)
        n = 100_000
        inputs = {
            "random": [rng.randint(-10 ** 6, 10 ** 6) for _ in range(n)],
            "few values": [rng.randint(0, 3) for _ in range(n)],
            "sorted": list(range(n)),
            "reversed": list(range(n, 0, -1)),
            "equal": [5] * n,
        }
        for name, nums in inputs.items():
            desc = sorted(nums, reverse=True)
            for k in (1, n // 3, n // 2, n):
                with self.subTest(name=name, k=k):
                    log = []
                    self.assertEqual(find_kth_largest(nums, k, log=log), desc[k - 1])
                    # Нет квадратичной деградации: шагов порядка log n, а не n
                    self.assertLessEqual(len(log), 60)


class TestPartition3(unittest.TestCase):
    def test_example(self):
        arr = [3, 2, 3, 1, 2, 4, 5, 5, 6]
        self.assertEqual(main.partition3(arr, 0, 8, 2), (1, 2))
        self.assertEqual(arr, [1, 2, 2, 3, 4, 5, 5, 6, 3])

    def test_invariant_random(self):
        rng = random.Random(7)
        for _ in range(500):
            n = rng.randint(1, 15)
            arr = [rng.randint(0, 4) for _ in range(n)]
            low = rng.randint(0, n - 1)
            high = rng.randint(low, n - 1)
            pivot = arr[rng.randint(low, high)]
            before = list(arr)
            lt, gt = main.partition3(arr, low, high, pivot)
            self.assertTrue(low <= lt <= gt <= high)
            self.assertTrue(all(x < pivot for x in arr[low:lt]))
            self.assertTrue(all(x == pivot for x in arr[lt:gt + 1]))
            self.assertTrue(all(x > pivot for x in arr[gt + 1:high + 1]))
            self.assertEqual(arr[:low], before[:low])
            self.assertEqual(arr[high + 1:], before[high + 1:])
            self.assertEqual(Counter(arr[low:high + 1]), Counter(before[low:high + 1]))


class TestSteps(unittest.TestCase):
    def test_log_invariants(self):
        rng = random.Random(3)
        for _ in range(300):
            n = rng.randint(1, 60)
            nums = [rng.randint(0, 9) for _ in range(n)]
            k = rng.randint(1, n)
            target = n - k
            expected = sorted(nums)
            log = []
            answer = find_kth_largest(nums, k, log=log)
            prev_size = n + 1
            for low, high, pivot, lt, gt, arr in log:
                # Отрезок содержит target и строго уменьшается
                self.assertTrue(low <= target <= high)
                self.assertLess(high - low + 1, prev_size)
                prev_size = high - low + 1
                # Отброшенные части уже на своих местах по порядку
                self.assertTrue(all(x <= pivot for x in arr[:lt]))
                self.assertTrue(all(x >= pivot for x in arr[gt + 1:]))
                self.assertEqual(Counter(arr), Counter(nums))
                self.assertEqual(sorted(arr[low:high + 1]), expected[low:high + 1])
            self.assertTrue(log[-1][3] <= target <= log[-1][4])
            self.assertEqual(answer, log[-1][2])

    def test_example_steps(self):
        log = []
        find_kth_largest([3, 2, 3, 1, 2, 4, 5, 5, 6], 4, log=log)
        self.assertEqual([entry[:5] for entry in log],
                         [(0, 8, 2, 1, 2), (3, 8, 5, 6, 7), (3, 5, 4, 5, 5)])
        self.assertEqual(log[-1][5], [1, 2, 2, 3, 3, 4, 5, 5, 6])

    def test_all_equal_one_step(self):
        log = []
        self.assertEqual(find_kth_largest([4] * 1000, 600, log=log), 4)
        self.assertEqual(len(log), 1)

    def test_sorted_and_reversed_inputs(self):
        # Первый pivot отсортированного массива - его медиана, дальше порядок
        # внутри отрезка уже изменен разбиением. Шагов все равно мало для любого k
        n = 1024
        for nums in (list(range(n)), list(range(n, 0, -1))):
            for k in range(1, n + 1):
                log = []
                find_kth_largest(nums, k, log=log)
                self.assertLessEqual(log[1][1] - log[1][0] + 1 if len(log) > 1 else 0, n // 2)
                self.assertLessEqual(len(log), 2 * 10)

    def test_worst_case_exists(self):
        # Худший случай Θ(n²) достижим: на специально построенном входе отрезок
        # каждый раз уменьшается только на один элемент
        for n in (8, 500):
            nums = adversarial_input(n)
            self.assertEqual(sorted(nums), list(range(n)))
            log = []
            self.assertEqual(find_kth_largest(nums, 1, log=log), n - 1)
            self.assertEqual(len(log), n)
            self.assertEqual([high - low + 1 for low, high, *_ in log], list(range(n, 0, -1)))


class TestModule(unittest.TestCase):
    def test_no_sorting_and_no_heaps(self):
        source = inspect.getsource(main)
        for forbidden in ("sorted(", ".sort(", "heapq", "import"):
            self.assertNotIn(forbidden, source)
        with patch("builtins.sorted", side_effect=AssertionError("sorted вызван")):
            self.assertEqual(find_kth_largest([3, 2, 1, 5, 6, 4], 2), 5)

    def test_import_prints_nothing(self):
        out = subprocess.run([sys.executable, "-c", "import homework_6.k_th.main"],
                             cwd=ROOT, capture_output=True, text=True, check=True)
        self.assertEqual(out.stdout, "")

    def test_readme_matches_program(self):
        with open(os.path.join(HERE, "README.md"), encoding="utf-8") as f:
            readme = f.read()
        for nums, k in main.EXAMPLES:
            log = []
            find_kth_largest(nums, k, log=log)
            self.assertIn(main.format_log(log, len(nums) - k), readme)

    def test_main_output(self):
        buf = io.StringIO()
        with redirect_stdout(buf):
            main.main()
        self.assertIn("find_kth_largest([3, 2, 3, 1, 2, 4, 5, 5, 6], k=4) = 4, target = 5",
                      buf.getvalue())


if __name__ == "__main__":
    unittest.main()
