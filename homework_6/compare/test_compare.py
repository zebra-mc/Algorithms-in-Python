"""Тесты к задаче 1 "Compare".

Запуск из папки задачи: python -m unittest -v
Из корня репозитория: python -m unittest discover -v
"""

import io
import os
import random
import subprocess
import sys
import unittest
from collections import Counter
from contextlib import redirect_stdout
from unittest.mock import patch

# Из корня модуль берется по полному имени: у всех задач файл называется main.py
try:
    from homework_6.compare import main
except ModuleNotFoundError:
    import main

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))


class SortContract:
    """Общие тесты для любой сортировки; подкласс задает sort = staticmethod(...).

    Класс не наследует TestCase, поэтому сам по себе не запускается. Его
    подключают и тесты задачи Iterative.
    """

    sort = None
    # Худший случай рекурсивного quick_sort - рекурсия глубины порядка n, поэтому
    # подкласс может уменьшить размер вырожденных входов
    big_degenerate_n = 5000

    def check(self, nums):
        original = list(nums)
        result = self.sort(nums)
        self.assertEqual(nums, original, "входной массив изменился")
        self.assertIsNot(result, nums)
        self.assertTrue(all(result[i] <= result[i + 1] for i in range(len(result) - 1)),
                        f"не отсортировано: {result}")
        self.assertEqual(Counter(result), Counter(original))
        self.assertEqual(result, sorted(original))
        return result

    def test_small_cases(self):
        cases = [
            [], [1], [1, 2], [2, 1], [3, 3],
            [1, 2, 3, 4, 5], [5, 4, 3, 2, 1],
            [7] * 10,
            [2, 1, 2, 1, 2, 1, 1, 2],
            [-3, -1, -7, -2],
            [0, 0, 0, -1, 1, 0],
            [5, -2, 0, 3, -8, 3, -2],
            [100, 1, 99, 2, 98, 3, 97, 4],
            [3, 1, 2], [4, 1, 3, 2],
            [5, 2, 7, 2, 9, 1, 2, 6],
            [9, -3, 5, 2, 6, 8, -6, 1, 3],
        ]
        for nums in cases:
            with self.subTest(nums=nums):
                self.check(nums)

    def test_lengths_near_powers_of_two(self):
        rng = random.Random(7)
        for n in (7, 8, 9, 15, 16, 17, 31, 32, 33):
            for nums in ([rng.randint(-5, 5) for _ in range(n)], list(range(n, 0, -1))):
                with self.subTest(n=n, nums=nums):
                    self.check(nums)

    def test_all_small_arrays_exhaustively(self):
        # Все массивы длины до 6 из значений 0..2: и повторы, и все порядки
        for n in range(7):
            for code in range(3 ** n):
                nums = [(code // 3 ** i) % 3 for i in range(n)]
                self.check(nums)

    def test_random(self):
        rng = random.Random(2026)
        for _ in range(200):
            n = rng.randint(0, 60)
            nums = [rng.randint(-20, 20) for _ in range(n)]
            self.check(nums)

    def test_floats_and_large_values(self):
        self.check([2.5, -1.0, 2.5, 0.0, 10 ** 18, -10 ** 18])

    def test_big_random(self):
        rng = random.Random(1)
        self.check([rng.randint(-10 ** 6, 10 ** 6) for _ in range(20_000)])

    def test_big_degenerate(self):
        # Входы, плохие для quicksort с pivot = последний элемент и сравнением <
        n = self.big_degenerate_n
        rng = random.Random(4)
        self.check(list(range(n)))
        self.check(list(range(n, 0, -1)))
        self.check([0] * n)
        self.check([rng.randint(0, 3) for _ in range(n)])

    def test_repeated_calls_independent(self):
        nums = [3, 1, 2, 3, 0]
        first = self.sort(nums)
        first.append(100)
        self.assertEqual(self.sort(nums), [0, 1, 2, 3, 3])


class TestMergeSort(SortContract, unittest.TestCase):
    sort = staticmethod(main.merge_sort)

    def test_stable(self):
        items = [Item(k, tag) for tag, k in enumerate([2, 1, 2, 0, 1, 2, 0])]
        result = main.merge_sort(items)
        self.assertEqual([(x.key, x.tag) for x in result],
                         [(0, 3), (0, 6), (1, 1), (1, 4), (2, 0), (2, 2), (2, 5)])


class TestQuickSort(SortContract, unittest.TestCase):
    sort = staticmethod(main.quick_sort)
    # Глубина рекурсии на таких входах до n; 500 + кадры unittest < 1000
    big_degenerate_n = 500

    def test_recursion_limit_on_sorted_input(self):
        # Ограничение реализации, а не ошибка: на отсортированном массиве длиннее
        # предела рекурсии двухсторонняя рекурсия не помещается в стек
        n = sys.getrecursionlimit() + 100
        with self.assertRaises(RecursionError):
            main.quick_sort(list(range(n)))


class Item:
    """Элемент, который сравнивается только по key; tag показывает исходный порядок."""

    def __init__(self, key, tag):
        self.key, self.tag = key, tag

    def __lt__(self, other):
        return self.key < other.key

    def __le__(self, other):
        return self.key <= other.key


class TestMerge(unittest.TestCase):
    def test_merge(self):
        self.assertEqual(main.merge([], []), [])
        self.assertEqual(main.merge([1, 4], []), [1, 4])
        self.assertEqual(main.merge([], [2]), [2])
        self.assertEqual(main.merge([1, 3, 5], [2, 3, 4, 10]), [1, 2, 3, 3, 4, 5, 10])

    def test_merge_random(self):
        rng = random.Random(3)
        for _ in range(300):
            left = sorted(rng.randint(0, 9) for _ in range(rng.randint(0, 10)))
            right = sorted(rng.randint(0, 9) for _ in range(rng.randint(0, 10)))
            self.assertEqual(main.merge(left, right), sorted(left + right))

    def test_merge_takes_left_first_on_ties(self):
        left = [Item(1, "L1"), Item(2, "L2")]
        right = [Item(1, "R1"), Item(2, "R2")]
        self.assertEqual([x.tag for x in main.merge(left, right)], ["L1", "R1", "L2", "R2"])


class TestPartition(unittest.TestCase):
    def test_example_from_lecture(self):
        # Слайд 18: pivot 3 - последний элемент
        arr = [9, -3, 5, 2, 6, 8, -6, 1, 3]
        p = main.partition(arr, 0, len(arr) - 1)
        self.assertEqual(p, 4)
        self.assertEqual(arr, [-3, 2, -6, 1, 3, 8, 5, 9, 6])

    def test_invariant_random(self):
        rng = random.Random(11)
        for _ in range(500):
            n = rng.randint(1, 15)
            arr = [rng.randint(0, 5) for _ in range(n)]
            low = rng.randint(0, n - 1)
            high = rng.randint(low, n - 1)
            before = list(arr)
            pivot = arr[high]
            p = main.partition(arr, low, high)
            self.assertTrue(low <= p <= high)
            self.assertEqual(arr[p], pivot)
            self.assertTrue(all(x < pivot for x in arr[low:p]))
            self.assertTrue(all(x >= pivot for x in arr[p + 1:high + 1]))
            self.assertEqual(arr[:low], before[:low])
            self.assertEqual(arr[high + 1:], before[high + 1:])
            self.assertEqual(Counter(arr[low:high + 1]), Counter(before[low:high + 1]))


class TestTimer(unittest.TestCase):
    def test_keeps_result_and_metadata(self):
        def add(a, b=0):
            """Сумма."""
            return a + b

        timed = main.timer(add)
        self.assertEqual(timed.__name__, "add")
        self.assertEqual(timed.__doc__, "Сумма.")
        self.assertIs(timed.__wrapped__, add)
        self.assertIsNone(timed.last_time)
        self.assertEqual(timed(2, b=3), 5)
        self.assertEqual(timed(*[1], **{"b": 10}), 11)
        self.assertIsInstance(timed.last_time, float)
        self.assertGreaterEqual(timed.last_time, 0)

    def test_sorts_are_decorated_and_result_unchanged(self):
        data = [5, 2, 7, 2, 9, 1, 2, 6]
        for sort in (main.merge_sort, main.quick_sort):
            with self.subTest(sort=sort.__name__):
                self.assertEqual(sort(data), sort.__wrapped__(data))
                self.assertEqual(sort(data), sorted(data))
                self.assertIsNotNone(sort.last_time)

    def test_measures_each_call(self):
        timed = main.timer(lambda x: x * 2)
        # Подменяем часы: каждый вызов читает их дважды - в начале и в конце
        with patch.object(main.time, "perf_counter", side_effect=[1.0, 3.5, 10.0, 10.25]):
            self.assertEqual(timed(4), 8)
            self.assertEqual(timed.last_time, 2.5)
            self.assertEqual(timed(5), 10)
            self.assertEqual(timed.last_time, 0.25)

    def test_exception(self):
        @main.timer
        def fail():
            raise KeyError("x")

        with patch.object(main.time, "perf_counter", side_effect=[2.0, 2.75]):
            with self.assertRaises(KeyError):
                fail()
        self.assertEqual(fail.last_time, 0.75)

    def test_recursive_function_reports_outer_call(self):
        @main.timer
        def depth(n):
            return 0 if n == 0 else 1 + depth(n - 1)

        # Вход depth(1), вход depth(0), выход depth(0), выход depth(1).
        # finally внешнего вызова выполняется последним, поэтому last_time -
        # длительность всего вычисления
        with patch.object(main.time, "perf_counter", side_effect=[0.0, 1.0, 2.0, 10.0]):
            self.assertEqual(depth(1), 1)
        self.assertEqual(depth.last_time, 10.0)


class TestLogs(unittest.TestCase):
    def test_merge_log(self):
        log = []
        main.merge_sort([3, 1, 2], log=log)
        self.assertEqual(log, [
            ("call", 0, [3, 1, 2]),
            ("call", 1, [3]),
            ("call", 1, [1, 2]),
            ("call", 2, [1]),
            ("call", 2, [2]),
            ("merge", 1, [1], [2], [1, 2]),
            ("merge", 0, [3], [1, 2], [1, 2, 3]),
        ])

    def test_merge_log_structure(self):
        rng = random.Random(5)
        for n in range(1, 40):
            nums = [rng.randint(0, 9) for _ in range(n)]
            log = []
            main.merge_sort(nums, log=log)
            calls = [e for e in log if e[0] == "call"]
            merges = [e for e in log if e[0] == "merge"]
            # Каждый вызов на части длины >= 2 делает ровно одно слияние
            self.assertEqual(len(calls), 2 * n - 1)
            self.assertEqual(len(merges), n - 1)
            self.assertEqual(max(e[1] for e in calls), (n - 1).bit_length())
            for _, _, left, right, result in merges:
                self.assertEqual(result, sorted(left + right))
            self.assertEqual(log[-1][-1] if n > 1 else log[0][2], sorted(nums))

    def test_quick_log(self):
        log = []
        main.quick_sort([5, 2, 7, 2, 9, 1, 2, 6], log=log)
        self.assertEqual(log[0], (0, 0, 7, 6, 5, [5, 2, 2, 1, 2, 6, 9, 7]))
        self.assertEqual([entry[1:5] for entry in log],
                         [(0, 7, 6, 5), (0, 4, 2, 1), (2, 4, 2, 2), (3, 4, 2, 3), (6, 7, 7, 6)])
        self.assertEqual(log[-1][-1], [1, 2, 2, 2, 5, 6, 7, 9])

    def test_quick_log_on_sorted_input(self):
        # Худший случай: pivot каждый раз максимум, отрезок короче всего на 1
        n = 30
        log = []
        main.quick_sort(list(range(n)), log=log)
        self.assertEqual([(depth, low, high, p) for depth, low, high, _, p, _ in log],
                         [(d, 0, n - 1 - d, n - 1 - d) for d in range(n - 1)])
        comparisons = sum(high - low for _, low, high, _, _, _ in log)
        self.assertEqual(comparisons, n * (n - 1) // 2)

    def test_log_does_not_change_result(self):
        rng = random.Random(8)
        for _ in range(50):
            nums = [rng.randint(0, 9) for _ in range(rng.randint(0, 20))]
            self.assertEqual(main.merge_sort(nums, log=[]), main.merge_sort(nums))
            self.assertEqual(main.quick_sort(nums, log=[]), main.quick_sort(nums))


class TestBenchmark(unittest.TestCase):
    def test_make_input(self):
        self.assertEqual(main.make_input("sorted", 4), [0, 1, 2, 3])
        self.assertEqual(main.make_input("reversed", 4), [4, 3, 2, 1])
        self.assertEqual(main.make_input("equal", 3), [7, 7, 7])
        self.assertEqual(main.make_input("random", 50), main.make_input("random", 50))
        self.assertEqual(len(main.make_input("random", 50)), 50)
        with self.assertRaises(ValueError):
            main.make_input("other", 5)

    def test_worst_sizes_fit_recursion_limit(self):
        self.assertLess(max(main.WORST_SIZES) + 50, sys.getrecursionlimit())

    def test_benchmark_runs(self):
        # Проверяется только структура результата: время зависит от машины
        rows = main.benchmark([("random", 40), ("sorted", 40)], repeats=3)
        self.assertEqual([(kind, n) for kind, n, _, _ in rows], [("random", 40), ("sorted", 40)])
        for _, _, t_merge, t_quick in rows:
            self.assertGreater(t_merge, 0)
            self.assertGreater(t_quick, 0)
        self.assertIn("| sorted | 40 |", main.format_benchmark(rows))

    def test_measure_detects_wrong_sort(self):
        broken = main.timer(lambda nums: list(nums))
        with self.assertRaises(AssertionError):
            main.measure([broken], [2, 1], repeats=1)

    def test_measure_calls_each_sort_repeats_times(self):
        calls = []

        @main.timer
        def counting_sort(nums):
            calls.append(1)
            return sorted(nums)

        main.measure([counting_sort], [3, 1, 2], repeats=4)
        self.assertEqual(len(calls), 4)


class TestModule(unittest.TestCase):
    def test_import_prints_nothing(self):
        out = subprocess.run([sys.executable, "-c", "import homework_6.compare.main"],
                             cwd=ROOT, capture_output=True, text=True, check=True)
        self.assertEqual(out.stdout, "")

    def test_readme_matches_program(self):
        with open(os.path.join(HERE, "README.md"), encoding="utf-8") as f:
            readme = f.read()
        log = []
        main.merge_sort(main.EXAMPLE, log=log)
        self.assertIn(main.format_merge_log(log), readme)
        for example in (main.EXAMPLE, main.BAD_EXAMPLE):
            log = []
            main.quick_sort(example, log=log)
            self.assertIn(main.format_quick_log(log), readme)

    def test_main_output(self):
        buf = io.StringIO()
        with patch.object(main, "benchmark", return_value=[("random", 10, 0.002, 0.001)]):
            with redirect_stdout(buf):
                main.main()
        out = buf.getvalue()
        self.assertIn("[2, 2, 5, 7] + [1, 2, 6, 9] -> [1, 2, 2, 2, 5, 6, 7, 9]", out)
        self.assertIn("| random | 10 | 2.00 | 1.00 | 0.5 |", out)


if __name__ == "__main__":
    unittest.main()
