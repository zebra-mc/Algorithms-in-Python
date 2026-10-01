"""Тесты к задаче 1 "Two sum". Запуск: python -m unittest -v"""

import io
import random
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch

from main import (count_pairs, main, parse_number, parse_numbers, read_number,
                  read_numbers, trace, two_sum)


def naive_pairs(arr, k):
    """Независимый оракул: все пары i < j с суммой k полным перебором."""
    return [(i, j)
            for i in range(len(arr))
            for j in range(i + 1, len(arr))
            if arr[i] + arr[j] == k]


def random_unique_case(rnd):
    """Случайный массив и k, для которых пара ровно одна (по оракулу)."""
    while True:
        arr = [rnd.randint(-30, 30) for _ in range(rnd.randint(2, 12))]
        a, b = sorted(rnd.sample(range(len(arr)), 2))
        k = arr[a] + arr[b]
        pairs = naive_pairs(arr, k)
        if len(pairs) == 1:
            return arr, k, pairs[0]


class TestTwoSum(unittest.TestCase):

    def test_examples(self):
        """Примеры из условия"""
        self.assertEqual(two_sum([1, 3, 4, 10], 7), (1, 2))
        self.assertEqual(two_sum([5, 5, 1, 4], 10), (0, 1))

    def test_two_elements(self):
        """Граница: минимальный массив"""
        self.assertEqual(two_sum([2, 3], 5), (0, 1))
        self.assertEqual(two_sum([-4, 4], 0), (0, 1))

    def test_not_same_element(self):
        """Элемент не складывается сам с собой"""
        self.assertEqual(two_sum([3, 2, 4], 6), (1, 2))    # 3 + 3 = 6, но тройка одна
        self.assertIsNone(two_sum([5, 1, 4], 10))

    def test_pair_position(self):
        """Пара в начале, в конце и на краях массива"""
        self.assertEqual(two_sum([1, 2, 10, 20, 30], 3), (0, 1))
        self.assertEqual(two_sum([10, 20, 30, 1, 2], 3), (3, 4))
        self.assertEqual(two_sum([1, 10, 20, 30, 2], 3), (0, 4))

    def test_order(self):
        """Индексы по возрастанию, даже если меньшее число стоит правее"""
        self.assertEqual(two_sum([9, 1, 20], 10), (0, 1))
        self.assertEqual(two_sum([1, 20, 9], 10), (0, 2))

    def test_negative_and_zero(self):
        """Отрицательные числа, нули, отрицательное k"""
        self.assertEqual(two_sum([-3, 7, 0, -5], -5), (2, 3))
        self.assertEqual(two_sum([-1, -2, -3, -4], -7), (2, 3))
        self.assertEqual(two_sum([0, 4, 0], 0), (0, 2))

    def test_duplicates_outside_answer(self):
        """Повторы значений, которые в ответ не входят"""
        self.assertEqual(two_sum([7, 2, 7, -3, 11, 5], 8), (3, 4))   # пример из README
        self.assertEqual(two_sum([1, 4, 4, 9], 10), (0, 3))         # 4 + 4 = 8, не мешают
        self.assertEqual(two_sum([6, 6, 6, 1, 3], 4), (3, 4))

    def test_big_numbers(self):
        """Длинная арифметика, переполнения нет"""
        self.assertEqual(two_sum([10 ** 18, 5, 10 ** 18 + 1], 2 * 10 ** 18 + 1), (0, 2))

    def test_equal_hashes(self):
        """Разные числа с одинаковым hash() (-1 и -2, x и x + 2^61 - 1) не путаются"""
        self.assertEqual(hash(-1), hash(-2))
        self.assertEqual(two_sum([-1, 5, -2], 3), (1, 2))
        m = 2 ** 61 - 1
        self.assertEqual(two_sum([0, m, 2 * m, 1], 2 * m + 1), (2, 3))

    def test_big_input(self):
        """n = 100 000, пара только на последнем шаге"""
        n = 100_000
        arr = list(range(0, 2 * n, 2))
        arr[-1] = 1                      # единственное нечетное число
        k = arr[-2] + 1                  # нечетная сумма возможна только с 1
        self.assertEqual(two_sum(arr, k), (n - 2, n - 1))

    def test_input_not_modified(self):
        """Функция не меняет массив и работает с любым последовательным типом"""
        arr = [7, 2, 7, -3, 11, 5]
        copy = arr[:]
        two_sum(arr, 8)
        self.assertEqual(arr, copy)
        self.assertEqual(two_sum(tuple(arr), 8), (3, 4))

    def test_against_oracle(self):
        """Сверка с перебором всех пар на 500 случайных входах с единственной парой"""
        rnd = random.Random(42)
        for _ in range(500):
            arr, k, expected = random_unique_case(rnd)
            self.assertEqual(two_sum(arr, k), expected, (arr, k))

    def test_invariants(self):
        """На длинных случайных массивах: 0 <= i < j < n и сумма равна k"""
        rnd = random.Random(7)
        for _ in range(200):
            arr = [rnd.randint(-10 ** 6, 10 ** 6) for _ in range(rnd.randint(2, 500))]
            k = sum(rnd.sample(arr, 2))
            result = two_sum(arr, k)
            self.assertIsNotNone(result, (arr, k))
            i, j = result
            self.assertTrue(0 <= i < j < len(arr), (arr, k))
            self.assertEqual(arr[i] + arr[j], k, (arr, k))


