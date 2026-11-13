"""Тесты к задаче 2 "Iterative".

Запуск из папки задачи: python -m unittest -v
Из корня репозитория: python -m unittest discover -v
"""

import io
import itertools
import os
import random
import subprocess
import sys
import unittest
from collections import Counter
from contextlib import redirect_stdout

try:
    from homework_6.iterative import main
except ModuleNotFoundError:
    import main

# Общие тесты сортировок и рекурсивные версии берутся из задачи 1. main.py
# при запуске из папки задачи уже добавил корень репозитория в sys.path
from homework_6.compare import main as compare
from homework_6.compare.test_compare import Item, SortContract

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))


def max_self_nesting(func, *args):
    """Сколько раз одна и та же функция Python максимум была активна одновременно.

    Через sys.setprofile считаются входы и выходы всех вызываемых функций,
    включая вспомогательные. 1 - рекурсии нет ни в одной из них.
    """
    active = Counter()
    worst = 0

    def profiler(frame, event, arg):
        nonlocal worst
        if event == "call":
            active[frame.f_code] += 1
            worst = max(worst, active[frame.f_code])
        elif event == "return":
            active[frame.f_code] -= 1

    sys.setprofile(profiler)
    try:
        func(*args)
    finally:
        sys.setprofile(None)
    return worst


class TestMergeSortIterative(SortContract, unittest.TestCase):
    sort = staticmethod(main.merge_sort_iterative)


class TestQuickSortIterative(SortContract, unittest.TestCase):
    sort = staticmethod(main.quick_sort_iterative)
    # Больше предела рекурсии: рекурсивная версия на этих входах падает.
    # Время здесь Θ(n²), поэтому не 5000
    big_degenerate_n = 2000


class TestSameAsRecursive(unittest.TestCase):
    def test_same_results(self):
        rng = random.Random(42)
        for _ in range(300):
            nums = [rng.randint(-10, 10) for _ in range(rng.randint(0, 50))]
            expected = compare.merge_sort(nums)
            self.assertEqual(compare.quick_sort(nums), expected)
            self.assertEqual(main.merge_sort_iterative(nums), expected)
            self.assertEqual(main.quick_sort_iterative(nums), expected)

    def test_quick_sort_does_same_partitions(self):
        # Разбиение отрезка зависит только от его содержимого, а отрезки в стеке
        # не пересекаются. Поэтому итеративная версия делает те же partition,
        # что рекурсивная, только в другом порядке
        rng = random.Random(9)
        for _ in range(200):
            nums = [rng.randint(0, 9) for _ in range(rng.randint(0, 40))]
            rec_log, it_log = [], []
            compare.quick_sort(nums, log=rec_log)
            main.quick_sort_iterative(nums, log=it_log)
            rec = sorted(entry[1:5] for entry in rec_log)  # (low, high, pivot, p)
            it = sorted(entry[1:5] for entry in it_log)
            self.assertEqual(rec, it)

    def test_merge_sort_is_stable(self):
        items = [Item(k, tag) for tag, k in enumerate([3, 1, 3, 2, 1, 3, 2, 1, 0])]
        result = main.merge_sort_iterative(items)
        self.assertEqual([(x.key, x.tag) for x in result],
                         [(x.key, x.tag) for x in compare.merge_sort(items)])
        self.assertEqual([x.tag for x in result], [8, 1, 4, 7, 3, 6, 0, 2, 5])


class TestNoRecursion(unittest.TestCase):
    def test_checker_sees_recursion(self):
        self.assertGreater(max_self_nesting(compare.merge_sort, [3, 1, 2, 5, 4]), 1)
        self.assertGreater(max_self_nesting(compare.quick_sort, [3, 1, 2, 5, 4]), 1)

    def test_iterative_versions(self):
        rng = random.Random(1)
        for nums in ([], [1], [5, 2, 7, 2, 9, 1, 2, 6, 3], list(range(100)),
                     [rng.randint(0, 5) for _ in range(200)]):
            with self.subTest(n=len(nums)):
                self.assertEqual(max_self_nesting(main.merge_sort_iterative, nums), 1)
                self.assertEqual(max_self_nesting(main.quick_sort_iterative, nums), 1)

    def test_sorted_input_longer_than_recursion_limit(self):
        n = sys.getrecursionlimit() + 500
        self.assertEqual(main.quick_sort_iterative(list(range(n, 0, -1))), list(range(1, n + 1)))


