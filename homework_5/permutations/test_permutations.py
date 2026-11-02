"""Тесты к задаче 2 "Permutations".

Запуск из папки задачи: python -m unittest -v
Из корня репозитория все тесты ДЗ 5: python -m unittest discover -v
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
from unittest.mock import patch

# Полное имя нужно при общем запуске из корня, где у каждой задачи свой main.py.
# Из папки задачи импортируется свой main.py, а он сам находит пакет homework_5
try:
    from homework_5.permutations import main as perm_main
except ModuleNotFoundError:
    import main as perm_main
from homework_5.tracer import main as tracer_main

permute = perm_main.permute

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


def run_main(*answers):
    """main() с ответами answers на вызовы input(): (напечатанный текст, сколько было вопросов)."""
    buf = io.StringIO()
    with patch("builtins.input", side_effect=list(answers)) as fake_input, redirect_stdout(buf):
        perm_main.main()
    return buf.getvalue(), fake_input.call_count


def printed_permutations(out):
    """Перестановки, напечатанные между 'Перестановки:' и 'Всего:'."""
    block = out.split("Перестановки:\n", 1)[1].split("Всего:", 1)[0]
    return [ast.literal_eval(line) for line in block.splitlines()]


class TestConsole(unittest.TestCase):

    def test_permutations_output(self):
        """Ввод чисел: каждая перестановка с новой строки, в порядке permute()"""
        for line, nums in (("1 2 3", [1, 2, 3]), ("0 1", [0, 1]), ("1", [1]),
                           ("-1 0 -7", [-1, 0, -7]), ("1 1 2", [1, 1, 2]),
                           ("  5   -5 ", [5, -5])):
            out, _ = run_main(line, "н")
            self.assertEqual(printed_permutations(out), oracle(nums), line)
            self.assertIn(f"Всего: {len(oracle(nums))}", out)
        out, _ = run_main("1 2 3", "")
        self.assertEqual(printed_permutations(out), [[1, 2, 3], [1, 3, 2], [2, 1, 3],
                                                     [2, 3, 1], [3, 1, 2], [3, 2, 1]])

    def test_empty_input(self):
        """Пустая строка – пустой массив, одна пустая перестановка, как permute([])"""
        out, _ = run_main("", "н")
        self.assertEqual(printed_permutations(out), [[]])

    def test_bad_input(self):
        """Не число: понятное сообщение, без исключения и без вопроса о трассировке"""
        for line in ("1 2 abc", "1.5", "x"):
            out, asked = run_main(line)
            self.assertIn("не целое число", out)
            self.assertNotIn("Перестановки", out)
            self.assertEqual(asked, 1)
        self.assertIn("'abc'", run_main("1 2 abc")[0])

    def test_trace_yes(self):
        """Ответ 'д': печатается настоящая трассировка tracer, как у permute(trace=True)"""
        for nums in ([1, 2, 3], [1, 1, 2], []):
            line = " ".join(map(str, nums))
            out, _ = run_main(line, "д")
            self.assertTrue(out.endswith(run_traced(nums)[1]), nums)
            self.assertIn("Стек рекурсивных вызовов", out)

    def test_trace_no_or_enter(self):
        """Ответ 'н' или Enter: трассировки нет, программа завершается"""
        for answer in ("н", "", "  "):
            out, asked = run_main("1 2 3", answer)
            self.assertNotIn("→", out)
            self.assertNotIn("Стек рекурсивных вызовов", out)
            self.assertEqual(asked, 2)

    def test_closed_input(self):
        """Ввод закрыт (Ctrl+D) – завершение без исключения"""
        self.assertEqual(run_main(EOFError())[1], 1)
        out, _ = run_main("1 2", EOFError())
        self.assertNotIn("→", out)

    def test_large_input_warning(self):
        """Много элементов: предупреждение и подтверждение только в консоли"""
        out, asked = run_main(" ".join(map(str, range(9))), "н")
        self.assertIn("362 880", out)
        self.assertNotIn("Перестановки:", out)
        self.assertEqual(asked, 1 + 1)
        out, _ = run_main("1 2 3 4 5", "н")
        self.assertIn("до 652 строк", out)          # 2 · (1 + 5 + 20 + 60 + 120 + 120)
        self.assertNotIn("Внимание", run_main("1 2 3", "н")[0])

    def test_no_input_on_import(self):
        """Импорт не вызывает input() и ничего не печатает"""
        code = ("import builtins\n"
                "def fail(*a): raise AssertionError('input() при импорте')\n"
                "builtins.input = fail\n"
                "from homework_5.permutations.main import permute\n"
                "assert permute([1, 2]) == [[1, 2], [2, 1]]\n")
        out = subprocess.run([sys.executable, "-c", code], cwd=ROOT, capture_output=True,
                             text=True, check=True).stdout
        self.assertEqual(out, "")

    def test_both_launch_modes(self):
        """python -m из корня и python main.py из папки задачи работают одинаково"""
        # В Windows потоки дочернего процесса по умолчанию в кодировке системы
        # (например, cp1251), где нет '→' и '←'. Явно задаем UTF-8 с обеих сторон
        env = os.environ.copy()
        env["PYTHONIOENCODING"] = "utf-8"
        outputs = []
        for cmd, cwd in (([sys.executable, "-m", "homework_5.permutations.main"], ROOT),
                         ([sys.executable, "main.py"], HERE)):
            try:
                completed = subprocess.run(cmd, cwd=cwd, input="1 2 3\nд\n",
                                           capture_output=True, text=True,
                                           encoding="utf-8", env=env, check=True)
            except subprocess.CalledProcessError as exc:
                self.fail(f"{cmd} завершился с кодом {exc.returncode}, stderr:\n{exc.stderr}")
            outputs.append(completed.stdout)
        self.assertEqual(outputs[0], outputs[1])
        self.assertTrue(outputs[0].endswith(run_traced([1, 2, 3])[1]))


if __name__ == "__main__":
    unittest.main()
