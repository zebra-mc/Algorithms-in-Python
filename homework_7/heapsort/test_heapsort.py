"""Тесты к задаче 3. Heapsort."""

import itertools
import random
import unittest
from collections import Counter
from pathlib import Path
from unittest.mock import patch

if __package__:
    from homework_7.heapsort import main
else:
    import main


class IndexOnlyList(list):
    """Запрещает сортировку, создание копий списка, срезы и смену длины."""

    def __getitem__(self, index):
        if isinstance(index, slice):
            raise AssertionError("срез")
        return super().__getitem__(index)

    def __setitem__(self, index, value):
        if isinstance(index, slice):
            raise AssertionError("срез")
        super().__setitem__(index, value)

    def __iter__(self):
        raise AssertionError("итерация по входу")

    def copy(self):
        raise AssertionError("копирование")

    def sort(self, *args, **kwargs):
        raise AssertionError("list.sort")

    def append(self, value):
        raise AssertionError("append")

    def pop(self, *args):
        raise AssertionError("pop")


class TestHeapsort(unittest.TestCase):
    def check_sort(self, nums):
        arr = list(nums)
        expected = sorted(arr)
        self.assertIs(main.heapsort(arr), arr)
        self.assertEqual(arr, expected)

    def test_example(self):
        self.check_sort(main.EXAMPLE)

    def test_empty_single_two(self):
        for nums in ([], [7], [1, 2], [2, 1], [1, 1]):
            self.check_sort(nums)

    def test_negative_duplicates_and_float(self):
        self.check_sort([0, -1, 7, -3, 7, 0, -3])
        self.check_sort([1.5, -2.5, 0.0, 1.5])

    def test_ordered_and_equal(self):
        for n in (7, 8, 9, 15, 16, 17, 1000):
            for nums in (list(range(n)), list(range(n, 0, -1)), [7] * n):
                self.check_sort(nums)

    def test_exhaustive_small(self):
        for n in range(7):
            for nums in itertools.product(range(-1, 2), repeat=n):
                self.check_sort(nums)

    def test_random(self):
        rng = random.Random(75)
        for _ in range(300):
            self.check_sort([rng.randrange(-100, 101) for _ in range(rng.randrange(200))])

    def test_large(self):
        n = 100_000
        rng = random.Random(76)
        for nums in ([rng.randrange(n) for _ in range(n)], list(range(n)),
                     list(range(n, 0, -1)), [7] * n):
            self.check_sort(nums)

    def test_inplace_and_no_builtin_sort(self):
        arr = IndexOnlyList([3, 1, 6, 2, 3, -1])
        with patch("builtins.sorted", side_effect=AssertionError("sorted")), \
                patch("heapq.heapify", side_effect=AssertionError("heapify")), \
                patch("heapq.heappop", side_effect=AssertionError("heappop")):
            self.assertIs(main.heapsort(arr), arr)
        self.assertEqual(arr, [-1, 1, 2, 3, 3, 6])

    def test_sift_down_respects_size(self):
        arr = [0, 9, 8, 4, 5, 100, 200]
        main.sift_down_max(arr, 0, 5)
        self.assertTrue(all(arr[(i - 1) // 2] >= arr[i] for i in range(1, 5)))
        self.assertEqual(Counter(arr[:5]), Counter([0, 9, 8, 4, 5]))
        self.assertEqual(arr[5:], [100, 200])

    def test_trace_invariants(self):
        rng = random.Random(77)
        for n in range(70):
            nums = [rng.randrange(-10, 11) for _ in range(n)]
            expected = sorted(nums)
            arr = nums.copy()
            log = main.trace_heapsort(arr)
            self.assertEqual(arr, expected)
            self.assertEqual([(phase, index, size) for phase, index, size, _ in log],
                             [("build", i, n) for i in range(n // 2 - 1, -1, -1)] +
                             [("extract", end, end) for end in range(n - 1, 0, -1)])
            for phase, index, size, state in log:
                self.assertEqual(Counter(state), Counter(nums))
                self.assertIsNot(state, arr)
                if phase == "build":
                    self.assertEqual(state[:index], nums[:index])
                    for child in range(1, size):
                        parent = (child - 1) // 2
                        if parent >= index:
                            self.assertGreaterEqual(state[parent], state[child])
                else:
                    self.assertTrue(all(state[(i - 1) // 2] >= state[i] for i in range(1, size)))
                    self.assertEqual(state[size:], expected[size:])
                    self.assertLessEqual(max(state[:size]), min(state[size:]))
            if log:
                self.assertEqual(log[-1][3], arr)

    def test_observer_receives_same_list(self):
        arr = [5, 1, 8, 0]

        def visit(phase, index, size, state):
            self.assertIs(state, arr)

        self.assertIs(main.heapsort(arr, visit=visit), arr)
        self.assertEqual(arr, [0, 1, 5, 8])

    def test_readme_matches_program(self):
        readme = Path(__file__).with_name("README.md").read_text(encoding="utf-8")
        log = main.trace_heapsort(main.EXAMPLE.copy())
        self.assertIn(main.format_log(main.EXAMPLE, log), readme)


if __name__ == "__main__":
    unittest.main()
