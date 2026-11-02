"""Тесты к задаче 2 "Permutations".

Запуск из корня репозитория:
    python -m unittest discover -s homework_5/permutations -p "test_*.py" -v
"""

import ast
import io
import math
import os
import subprocess
import sys
import unittest
from collections import Counter
from contextlib import redirect_stdout
from itertools import permutations

import homework_5.permutations.main as perm_main
import homework_5.tracer.main as tracer_main
from homework_5.permutations.main import permute

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))


def oracle(nums):
    """Независимый эталон: различные перестановки itertools в порядке первого появления."""
    return [list(p) for p in dict.fromkeys(permutations(nums))]


def oracle_prefixes(nums):
    """Начала перестановок в порядке обхода в глубину – ожидаемые path при входах.

    Для каждой перестановки из эталона выписываются ее префиксы длины 0..n;
    dict.fromkeys оставляет первое появление, что и дает порядок preorder.
    """
    perms = dict.fromkeys(permutations(nums))
    return [list(p) for p in dict.fromkeys(p[:k] for p in perms for k in range(len(nums) + 1))]


def run_traced(nums):
    """permute(nums, trace=True): результат и напечатанные строки."""
    buf = io.StringIO()
    with redirect_stdout(buf):
        result = permute(nums, trace=True)
    return result, buf.getvalue()


def parse_trace(text):
    """Строки трассировки -> список (вход?, отступ, path, возвращенное число или None)."""
    events = []
    for line in text.splitlines():
        body = line.lstrip(" ")
        indent = len(line) - len(body)
        call, _, value = body[2:].partition(" = ")
        path = ast.literal_eval(call[len("backtrack("):-1])
        events.append((body.startswith("→"), indent, path, int(value) if value else None))
    return events


class TestExamples(unittest.TestCase):

    def test_statement_examples(self):
        """Примеры из условия, включая порядок"""
        self.assertEqual(permute([1, 2, 3]), [[1, 2, 3], [1, 3, 2], [2, 1, 3],
                                              [2, 3, 1], [3, 1, 2], [3, 2, 1]])
        self.assertEqual(permute([0, 1]), [[0, 1], [1, 0]])
        self.assertEqual(permute([1]), [[1]])

    def test_empty(self):
        """Пустой массив: одна пустая перестановка"""
        self.assertEqual(permute([]), [[]])

    def test_negative_and_zero(self):
        """Отрицательные числа и ноль"""
        self.assertEqual(permute([-1, 0]), [[-1, 0], [0, -1]])
        self.assertEqual(permute([0, -5, 7]), oracle([0, -5, 7]))

    def test_against_itertools(self):
        """Различные значения: совпадение с itertools.permutations вместе с порядком"""
        for nums in ([4, 1, 3, 2], [3, 1, 2], [10, -10, 0, 5, 1], list(range(6)),
                     [9, 8, 7, 6, 5, 4, 3]):
            self.assertEqual(permute(nums), oracle(nums), nums)


class TestDuplicates(unittest.TestCase):

    def test_example(self):
        """[1, 1, 2]: только различные перестановки значений"""
        self.assertEqual(permute([1, 1, 2]), [[1, 1, 2], [1, 2, 1], [2, 1, 1]])

    def test_against_oracle(self):
        """Повторы в разных местах: совпадение с эталоном и мультиномиальное число"""
        for nums in ([2, 1, 1], [1, 1, 1], [3, 1, 3, 1], [0, 0, -1, 0, 5], [2, 2, 1, 1, 2, 3]):
            result = permute(nums)
            self.assertEqual(result, oracle(nums), nums)
            expected = math.factorial(len(nums))
            for k in Counter(nums).values():
                expected //= math.factorial(k)
            self.assertEqual(len(result), expected, nums)


