"""Тесты к задаче 1. Makeheap."""

import itertools
import random
import unittest
from collections import Counter
from pathlib import Path
from unittest.mock import patch

if __package__:
    from homework_7.makeheap import main
else:
    import main


ALGORITHMS = (main.makeheap_n_log_n, main.makeheap)


def is_minheap(arr):
    return all(arr[(i - 1) // 2] <= arr[i] for i in range(1, len(arr)))


class Counted:
    """Считает сравнения ключей, не вмешиваясь в алгоритм."""
    comparisons = 0

    def __init__(self, value):
        self.value = value

    def __lt__(self, other):
        Counted.comparisons += 1
        return self.value < other.value


class TestMakeheap(unittest.TestCase):
    def check_heap(self, nums):
        expected = Counter(nums)
        for algorithm in ALGORITHMS:
            with self.subTest(algorithm=algorithm.__name__):
                arr = list(nums)
                self.assertIs(algorithm(arr), arr)
                self.assertEqual(Counter(arr), expected)
                self.assertTrue(is_minheap(arr))
                if arr:
                    self.assertEqual(arr[0], min(nums))

    def test_examples(self):
        self.check_heap(main.EXAMPLE)
        self.check_heap([3, 2, 1, 5, 6, 4])

    def test_empty_and_single(self):
        self.check_heap([])
        self.check_heap([7])

    def test_two_elements(self):
        for nums in ([1, 2], [2, 1], [1, 1]):
            self.check_heap(nums)

    def test_duplicates_and_negative(self):
        self.check_heap([0, -3, 7, -3, 0, -9, 7, -9])
        self.check_heap([4] * 100)
        self.check_heap([1.5, -2.5, 0.0, 1.5])

    def test_ordered_inputs(self):
        for n in (7, 8, 9, 15, 16, 17, 1000):
            self.check_heap(list(range(n)))
            self.check_heap(list(range(n, 0, -1)))

    def test_exhaustive_small(self):
        for n in range(7):
            for nums in itertools.product(range(-1, 2), repeat=n):
                self.check_heap(nums)

    def test_random(self):
        rng = random.Random(7)
        for _ in range(300):
            self.check_heap([rng.randrange(-50, 51) for _ in range(rng.randrange(200))])

    def test_large(self):
        rng = random.Random(70)
        self.check_heap([rng.randrange(100_000) for _ in range(100_000)])
        self.check_heap(list(range(100_000, 0, -1)))

    def test_no_builtin_sort_or_heap(self):
        for algorithm in ALGORITHMS:
            arr = [4, 1, 3, 2]
            with patch("builtins.sorted", side_effect=AssertionError("sorted")), \
                    patch("heapq.heapify", side_effect=AssertionError("heapify")), \
                    patch("heapq.heappush", side_effect=AssertionError("heappush")):
                algorithm(arr)
            self.assertTrue(is_minheap(arr))

    def test_sift_down_respects_size(self):
        arr = [9, 1, 2, 3, 4, -100, -200]
        main.sift_down(arr, 0, 5)
        self.assertTrue(is_minheap(arr[:5]))
        self.assertEqual(Counter(arr[:5]), Counter([9, 1, 2, 3, 4]))
        self.assertEqual(arr[5:], [-100, -200])

    def test_comparison_bounds(self):
        # Убывающий массив заставляет каждый sift_up дойти до корня.
        for n in (1, 2, 3, 7, 8, 9, 31, 32, 33, 1000, 8192):
            for algorithm in ALGORITHMS:
                arr = [Counted(i) for i in range(n, 0, -1)]
                Counted.comparisons = 0
                algorithm(arr)
                count = Counted.comparisons
                if algorithm is main.makeheap_n_log_n:
                    self.assertEqual(count, sum(i.bit_length() - 1 for i in range(2, n + 1)))
                else:
                    heights = sum(n // (1 << h) for h in range(1, n.bit_length()))
                    self.assertLessEqual(count, 2 * heights)
                self.assertTrue(is_minheap([x.value for x in arr]))

    def test_trace_invariants(self):
        rng = random.Random(71)
        for n in range(50):
            nums = [rng.randrange(-10, 11) for _ in range(n)]
            for algorithm in ALGORITHMS:
                log = []
                arr = nums.copy()
                algorithm(arr, log=log)
                if algorithm is main.makeheap_n_log_n:
                    self.assertEqual([i for i, _ in log], list(range(1, n)))
                else:
                    self.assertEqual([i for i, _ in log], list(range(n // 2 - 1, -1, -1)))
                for i, state in log:
                    self.assertEqual(Counter(state), Counter(nums))
                    self.assertIsNot(state, arr)
                    if algorithm is main.makeheap_n_log_n:
                        self.assertTrue(is_minheap(state[:i + 1]))
                        self.assertEqual(state[i + 1:], nums[i + 1:])
                    else:
                        self.assertEqual(state[:i], nums[:i])
                        for child in range(1, n):
                            parent = (child - 1) // 2
                            if parent >= i:
                                self.assertLessEqual(state[parent], state[child])
                if log:
                    self.assertEqual(log[-1][1], arr)

    def test_readme_matches_program(self):
        readme = Path(__file__).with_name("README.md").read_text(encoding="utf-8")
        for algorithm in ALGORITHMS:
            log = []
            algorithm(main.EXAMPLE.copy(), log=log)
            table = main.format_log(main.EXAMPLE, log, bottom_up=algorithm is main.makeheap)
            self.assertIn(table, readme)


if __name__ == "__main__":
    unittest.main()
