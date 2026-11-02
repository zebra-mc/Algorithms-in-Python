"""Тесты к задаче 1 "Tracer".

Запуск из папки задачи: python -m unittest -v
Из корня репозитория все тесты ДЗ 5: python -m unittest discover -v
"""

import io
import math
import os
import subprocess
import sys
import unittest
from contextlib import redirect_stdout

# Из корня модуль берется по полному имени: у всех задач файл называется main.py,
# и при общем запуске простой "import main" подхватил бы чужой модуль
try:
    from homework_5.tracer import main
except ModuleNotFoundError:
    import main

factorial, fibonacci, tracer = main.factorial, main.fibonacci, main.tracer

HERE = os.path.dirname(os.path.abspath(__file__))

# Трассировка fibonacci(4), выписанная вручную по дереву вызовов. Этот же блок
# стоит в README в разделе "Визуализация" (см. test_readme_matches_program).
FIB_4 = """\
→ fibonacci(4)
  → fibonacci(3)
    → fibonacci(2)
      → fibonacci(1)
      ← fibonacci(1) = 1
      → fibonacci(0)
      ← fibonacci(0) = 0
    ← fibonacci(2) = 1
    → fibonacci(1)
    ← fibonacci(1) = 1
  ← fibonacci(3) = 2
  → fibonacci(2)
    → fibonacci(1)
    ← fibonacci(1) = 1
    → fibonacci(0)
    ← fibonacci(0) = 0
  ← fibonacci(2) = 1
← fibonacci(4) = 3
"""


def run(func, *args, **kwargs):
    """Вызывает func, возвращает (результат, напечатанный текст)."""
    buf = io.StringIO()
    with redirect_stdout(buf):
        result = func(*args, **kwargs)
    return result, buf.getvalue()


def check_nesting(test, text):
    """Независимая проверка структуры трассировки по одному лишь тексту.

    Разбирает строки и ведет свой стек открытых вызовов: каждый вход должен
    иметь отступ 2 * (число открытых вызовов), каждый выход – закрывать
    последний открытый вызов с той же записью аргументов и тем же отступом.
    Возвращает число вызовов.
    """
    stack = []
    calls = 0
    for line in text.splitlines():
        body = line.lstrip(" ")
        indent = len(line) - len(body)
        if body.startswith("→ "):
            test.assertEqual(indent, 2 * len(stack), line)
            stack.append(body[2:])
            calls += 1
        else:
            test.assertTrue(body.startswith("← "), line)
            test.assertTrue(stack, f"выход без входа: {line}")
            call = body[2:].partition(" = ")[0].partition(" ! ")[0]
            test.assertEqual(call, stack.pop(), line)
            test.assertEqual(indent, 2 * len(stack), line)
    test.assertEqual(stack, [], "остались незакрытые вызовы")
    return calls


# Вспомогательные рекурсивные функции для тестов

@tracer
def countdown(n, step=1, *, label="t"):
    """Ничего не возвращает (None); нужна для проверки именованных аргументов."""
    if n <= 0:
        return None
    return countdown(n - step, step=step, label=label)


@tracer
def reverse(s):
    """Переворот строки: результат – строка, а не число."""
    if len(s) <= 1:
        return s
    return reverse(s[1:]) + s[0]


@tracer
def drain(items):
    """Опустошает список, считая шаги; изменяет свой аргумент."""
    if not items:
        return 0
    items.pop()
    return 1 + drain(items)


@tracer
def is_even(n):
    """Взаимная рекурсия с is_odd."""
    return True if n == 0 else is_odd(n - 1)


@tracer
def is_odd(n):
    return False if n == 0 else is_even(n - 1)


@tracer
def fall(n):
    """Спускается до 0 и там бросает исключение."""
    if n == 0:
        raise ValueError("дно")
    return fall(n - 1)