class TestCountPairs(unittest.TestCase):

    def test_values(self):
        """Ручные случаи, в том числе C(3, 2) = 3 пары из одинаковых чисел"""
        self.assertEqual(count_pairs([1, 3, 4, 10], 7), 1)
        self.assertEqual(count_pairs([5, 5, 1, 4], 10), 1)
        self.assertEqual(count_pairs([1, 2, 3], 100), 0)
        self.assertEqual(count_pairs([1, 6, 2, 5], 7), 2)
        self.assertEqual(count_pairs([2, 2, 2], 4), 3)
        self.assertEqual(count_pairs([5], 10), 0)
        self.assertEqual(count_pairs([], 0), 0)

    def test_against_oracle(self):
        """Сверка с перебором на 500 случайных массивах с большим числом повторов"""
        rnd = random.Random(1)
        for _ in range(500):
            arr = [rnd.randint(-5, 5) for _ in range(rnd.randint(0, 15))]
            k = rnd.randint(-10, 10)
            self.assertEqual(count_pairs(arr, k), len(naive_pairs(arr, k)), (arr, k))


class TestReadmeExample(unittest.TestCase):

    def test_states(self):
        """Шаги совпадают с таблицами визуализации в README"""
        self.assertEqual(trace([7, 2, 7, -3, 11, 5], 8), [
            (0, 7, 1, {7: 0}, None),
            (1, 2, 6, {7: 0, 2: 1}, None),
            (2, 7, 1, {7: 2, 2: 1}, None),                  # индекс семерки обновился
            (3, -3, 11, {7: 2, 2: 1, -3: 3}, None),
            (4, 11, -3, {7: 2, 2: 1, -3: 3}, 3),            # до элемента 5 не доходим
        ])
        self.assertEqual(trace([5, 5, 1, 4], 10), [
            (0, 5, 5, {5: 0}, None),
            (1, 5, 5, {5: 0}, 0),
        ])

    def test_trace_invariants(self):
        """В seen только индексы левее текущего, и trace заканчивается ответом two_sum"""
        rnd = random.Random(3)
        for _ in range(300):
            arr, k, expected = random_unique_case(rnd)
            steps = trace(arr, k)
            for i, x, need, seen, found in steps:
                self.assertEqual(need, k - x, (arr, k))
                self.assertTrue(all(0 <= j <= i for j in seen.values()), (arr, k))
                self.assertTrue(all(arr[j] == v for v, j in seen.items()), (arr, k))
            last = steps[-1]
            self.assertEqual((last[4], last[0]), expected, (arr, k))
            self.assertEqual((last[4], last[0]), two_sum(arr, k), (arr, k))


class TestInput(unittest.TestCase):

    def run_main(self, lines):
        """Запускает main с подмененным вводом и возвращает напечатанное."""
        out = io.StringIO()
        with patch("builtins.input", side_effect=lines), redirect_stdout(out):
            main()
        return out.getvalue()

    def test_parse_numbers(self):
        """Разбор строки: нормальный ввод и мусор"""
        self.assertEqual(parse_numbers("1 3 4 10"), [1, 3, 4, 10])
        self.assertEqual(parse_numbers("  -3   0 7 "), [-3, 0, 7])
        for bad in ["", "   ", "1 x 3", "1 2.5", "--1", "-", "+5", "1_000", "²"]:
            self.assertIsNone(parse_numbers(bad), bad)

    def test_parse_number(self):
        """Ровно одно целое число"""
        self.assertEqual(parse_number(" -7 "), -7)
        for bad in ["", "7 8", "x"]:
            self.assertIsNone(parse_number(bad), bad)

    def test_read_numbers(self):
        """read_numbers и read_number берут строку из input и разбирают ее"""
        cases = {
            "1 3 4 10": ([1, 3, 4, 10], None),
            "-7": ([-7], -7),
            "": (None, None),
            "1 x": (None, None),
        }
        for text, (numbers, number) in cases.items():
            with patch("builtins.input", return_value=text):
                self.assertEqual(read_numbers("> "), numbers, text)
                self.assertEqual(read_number("> "), number, text)

    def test_main(self):
        """Запуск программы на примерах из условия"""
        self.assertEqual(self.run_main(["1 3 4 10", "7"]), "1, 2\n")
        self.assertEqual(self.run_main(["5 5 1 4", "10"]), "0, 1\n")

    def test_main_bad_input(self):
        """Некорректный ввод: сообщение вместо исключения"""
        cases = [
            ["1 x", "7"],               # мусор в массиве, k уже не спрашиваем
            ["1 3 4 10", "7 8"],        # k не одно число
            ["1 2 3", "100"],           # пар нет
            ["1 6 2 5", "7"],           # пар две
        ]
        for lines in cases:
            self.assertTrue(self.run_main(lines).startswith("Некорректный ввод"), lines)


if __name__ == "__main__":
    unittest.main()