class TestMergeLog(unittest.TestCase):
    def test_example(self):
        log = []
        main.merge_sort_iterative([5, 2, 7, 2, 9, 1, 2, 6, 3], log=log)
        self.assertEqual(log, [
            (1, [2, 5, 2, 7, 1, 9, 2, 6, 3]),
            (2, [2, 2, 5, 7, 1, 2, 6, 9, 3]),
            (4, [1, 2, 2, 2, 5, 6, 7, 9, 3]),
            (8, [1, 2, 2, 2, 3, 5, 6, 7, 9]),
        ])

    def test_passes_and_blocks(self):
        rng = random.Random(3)
        for n in range(0, 70):
            nums = [rng.randint(0, 9) for _ in range(n)]
            log = []
            main.merge_sort_iterative(nums, log=log)
            # Проходов ceil(log2 n), ширины 1, 2, 4, ...
            passes = max(n - 1, 0).bit_length()
            self.assertEqual([width for width, _ in log], [2 ** i for i in range(passes)])
            for width, arr in log:
                # Инвариант: после прохода каждый блок длины 2 * width отсортирован
                # и состоит из тех же элементов, что и в исходном массиве
                for start in range(0, n, 2 * width):
                    block = arr[start:start + 2 * width]
                    self.assertEqual(block, sorted(nums[start:start + 2 * width]))


class TestQuickStack(unittest.TestCase):
    def check_steps(self, nums):
        """Проверяет инварианты стека на каждом шаге журнала."""
        log = []
        result = main.quick_sort_iterative(nums, log=log)
        expected = sorted(nums)
        for before, low, high, pivot, p, arr, pushed in log:
            self.assertEqual(before[-1], (low, high))
            stack = before[:-1] + pushed
            covered = [False] * len(nums)
            for a, b in stack:
                self.assertLess(a, b, "в стеке отрезок длины меньше 2")
                for i in range(a, b + 1):
                    self.assertFalse(covered[i], "отрезки в стеке пересекаются")
                    covered[i] = True
            # Инвариант: все позиции вне отрезков стека уже окончательные
            for i, in_stack in enumerate(covered):
                if not in_stack:
                    self.assertEqual(arr[i], expected[i])
            if len(pushed) == 2:
                first, second = pushed
                self.assertGreaterEqual(first[1] - first[0], second[1] - second[0],
                                        "меньший отрезок должен лежать сверху")
        self.assertEqual(result, expected)

    def test_invariants_exhaustive(self):
        for n in range(1, 7):
            for nums in itertools.product(range(4), repeat=n):
                self.check_steps(list(nums))

    def test_stack_size_bound(self):
        rng = random.Random(5)
        inputs = [list(range(n)) for n in (2, 3, 64, 500)]
        inputs += [list(p) for p in itertools.permutations(range(7))]
        inputs += [rng.sample(range(n), n) for n in (16, 100, 1000) for _ in range(20)]
        inputs += [[rng.randint(0, 3) for _ in range(300)] for _ in range(20)]
        for nums in inputs:
            log = []
            main.quick_sort_iterative(nums, log=log)
            largest = max(max(len(before), len(before) - 1 + len(pushed))
                          for before, *_, pushed in log)
            # n >= 2: в стеке не больше floor(log2 n) отрезков
            self.assertLessEqual(largest, len(nums).bit_length() - 1, nums)

    def test_example(self):
        log = []
        main.quick_sort_iterative([5, 2, 7, 2, 9, 1, 2, 6], log=log)
        self.assertEqual([(before, (low, high), pivot, p, pushed)
                          for before, low, high, pivot, p, _, pushed in log], [
            ([(0, 7)], (0, 7), 6, 5, [(0, 4), (6, 7)]),
            ([(0, 4), (6, 7)], (6, 7), 7, 6, []),
            ([(0, 4)], (0, 4), 2, 1, [(2, 4)]),
            ([(2, 4)], (2, 4), 2, 2, [(3, 4)]),
            ([(3, 4)], (3, 4), 2, 3, []),
        ])

    def test_empty_and_single(self):
        for nums in ([], [4]):
            log = []
            self.assertEqual(main.quick_sort_iterative(nums, log=log), nums)
            self.assertEqual(log, [])


class TestModule(unittest.TestCase):
    def test_import_prints_nothing(self):
        out = subprocess.run([sys.executable, "-c", "import homework_6.iterative.main"],
                             cwd=ROOT, capture_output=True, text=True, check=True)
        self.assertEqual(out.stdout, "")

    def test_readme_matches_program(self):
        with open(os.path.join(HERE, "README.md"), encoding="utf-8") as f:
            readme = f.read()
        log = []
        main.merge_sort_iterative(main.MERGE_EXAMPLE, log=log)
        self.assertIn(main.format_merge_log(main.MERGE_EXAMPLE, log), readme)
        for example in (main.QUICK_EXAMPLE, main.BAD_EXAMPLE):
            log = []
            main.quick_sort_iterative(example, log=log)
            self.assertIn(main.format_quick_log(log), readme)

    def test_main_output_both_ways(self):
        buf = io.StringIO()
        with redirect_stdout(buf):
            main.main()
        from_folder = subprocess.run([sys.executable, "main.py"], cwd=HERE,
                                     capture_output=True, text=True, check=True)
        self.assertEqual(from_folder.stdout, buf.getvalue())
        self.assertIn("width = 8:   1 2 2 2 3 5 6 7 9", buf.getvalue())


if __name__ == "__main__":
    unittest.main()