@tracer
def risky(n):
    """Перехватывает исключение дочернего вызова и пробует другую ветку."""
    if n < 0:
        raise ValueError("n < 0")
    if n == 0:
        return 0
    try:
        return risky(n - 2)
    except ValueError:
        return risky(n - 1)


class TestTrace(unittest.TestCase):

    def test_factorial(self):
        """Линейная рекурсия: точный текст трассировки"""
        result, out = run(factorial, 3)
        self.assertEqual(result, 6)
        self.assertEqual(out,
                         "→ factorial(3)\n"
                         "  → factorial(2)\n"
                         "    → factorial(1)\n"
                         "    ← factorial(1) = 1\n"
                         "  ← factorial(2) = 2\n"
                         "← factorial(3) = 6\n")

    def test_fibonacci(self):
        """Ветвящаяся рекурсия: точный текст, братья на одном уровне"""
        result, out = run(fibonacci, 4)
        self.assertEqual(result, 3)
        self.assertEqual(out, FIB_4)

    def test_base_case(self):
        """Базовый случай: ровно две строки без отступа"""
        self.assertEqual(run(factorial, 1), (1, "→ factorial(1)\n← factorial(1) = 1\n"))
        self.assertEqual(run(fibonacci, 0), (0, "→ fibonacci(0)\n← fibonacci(0) = 0\n"))

    def test_results_unchanged(self):
        """Результаты совпадают с независимыми эталонами"""
        fib = [0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89]
        for n in range(len(fib)):
            self.assertEqual(run(fibonacci, n)[0], fib[n])
        for n in range(1, 15):
            self.assertEqual(run(factorial, n)[0], math.factorial(n))
        self.assertIs(type(run(factorial, 20)[0]), int)

    def test_nesting_and_call_count(self):
        """Структура трассировки и число вызовов: 2F(n+1) - 1 для fibonacci, n для factorial"""
        fib = [0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89]
        for n in range(11):
            calls = check_nesting(self, run(fibonacci, n)[1])
            self.assertEqual(calls, 2 * fib[n + 1] - 1, n)
        for n in range(1, 30):
            self.assertEqual(check_nesting(self, run(factorial, n)[1]), n)

    def test_max_indent(self):
        """Наибольший отступ равен 2 * (глубина - 1)"""
        out = run(factorial, 6)[1]
        self.assertEqual(max(len(s) - len(s.lstrip()) for s in out.splitlines()), 2 * 5)


class TestState(unittest.TestCase):

    def test_repeated_calls(self):
        """Повторный запуск начинается с нулевого уровня и печатает то же самое"""
        first = run(fibonacci, 4)[1]
        second = run(fibonacci, 4)[1]
        self.assertEqual(first, second)
        self.assertEqual(main._depth, 0)

    def test_several_functions(self):
        """Разные декорированные функции подряд: глубина не переносится"""
        out = run(lambda: (factorial(2), fibonacci(1), reverse("ab")))[1]
        self.assertEqual(out,
                         "→ factorial(2)\n"
                         "  → factorial(1)\n"
                         "  ← factorial(1) = 1\n"
                         "← factorial(2) = 2\n"
                         "→ fibonacci(1)\n"
                         "← fibonacci(1) = 1\n"
                         "→ reverse('ab')\n"
                         "  → reverse('b')\n"
                         "  ← reverse('b') = 'b'\n"
                         "← reverse('ab') = 'ba'\n")

    def test_mutual_recursion(self):
        """Взаимная рекурсия: вложенность считается по всем декорированным вызовам"""
        result, out = run(is_even, 3)
        self.assertIs(result, False)
        self.assertEqual(out,
                         "→ is_even(3)\n"
                         "  → is_odd(2)\n"
                         "    → is_even(1)\n"
                         "      → is_odd(0)\n"
                         "      ← is_odd(0) = False\n"
                         "    ← is_even(1) = False\n"
                         "  ← is_odd(2) = False\n"
                         "← is_even(3) = False\n")

    def test_exception_propagates(self):
        """Исключение доходит до вызывающего, выходы напечатаны, глубина сброшена"""
        buf = io.StringIO()
        with redirect_stdout(buf), self.assertRaises(ValueError) as ctx:
            fall(2)
        self.assertEqual(str(ctx.exception), "дно")
        self.assertEqual(buf.getvalue(),
                         "→ fall(2)\n"
                         "  → fall(1)\n"
                         "    → fall(0)\n"
                         "    ← fall(0) ! ValueError: дно\n"
                         "  ← fall(1) ! ValueError: дно\n"
                         "← fall(2) ! ValueError: дно\n")
        self.assertEqual(main._depth, 0)
        self.assertEqual(run(factorial, 1)[1], "→ factorial(1)\n← factorial(1) = 1\n")

    def test_exception_caught_inside(self):
        """Исключение перехвачено внутри рекурсии: следующий дочерний вызов на верном уровне"""
        result, out = run(risky, 1)
        self.assertEqual(result, 0)
        self.assertEqual(out,
                         "→ risky(1)\n"
                         "  → risky(-1)\n"
                         "  ← risky(-1) ! ValueError: n < 0\n"
                         "  → risky(0)\n"
                         "  ← risky(0) = 0\n"
                         "← risky(1) = 0\n")
        # risky(5) -> 3 -> 1 -> -1 (ошибка) и 0: пять вызовов
        self.assertEqual(check_nesting(self, run(risky, 5)[1]), 5)