class TestProperties(unittest.TestCase):

    def test_shape(self):
        """n! штук, все различны, каждая – тот же мультимножество элементов"""
        for n in range(7):
            nums = [3 * i - 7 for i in range(n)]
            result = permute(nums)
            self.assertEqual(len(result), math.factorial(n))
            self.assertEqual(len({tuple(p) for p in result}), len(result))
            for p in result:
                self.assertEqual(len(p), n)
                self.assertEqual(Counter(p), Counter(nums))

    def test_input_not_modified(self):
        """Исходный массив не меняется, в том числе при трассировке"""
        nums = [3, 1, 2]
        permute(nums)
        run_traced(nums)
        self.assertEqual(nums, [3, 1, 2])

    def test_independent_lists(self):
        """Перестановки – разные объекты: изменение одной не задевает другие"""
        result = permute([1, 2, 3])
        self.assertEqual(len({id(p) for p in result}), 6)
        result[0].append(99)
        result[1].clear()
        self.assertEqual(result[2:], [[2, 1, 3], [2, 3, 1], [3, 1, 2], [3, 2, 1]])

    def test_repeated_calls(self):
        """Повторные вызовы независимы, в том числе после изменения прошлого результата"""
        first = permute([1, 2, 3])
        first[0][0] = 100
        self.assertEqual(permute([1, 2, 3]), oracle([1, 2, 3]))
        self.assertEqual(permute([5, 6]), [[5, 6], [6, 5]])


class TestTrace(unittest.TestCase):

    def test_uses_tracer_from_task_1(self):
        """Используется декоратор задачи 1, а не его копия"""
        self.assertIs(perm_main.tracer, tracer_main.tracer)

    def test_silent_by_default(self):
        """Без trace=True ничего не печатается"""
        buf = io.StringIO()
        with redirect_stdout(buf):
            permute([1, 2, 3])
        self.assertEqual(buf.getvalue(), "")

    def test_exact_small(self):
        """Точный текст трассировки для [1, 2]"""
        result, out = run_traced([1, 2])
        self.assertEqual(result, [[1, 2], [2, 1]])
        self.assertEqual(out,
                         "→ backtrack([])\n"
                         "  → backtrack([1])\n"
                         "    → backtrack([1, 2])\n"
                         "    ← backtrack([1, 2]) = 1\n"
                         "  ← backtrack([1]) = 1\n"
                         "  → backtrack([2])\n"
                         "    → backtrack([2, 1])\n"
                         "    ← backtrack([2, 1]) = 1\n"
                         "  ← backtrack([2]) = 1\n"
                         "← backtrack([]) = 2\n")

    def test_trace_does_not_change_result(self):
        """С трассировкой результат тот же"""
        for nums in ([], [1], [1, 2, 3], [1, 1, 2], [4, -1, 0, 2]):
            self.assertEqual(run_traced(nums)[0], permute(nums), nums)

    def test_order_depth_and_returns(self):
        """Порядок входов – обход в глубину, отступ = 2 * len(path), возвраты верны

        Проверка идет по тексту трассировки и эталонам из itertools, без
        обращения к внутреннему состоянию permute.
        """
        for nums in ([1, 2, 3], [4, 1, 3, 2], [1, 1, 2], [2, 1, 2, 1]):
            n = len(nums)
            events = parse_trace(run_traced(nums)[1])
            entries = [path for is_entry, _, path, _ in events if is_entry]
            self.assertEqual(entries, oracle_prefixes(nums), nums)
            stack = []
            for is_entry, indent, path, value in events:
                if is_entry:
                    self.assertEqual(indent, 2 * len(stack))
                    stack.append(path)
                else:
                    self.assertEqual(path, stack.pop())
                    self.assertEqual(indent, 2 * len(stack))
                    # Вызов возвращает число перестановок, начинающихся с path
                    tail = Counter(nums) - Counter(path)
                    self.assertEqual(value, len(oracle(list(tail.elements()))))
                self.assertEqual(indent, 2 * len(path))
            self.assertEqual(stack, [])

    def test_call_count(self):
        """Число вызовов для n различных значений: сумма n! / (n - k)! по k = 0..n"""
        for n in range(6):
            calls = run_traced(list(range(n)))[1].count("→")
            self.assertEqual(calls, sum(math.perm(n, k) for k in range(n + 1)))

    def test_readme_matches_program(self):
        """Трассировка в README совпадает с фактическим выводом"""
        with open(os.path.join(HERE, "README.md"), encoding="utf-8") as f:
            readme = f.read()
        self.assertIn(run_traced([1, 2, 3])[1], readme)

    def test_import_is_silent(self):
        """Импорт модуля ничего не печатает"""
        out = subprocess.run([sys.executable, "-c", "import homework_5.permutations.main"],
                             cwd=ROOT, capture_output=True, text=True, check=True).stdout
        self.assertEqual(out, "")


if __name__ == "__main__":
    unittest.main()
