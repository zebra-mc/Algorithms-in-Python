"""Тесты к задаче 2. K-th minheap."""

import ast
import heapq
import itertools
import random
import unittest
from pathlib import Path
from unittest.mock import patch

if __package__:
    from homework_7.k_th_minheap import main
else:
    import main


ALGORITHMS = (main.find_kth_largest, main.find_kth_largest_heapq)


class TestKthMinheap(unittest.TestCase):
    def check_answer(self, nums, k):
        before = list(nums)
        expected = sorted(nums, reverse=True)[k - 1]
        for algorithm in ALGORITHMS:
            with self.subTest(algorithm=algorithm.__name__, k=k):
                self.assertEqual(algorithm(nums, k), expected)
                self.assertEqual(nums, before)

    def test_statement(self):
        self.check_answer([3, 2, 1, 5, 6, 4], 2)
        self.check_answer([3, 2, 3, 1, 2, 4, 5, 5, 6], 4)
        self.assertEqual(main.find_kth_largest([3, 2, 1, 5, 6, 4], 2), 5)
        self.assertEqual(main.find_kth_largest_heapq([3, 2, 3, 1, 2, 4, 5, 5, 6], 4), 4)

    def test_all_ranks_with_duplicates(self):
        nums = [3, 2, 3, 1, 2, 4, 5, 5, 6]
        for algorithm in ALGORITHMS:
            self.assertEqual([algorithm(nums, k) for k in range(1, 10)],
                             [6, 5, 5, 4, 3, 3, 2, 2, 1])

    def test_single_and_extreme_k(self):
        self.check_answer([8], 1)
        for k in (1, 5):
            self.check_answer([5, 1, 7, 7, 3], k)

    def test_equal_negative_and_float(self):
        self.check_answer([5] * 30, 17)
        self.check_answer([-1, -8, -2, -2, -4], 3)
        self.check_answer([1.5, -2.5, 1.5, 0.0], 3)

    def test_invalid_k(self):
        for algorithm in ALGORITHMS:
            for nums, k in (([], 1), ([1], 0), ([1], -1), ([1, 2], 3)):
                with self.assertRaises(ValueError):
                    algorithm(nums, k)
            for k in (1.0, "1", None, True, False):
                with self.assertRaises(TypeError):
                    algorithm([1, 2], k)

    def test_exhaustive_small(self):
        for n in range(1, 7):
            for nums in itertools.product(range(-1, 2), repeat=n):
                for k in range(1, n + 1):
                    self.check_answer(list(nums), k)

    def test_random(self):
        rng = random.Random(72)
        for _ in range(300):
            nums = [rng.randrange(-100, 101) for _ in range(rng.randrange(1, 300))]
            self.check_answer(nums, rng.randint(1, len(nums)))

    def test_large_inputs(self):
        n = 100_000
        rng = random.Random(73)
        for nums, k in ((list(range(n)), n // 2),
                        (list(range(n, 0, -1)), 1),
                        ([7] * n, n),
                        ([rng.randrange(5) for _ in range(n)], 10_000)):
            self.check_answer(nums, k)

    def test_custom_heap_does_not_use_heapq(self):
        with patch("builtins.sorted", side_effect=AssertionError("sorted")), \
                patch.object(heapq, "heapify", side_effect=AssertionError("heapify")), \
                patch.object(heapq, "heapreplace", side_effect=AssertionError("heapreplace")), \
                patch.object(heapq, "heappush", side_effect=AssertionError("heappush")), \
                patch.object(heapq, "heappop", side_effect=AssertionError("heappop")):
            self.assertEqual(main.find_kth_largest(main.EXAMPLE, main.K), 4)

    def test_heapq_is_used_and_no_sort(self):
        with patch("builtins.sorted", side_effect=AssertionError("sorted")), \
                patch.object(heapq, "heapify", wraps=heapq.heapify) as heapify, \
                patch.object(heapq, "heapreplace", wraps=heapq.heapreplace) as replace:
            self.assertEqual(main.find_kth_largest_heapq(main.EXAMPLE, main.K), 4)
        self.assertEqual(heapify.call_count, 1)
        self.assertEqual(replace.call_count, 5)

    def test_trace_invariants(self):
        rng = random.Random(74)
        cases = [(main.EXAMPLE, main.K)]
        for n in range(1, 60):
            cases.append(([rng.randrange(-5, 6) for _ in range(n)], rng.randint(1, n)))
        for nums, k in cases:
            for algorithm in ALGORITHMS:
                log = []
                answer = algorithm(nums, k, log=log)
                self.assertEqual(len(log), len(nums) - k + 1)
                for step, (i, value, action, heap) in enumerate(log):
                    self.assertEqual(len(heap), k)
                    self.assertTrue(all(heap[(j - 1) // 2] <= heap[j] for j in range(1, k)))
                    # Эталон — k наибольших элементов каждого обработанного префикса.
                    self.assertEqual(sorted(heap), sorted(nums[:k + step])[-k:])
                    if step == 0:
                        self.assertEqual((i, value, action), (None, None, "построение"))
                    else:
                        self.assertEqual(i, k + step - 1)
                        self.assertEqual(value, nums[i])
                        previous = log[step - 1][3]
                        if value <= previous[0]:
                            self.assertEqual(action, "пропуск")
                            self.assertEqual(heap, previous)
                        else:
                            self.assertEqual(action, "замена")
                            self.assertEqual(sorted(heap), sorted(previous[1:] + [value]))
                self.assertEqual(answer, log[-1][3][0])
                self.assertEqual(len({id(row[3]) for row in log}), len(log))

    def test_readme_matches_program(self):
        readme = Path(__file__).with_name("README.md").read_text(encoding="utf-8")
        own, library = [], []
        main.find_kth_largest(main.EXAMPLE, main.K, log=own)
        main.find_kth_largest_heapq(main.EXAMPLE, main.K, log=library)
        self.assertIn(main.format_log(own), readme)

        # heapq не обещает конкретную перестановку внутри кучи.
        # Сверяем таблицу второй реализации по действиям, корню и мультимножеству.
        section = readme.split("### С использованием heapq\n", 1)[1]
        rows = [line.strip("|").split("|") for line in section.splitlines()
                if line.startswith("|") and line.split("|")[1].strip().isdigit()]
        self.assertEqual(len(rows), len(library))
        for step, (cells, (i, value, action, heap)) in enumerate(zip(rows, library)):
            fields = [cell.strip() for cell in cells]
            documented = ast.literal_eval(fields[4].strip("`"))
            self.assertEqual(fields[:4], [str(step), "—" if i is None else str(i),
                                          "—" if value is None else str(value), action])
            self.assertEqual(sorted(documented), sorted(heap))
            self.assertEqual(documented[0], heap[0])
            self.assertEqual(fields[5], str(heap[0]))
            self.assertTrue(all(documented[(j - 1) // 2] <= documented[j]
                                for j in range(1, len(documented))))


if __name__ == "__main__":
    unittest.main()