class TestArguments(unittest.TestCase):

    def test_positional_and_keyword(self):
        """Позиционные, именованные и keyword-only аргументы; результат None"""
        result, out = run(countdown, 3, step=2, label="x")
        self.assertIsNone(result)
        self.assertEqual(out,
                         "→ countdown(3, step=2, label='x')\n"
                         "  → countdown(1, step=2, label='x')\n"
                         "    → countdown(-1, step=2, label='x')\n"
                         "    ← countdown(-1, step=2, label='x') = None\n"
                         "  ← countdown(1, step=2, label='x') = None\n"
                         "← countdown(3, step=2, label='x') = None\n")

    def test_string_result(self):
        """Нечисловой результат печатается через repr и не меняется"""
        result, out = run(reverse, "abc")
        self.assertEqual(result, "cba")
        self.assertIn("← reverse('abc') = 'cba'\n", out)
        self.assertEqual(check_nesting(self, out), 3)

    def test_mutable_argument(self):
        """Строка возврата повторяет строку входа, даже если аргумент изменили"""
        data = [1, 2]
        result, out = run(drain, data)
        self.assertEqual((result, data), (2, []))
        self.assertEqual(out,
                         "→ drain([1, 2])\n"
                         "  → drain([1])\n"
                         "    → drain([])\n"
                         "    ← drain([]) = 0\n"
                         "  ← drain([1]) = 1\n"
                         "← drain([1, 2]) = 2\n")


class TestModule(unittest.TestCase):

    def test_metadata(self):
        """functools.wraps сохраняет имя, docstring и ссылку на исходную функцию"""
        self.assertEqual(factorial.__name__, "factorial")
        self.assertIn("линейная рекурсия", factorial.__doc__)
        self.assertEqual(countdown.__wrapped__.__name__, "countdown")

    def test_import_is_silent(self):
        """Импорт main ничего не печатает"""
        out = subprocess.run([sys.executable, "-c", "import main"], cwd=HERE,
                             capture_output=True, text=True, check=True).stdout
        self.assertEqual(out, "")

    def test_readme_matches_program(self):
        """Трассировка в README совпадает с фактическим выводом программы"""
        with open(os.path.join(HERE, "README.md"), encoding="utf-8") as f:
            readme = f.read()
        self.assertIn(run(fibonacci, 4)[1], readme)


if __name__ == "__main__":
    unittest.main()
