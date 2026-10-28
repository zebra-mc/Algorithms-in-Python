"""Тесты к задаче 2 "Validate BST". Запуск: python -m unittest -v"""

import importlib
import io
import os
import random
import subprocess
import sys
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch

import main as main_module
from main import TreeNode, check_steps, is_valid_bst
from main import (build_tree, build_tree_bfs, explain, find_path, format_path, main,
                  node_prompt, parse_value, read_tree, render_tree)

N = TreeNode


def readme_tree():
    """Дерево из визуализации в README: 16 нарушает границу, заданную корнем 15."""
    return N(15,
             N(8, N(4), N(12, N(10), N(16))),
             N(23, N(17), N(30)))


def readme_dup_tree():
    """Дерево из задачи 1 (вставки 41 20 65 11 29 91 32 72 26 29): второе 29 под 32."""
    return N(41,
             N(20, N(11), N(29, N(26), N(32, N(29)))),
             N(65, None, N(91, N(72))))


def readme_bad_dup_tree():
    """То же дерево, но второе 29 – правый ребенок 26, то есть в левом поддереве первого 29."""
    return N(41,
             N(20, N(11), N(29, N(26, None, N(29)), N(32))),
             N(65, None, N(91, N(72))))


def nodes(root):
    """Все узлы дерева в прямом порядке (рекурсия, только для небольших деревьев)."""
    if root is None:
        return []
    return [root] + nodes(root.left) + nodes(root.right)


def values(root):
    return [node.value for node in nodes(root)]


def oracle(root):
    """Независимый эталон прямо по определению left < node <= right, O(n^2):
    для каждого узла сравниваем его со всеми значениями левого и правого поддеревьев."""
    return all(all(v < node.value for v in values(node.left)) and
               all(v >= node.value for v in values(node.right))
               for node in nodes(root))


def inorder_oracle(root):
    """Второй эталон: симметричный обход должен не убывать, а перед узлом с левым
    поддеревом стоит максимум этого поддерева, и он должен быть строго меньше узла."""
    def inorder(node):
        if node is None:
            return []
        return inorder(node.left) + [(node.value, node.left is not None)] + inorder(node.right)
    seq = inorder(root)
    return all(a < b if has_left else a <= b
               for (a, _), (b, has_left) in zip(seq, seq[1:]))


def parents_only(root):
    """Ошибочная проверка: каждый узел сравнивается только со своими детьми."""
    return all((node.left is None or node.left.value < node.value) and
               (node.right is None or node.right.value >= node.value)
               for node in nodes(root))


def insert(root, value):
    """Вставка в BST как в задаче 1 (равные вправо), нужна для генерации корректных деревьев."""
    if root is None:
        return N(value)
    node = root
    while True:
        if value < node.value:
            if node.left is None:
                node.left = N(value)
                return root
            node = node.left
        else:
            if node.right is None:
                node.right = N(value)
                return root
            node = node.right


def random_bst(rnd, size, lo=-50, hi=50):
    root = None
    for value in rnd.sample(range(lo, hi + 1), size):
        root = insert(root, value)
    return root


def random_tree(rnd, size, lo=-10, hi=10):
    """Произвольное бинарное дерево случайной формы со случайными значениями."""
    if size == 0:
        return None
    left_size = rnd.randint(0, size - 1)
    return N(rnd.randint(lo, hi),
             random_tree(rnd, left_size, lo, hi),
             random_tree(rnd, size - 1 - left_size, lo, hi))


def chain(vals, side):
    """Цепочка узлов только из левых или только из правых детей, без рекурсии."""
    root = node = N(vals[0])
    for v in vals[1:]:
        child = N(v)
        setattr(node, side, child)
        node = child
    return root, node


def snapshot(root):
    """Структура дерева: для каждого узла сам объект, значение и объекты детей."""
    return [(node, node.value, node.left, node.right) for node in nodes(root)]


class TestBasic(unittest.TestCase):

    def test_empty(self):
        self.assertIs(is_valid_bst(None), True)

    def test_single(self):
        self.assertIs(is_valid_bst(N(7)), True)

    def test_two_nodes(self):
        self.assertIs(is_valid_bst(N(5, N(3))), True)
        self.assertIs(is_valid_bst(N(5, None, N(8))), True)
        self.assertIs(is_valid_bst(N(5, N(8))), False)
        self.assertIs(is_valid_bst(N(5, None, N(3))), False)

    def test_valid_multilevel(self):
        tree = N(8, N(3, N(1), N(6, N(4), N(7))), N(10, None, N(14, N(13))))
        self.assertIs(is_valid_bst(tree), True)

    def test_violation_at_root(self):
        self.assertIs(is_valid_bst(N(10, N(12), N(15))), False)
        self.assertIs(is_valid_bst(N(10, N(5), N(7))), False)

    def test_deep_left_violation(self):
        # 9 больше родителя 6, но лежит в левом поддереве узла 8
        tree = N(20, N(8, N(3, N(1), N(6, None, N(9))), N(12)), N(30))
        self.assertIs(is_valid_bst(tree), False)

    def test_deep_right_violation(self):
        tree = N(20, N(10), N(30, N(25, N(19), N(27)), N(40)))
        self.assertIs(is_valid_bst(tree), False)

    def test_unbalanced_valid(self):
        tree = N(1, None, N(5, N(2, None, N(4, N(3))), N(9, N(7, N(6)))))
        self.assertIs(is_valid_bst(tree), True)

    def test_readme_examples(self):
        self.assertIs(is_valid_bst(readme_tree()), False)
        good = N(8, N(3, N(1), N(6)), N(10, None, N(14)))
        self.assertIs(is_valid_bst(good), True)


class TestAncestors(unittest.TestCase):
    """Деревья, на которых сравнение только с родителем ошибается."""

    CASES = [
        # 6 меньше родителя 15, но лежит в правом поддереве корня 10
        N(10, N(5), N(15, N(6))),
        # симметрично: 12 больше родителя 5, но лежит в левом поддереве 10
        N(10, N(5, None, N(12)), N(15)),
        # пример из условия: 6 и 20 под 15
        N(10, N(5), N(15, N(6), N(20))),
        # граница от корня проходит через три уровня
        N(50, N(30, N(20), N(40, N(35), N(45, None, N(55)))), N(70)),
        N(50, N(30), N(70, N(60, N(55, N(45)), N(65)), N(80))),
        # граница не от корня, а от промежуточного предка
        N(100, N(50, N(20, None, N(30, None, N(60))), N(70)), N(150)),
        readme_tree(),
    ]

    def test_parent_check_is_not_enough(self):
        for tree in self.CASES:
            self.assertTrue(parents_only(tree), values(tree))
            self.assertFalse(oracle(tree), values(tree))
            self.assertIs(is_valid_bst(tree), False, values(tree))

    def test_value_equal_to_ancestor(self):
        # 10 справа от 5 корректно относительно родителя, но лежит в левом поддереве
        # корня 10, где равные запрещены
        self.assertIs(is_valid_bst(N(10, N(5, None, N(10)))), False)
        # 10 слева от 15 и в правом поддереве корня 10, где равные разрешены
        self.assertIs(is_valid_bst(N(10, None, N(15, N(10)))), True)


class TestEdgeCases(unittest.TestCase):

    def test_negative_and_zero(self):
        self.assertIs(is_valid_bst(N(0, N(-5, N(-10), N(-1)), N(3))), True)
        self.assertIs(is_valid_bst(N(0, N(-5, None, N(1)), N(3))), False)
        self.assertIs(is_valid_bst(N(-3, N(-7), N(0))), True)

    def test_big_numbers(self):
        big = 10 ** 30
        self.assertIs(is_valid_bst(N(0, N(-big, None, N(-big + 1)), N(big, N(big - 1)))), True)
        self.assertIs(is_valid_bst(N(0, N(-big), N(big, N(-1)))), False)
        self.assertIs(is_valid_bst(N(sys.maxsize, N(-sys.maxsize - 1), N(sys.maxsize + 1))), True)

    def test_chains(self):
        left, _ = chain([5, 4, 3, 2, 1], "left")
        right, _ = chain([1, 2, 3, 4, 5], "right")
        self.assertIs(is_valid_bst(left), True)
        self.assertIs(is_valid_bst(right), True)
        bad_left, _ = chain([5, 4, 6, 3], "left")
        bad_right, _ = chain([1, 3, 2, 4], "right")
        self.assertIs(is_valid_bst(bad_left), False)
        self.assertIs(is_valid_bst(bad_right), False)

    def test_zigzag(self):
        # сильно несбалансированное дерево: путь вправо-влево-вправо-влево
        tree = N(0, None, N(100, N(10, None, N(90, N(20, None, N(80))))))
        self.assertIs(is_valid_bst(tree), True)
        tree.right.left.right.left.right.value = 95   # 95 в левом поддереве узла 90
        self.assertIs(is_valid_bst(tree), False)

    def test_deeper_than_recursion_limit(self):
        n = 3 * sys.getrecursionlimit()
        right, last = chain(list(range(0, 10 * n, 10)), "right")
        self.assertIs(is_valid_bst(right), True)
        # 5 меньше родителя, как и положено левому ребенку, но меньше и предпоследнего узла
        last.left = N(5)
        self.assertIs(is_valid_bst(right), False)
        last.left.value = 10 * n - 15
        self.assertIs(is_valid_bst(right), True)

        left, _ = chain(list(range(n, 0, -1)), "left")
        self.assertIs(is_valid_bst(left), True)

    def test_deep_bounds_inclusive_and_exclusive(self):
        # длинная правая цепочка 0, 10, ..., 10 * (n - 1); левый ребенок последнего узла
        # получает интервал [10n - 20, 10n - 10): нижняя граница от предпоследнего узла
        # нестрогая, верхняя от родителя строгая
        n = 3 * sys.getrecursionlimit()
        right, last = chain(list(range(0, 10 * n, 10)), "right")
        last.left = N(10 * n - 20)
        self.assertIs(is_valid_bst(right), True)     # равно далекому предку справа
        last.left.value = 10 * n - 21
        self.assertIs(is_valid_bst(right), False)
        last.left.value = 10 * n - 10
        self.assertIs(is_valid_bst(right), False)    # равно родителю, но слева


class TestDuplicates(unittest.TestCase):
    """Единое с задачей 1 определение: left < node <= right относительно всех предков."""

    def test_duplicate_right_of_root(self):
        self.assertIs(is_valid_bst(N(5, None, N(5))), True)
        self.assertIs(is_valid_bst(N(5, N(3), N(5))), True)

    def test_duplicate_left_of_root(self):
        self.assertIs(is_valid_bst(N(5, N(5))), False)
        self.assertIs(is_valid_bst(N(5, N(5), N(8))), False)

    def test_right_chain_of_equal_values(self):
        same, _ = chain([7] * 6, "right")
        self.assertIs(is_valid_bst(same), True)
        # то же самое, что дает вставка 7 7 7 ... в задаче 1
        root = None
        for _ in range(6):
            root = insert(root, 7)
        self.assertEqual(values(root), values(same))
        self.assertIs(is_valid_bst(root), True)
        # цепочки с равными значениями и ростом: 1 1 2 2 2 3
        mixed, _ = chain([1, 1, 2, 2, 2, 3], "right")
        self.assertIs(is_valid_bst(mixed), True)

    def test_left_chain_of_equal_values(self):
        same, _ = chain([7] * 3, "left")
        self.assertIs(is_valid_bst(same), False)
        # равные слева запрещены, даже если где-то по пути значения убывают
        self.assertIs(is_valid_bst(chain([5, 4, 4], "left")[0]), False)

    def test_nested_duplicates_allowed(self):
        # повтор у соседних узлов глубоко в дереве: 15 справа от 15
        self.assertIs(is_valid_bst(N(20, N(10, N(5), N(15, N(12), N(15))), N(30))), True)
        # 25 слева от 28: в правом поддереве первого 25 (25 >= 25) и левом 28 (25 < 28)
        self.assertIs(is_valid_bst(N(20, N(10), N(30, N(25, None, N(28, N(25)))))), True)
        # повтор корня в правом поддереве, но не у правого ребенка: 5 слева от 8
        self.assertIs(is_valid_bst(N(5, None, N(8, N(5)))), True)
        # дерево, построенное вставками из задачи 1
        self.assertIs(is_valid_bst(readme_dup_tree()), True)

    def test_nested_duplicates_violate_ancestor(self):
        # 5 справа от 3 (с родителем все верно), но в левом поддереве корня 5
        self.assertIs(is_valid_bst(N(5, N(3, None, N(5)))), False)
        # 29 справа от 26, но в левом поддереве первого 29
        self.assertIs(is_valid_bst(readme_bad_dup_tree()), False)
        # 10 равно корню и лежит в его правом поддереве (это можно), но при этом
        # слева от другого 10 (это нельзя)
        self.assertIs(is_valid_bst(N(10, None, N(15, N(10, N(10))))), False)
        self.assertIs(is_valid_bst(N(10, None, N(15, N(10, None, N(10))))), True)
        # повтор корня на глубине 4: слева запрещен, справа разрешен
        self.assertIs(is_valid_bst(N(50, N(30, None, N(40, None, N(45, None, N(50)))))), False)
        self.assertIs(is_valid_bst(N(50, None, N(70, N(60, N(55, N(50)))))), True)

    def test_duplicate_breaks_upper_bound_of_far_ancestor(self):
        # 15 справа от 15 – с родителем все верно, но оба 15 в левом поддереве 15 повыше
        self.assertIs(is_valid_bst(N(15, N(10, None, N(15, None, N(15))))), False)
        # правая цепочка равных в левом поддереве корня допустима, пока значения
        # меньше корня; узел, равный корню, ее ломает
        tree = N(20, N(10, None, N(19, None, N(19))))
        self.assertIs(is_valid_bst(tree), True)
        tree.left.right.right.right = N(20)
        self.assertIs(is_valid_bst(tree), False)

    def test_parent_check_is_not_enough_with_duplicates(self):
        for tree in [N(5, N(3, None, N(5))), readme_bad_dup_tree(),
                     N(15, N(10, None, N(15, None, N(15)))),
                     N(50, N(30, None, N(40, None, N(45, None, N(50)))))]:
            self.assertTrue(parents_only(tree), values(tree))
            self.assertFalse(oracle(tree), values(tree))
            self.assertIs(is_valid_bst(tree), False, values(tree))

    def test_empty_single_no_duplicates(self):
        self.assertIs(is_valid_bst(None), True)
        self.assertIs(is_valid_bst(N(5)), True)
        self.assertIs(is_valid_bst(N(8, N(3, N(1), N(6)), N(10, None, N(14)))), True)


class TestNoSideEffects(unittest.TestCase):

    def test_tree_not_modified(self):
        for tree in [readme_tree(), N(8, N(3, N(1), N(6)), N(10, None, N(14))), N(5, N(5))]:
            before = snapshot(tree)
            is_valid_bst(tree)
            after = snapshot(tree)
            self.assertEqual(len(before), len(after))
            for (n1, v1, l1, r1), (n2, v2, l2, r2) in zip(before, after):
                self.assertIs(n1, n2)
                self.assertEqual(v1, v2)
                self.assertIs(l1, l2)
                self.assertIs(r1, r2)

    def test_repeated_and_interleaved_calls(self):
        good = N(8, N(3, N(1), N(6)), N(10, None, N(14)))
        bad = readme_tree()
        for _ in range(3):
            self.assertIs(is_valid_bst(good), True)
            self.assertIs(is_valid_bst(bad), False)
            self.assertIs(is_valid_bst(None), True)

    def test_unfinished_generator_does_not_leak(self):
        # недочитанный генератор не влияет на последующие проверки
        steps = check_steps(readme_tree())
        next(steps)
        self.assertIs(is_valid_bst(N(2, N(1), N(3))), True)
        self.assertIs(is_valid_bst(readme_tree()), False)


class TestRandom(unittest.TestCase):

    def test_random_bst(self):
        """Корректные BST из случайных вставок, в том числе с отрицательными числами"""
        rnd = random.Random(42)
        for _ in range(300):
            tree = random_bst(rnd, rnd.randint(1, 30))
            self.assertTrue(oracle(tree))
            self.assertIs(is_valid_bst(tree), True, values(tree))

    def test_random_bst_with_duplicates(self):
        """Деревья из вставок задачи 1 с большим числом повторов всегда корректны"""
        rnd = random.Random(11)
        for _ in range(300):
            root = None
            for value in rnd.choices(range(-5, 6), k=rnd.randint(1, 30)):
                root = insert(root, value)
            self.assertTrue(oracle(root))
            self.assertTrue(inorder_oracle(root))
            self.assertIs(is_valid_bst(root), True, values(root))

    def test_random_bst_with_mutation(self):
        """В корректном BST меняем одно значение, ответ определяет эталон, а не предположение"""
        rnd = random.Random(7)
        broken = 0
        for _ in range(500):
            tree = random_bst(rnd, rnd.randint(2, 25))
            rnd.choice(nodes(tree)).value = rnd.randint(-60, 60)
            expected = oracle(tree)
            broken += not expected
            self.assertIs(is_valid_bst(tree), expected, values(tree))
        self.assertGreater(broken, 100)   # некорректные деревья действительно встречаются

    def test_random_trees(self):
        """Произвольные деревья, маленький диапазон значений – много повторов"""
        rnd = random.Random(1)
        for _ in range(2000):
            tree = random_tree(rnd, rnd.randint(0, 9), -4, 4)
            expected = oracle(tree)
            self.assertEqual(expected, inorder_oracle(tree))
            self.assertIs(is_valid_bst(tree), expected, values(tree))

    def test_steps_invariants(self):
        """Каждый узел проверяется не больше одного раза, ok соответствует границам,
        при ответе True обойдены все узлы, ответ совпадает с последним шагом"""
        rnd = random.Random(3)
        for _ in range(500):
            tree = random_tree(rnd, rnd.randint(1, 12), -20, 20)
            steps = list(check_steps(tree))
            visited = [node for node, _, _, _ in steps]
            self.assertEqual(len(set(map(id, visited))), len(visited))
            for node, low, high, ok in steps[:-1]:
                self.assertTrue(ok)
            node, low, high, ok = steps[-1]
            self.assertEqual(ok, (low is None or low <= node.value) and
                             (high is None or node.value < high))
            self.assertIs(is_valid_bst(tree), ok)
            if ok:
                self.assertEqual(len(visited), len(nodes(tree)))


class TestReadmeTrace(unittest.TestCase):

    def test_invalid_tree_steps(self):
        """Таблица шагов из README для некорректного дерева"""
        steps = [(node.value, low, high, ok) for node, low, high, ok in check_steps(readme_tree())]
        self.assertEqual(steps, [
            (15, None, None, True),
            (8, None, 15, True),
            (4, None, 8, True),
            (12, 8, 15, True),
            (10, 8, 12, True),
            (16, 12, 15, False),     # 23, 17, 30 уже не проверяются
        ])

    def test_valid_tree_steps(self):
        """Границы узлов корректного дерева из README"""
        good = N(8, N(3, N(1), N(6)), N(10, None, N(14)))
        steps = [(node.value, low, high, ok) for node, low, high, ok in check_steps(good)]
        self.assertEqual(steps, [
            (8, None, None, True),
            (3, None, 8, True),
            (1, None, 3, True),
            (6, 3, 8, True),
            (10, 8, None, True),
            (14, 10, None, True),
        ])

    def test_duplicate_tree_steps(self):
        """Границы узлов дерева с повтором из README (дерево задачи 1)"""
        steps = [(node.value, low, high, ok) for node, low, high, ok in check_steps(readme_dup_tree())]
        self.assertEqual(steps, [
            (41, None, None, True),
            (20, None, 41, True),
            (11, None, 20, True),
            (29, 20, 41, True),
            (26, 20, 29, True),
            (32, 29, 41, True),
            (29, 29, 32, True),      # 29 <= 29 < 32: нижняя граница нестрогая
            (65, 41, None, True),
            (91, 65, None, True),
            (72, 65, 91, True),
        ])

    def test_bad_duplicate_tree_steps(self):
        """Таблица шагов из README для дерева, где повтор нарушает строгую границу предка"""
        steps = [(node.value, low, high, ok)
                 for node, low, high, ok in check_steps(readme_bad_dup_tree())]
        self.assertEqual(steps, [
            (41, None, None, True),
            (20, None, 41, True),
            (11, None, 20, True),
            (29, 20, 41, True),
            (26, 20, 29, True),
            (29, 26, 29, False),     # 29 < 29 неверно; 32, 65, 91, 72 не проверяются
        ])


# ---------------------------------------------------------------------------
# Интерактивный режим: построение дерева, рисунок, ввод с клавиатуры
# ---------------------------------------------------------------------------

def run_session(lines, argv=()):
    """Запускает main с подмененным input и возвращает (вывод, запросы input)."""
    out = io.StringIO()
    with patch("builtins.input", side_effect=list(lines)) as fake_input, redirect_stdout(out):
        main(list(argv))
    prompts = [call.args[0] for call in fake_input.call_args_list]
    return out.getvalue(), prompts


def session_result(lines):
    """Ответ, который main напечатал после "Результат проверки: "."""
    output, _ = run_session(lines)
    marker = "Результат проверки: "
    return output.split(marker, 1)[1].split("\n", 1)[0]


def same_shape(a, b):
    """Одинаковые структура и значения двух деревьев (без рекурсии)."""
    stack = [(a, b)]
    while stack:
        x, y = stack.pop()
        if (x is None) != (y is None):
            return False
        if x is not None:
            if x.value != y.value:
                return False
            stack += [(x.left, y.left), (x.right, y.right)]
    return True


EXAMPLE_SESSION = ["10", "5", "15", "-", "-", "6", "20", "-", "-", "-", "-"]

EXAMPLE_PICTURE = (" _10___\n"
                   "/      \\\n"
                   "5     _15_\n"
                   "     /    \\\n"
                   "     6    20")


class TestParseValue(unittest.TestCase):

    def test_integers(self):
        for text, value in [("10", 10), ("0", 0), ("-7", -7), ("  42  ", 42), ("-0", 0),
                            (str(10 ** 30), 10 ** 30), ("\t-3\n", -3)]:
            self.assertEqual(parse_value(text), value, text)

    def test_no_node(self):
        self.assertIsNone(parse_value("-"))
        self.assertIsNone(parse_value("  -  "))

    def test_bad_input(self):
        for text in ["", "   ", "abc", "3.5", "1e3", "--", "- 5", "1 2", "5-", "²", "None", "+"]:
            with self.assertRaises(ValueError, msg=text):
                parse_value(text)

    def test_error_message_names_input(self):
        with self.assertRaises(ValueError) as ctx:
            parse_value("abc")
        self.assertIn("'abc'", str(ctx.exception))
        with self.assertRaises(ValueError) as ctx:
            parse_value("")
        self.assertIn("пустая строка", str(ctx.exception))


class TestBuildTree(unittest.TestCase):
    """Дерево строится ровно таким, как задано: без insert() и любых перестановок."""

    def test_empty(self):
        self.assertIsNone(build_tree([]))
        self.assertIsNone(build_tree([None]))
        self.assertIs(is_valid_bst(build_tree([])), True)

    def test_single(self):
        root = build_tree([7])
        self.assertTrue(same_shape(root, N(7)))

    def test_example_from_task(self):
        root = build_tree([10, 5, 15, None, None, 6, 20])
        self.assertTrue(same_shape(root, N(10, N(5), N(15, N(6), N(20)))))
        self.assertIs(is_valid_bst(root), False)

    def test_non_bst_kept_as_is(self):
        # insert() из задачи 1 положил бы 12 вправо от 10; здесь 12 остается слева
        root = build_tree([10, 12])
        self.assertEqual(root.left.value, 12)
        self.assertIsNone(root.right)
        self.assertIs(is_valid_bst(root), False)

    def test_duplicates_both_sides(self):
        root = build_tree([5, 5, 5])
        self.assertTrue(same_shape(root, N(5, N(5), N(5))))

    def test_readme_trees(self):
        self.assertTrue(same_shape(build_tree([15, 8, 23, 4, 12, 17, 30, None, None, 10, 16]),
                                   readme_tree()))
        self.assertTrue(same_shape(
            build_tree([41, 20, 65, 11, 29, None, 91, None, None, 26, 32, 72, None,
                        None, None, 29]),
            readme_dup_tree()))

    def test_extra_values(self):
        with self.assertRaises(ValueError):
            build_tree([None, 5])
        with self.assertRaises(ValueError):
            build_tree([1, None, None, 2])
        # лишние None в конце не мешают
        self.assertTrue(same_shape(build_tree([1, None, None, None]), N(1)))

    def test_random_round_trip(self):
        """Дерево -> список по уровням -> дерево дает то же самое дерево."""
        rnd = random.Random(5)
        for _ in range(300):
            tree = random_tree(rnd, rnd.randint(0, 15), -9, 9)
            order, queue = [], [tree]
            for node in queue:                       # список по уровням с None
                order.append(None if node is None else node.value)
                if node is not None:
                    queue += [node.left, node.right]
            rebuilt = build_tree(order)
            self.assertTrue(same_shape(rebuilt, tree))
            self.assertIs(is_valid_bst(rebuilt), oracle(tree))

    def test_bfs_order_of_questions(self):
        asked = []

        def answer(parent, side, path):
            asked.append(None if parent is None else (parent.value, side, format_path(path)))
            return {None: 1, (1, "left"): 2, (1, "right"): 3,
                    (2, "right"): 4, (3, "left"): 5}.get(
                None if parent is None else (parent.value, side))

        build_tree_bfs(answer)
        self.assertEqual(asked, [
            None,
            (1, "left", "корень"), (1, "right", "корень"),
            (2, "left", "корень -> Л"), (2, "right", "корень -> Л"),
            (3, "left", "корень -> П"), (3, "right", "корень -> П"),
            (4, "left", "корень -> Л -> П"), (4, "right", "корень -> Л -> П"),
            (5, "left", "корень -> П -> Л"), (5, "right", "корень -> П -> Л"),
        ])

    def test_deeper_than_recursion_limit(self):
        """Построение, путь и рисунок без рекурсии: цепочка длиннее лимита рекурсии."""
        n = sys.getrecursionlimit() + 200
        right = build_tree([v for i in range(n) for v in (None, i)][1:])
        node, depth = right, 1
        while node.right is not None:
            self.assertIsNone(node.left)
            node, depth = node.right, depth + 1
        self.assertEqual(depth, n)
        self.assertIs(is_valid_bst(right), True)
        self.assertEqual(format_path(find_path(right, node)),
                         " -> ".join(["корень"] + ["П"] * (n - 1)))
        self.assertEqual(len(render_tree(right).split("\n")), 2 * n - 1)

        left = build_tree([n] + [v for i in range(n - 1, 0, -1) for v in (i, None)])
        self.assertIsNone(left.right)
        self.assertEqual(left.left.value, n - 1)
        self.assertIs(is_valid_bst(left), True)


class TestRender(unittest.TestCase):

    def test_empty(self):
        self.assertEqual(render_tree(None), "(пустое дерево)")

    def test_single(self):
        self.assertEqual(render_tree(N(7)), "7")
        self.assertEqual(render_tree(N(-15)), "-15")

    def test_example(self):
        self.assertEqual(render_tree(N(10, N(5), N(15, N(6), N(20)))), EXAMPLE_PICTURE)

    def test_left_and_right_child_differ(self):
        self.assertEqual(render_tree(N(5, N(3))), " _5\n/\n3")
        self.assertEqual(render_tree(N(5, None, N(8))), "5_\n  \\\n  8")
        self.assertNotEqual(render_tree(N(5, N(5))), render_tree(N(5, None, N(5))))

    def test_negative_and_zero(self):
        self.assertEqual(render_tree(N(0, N(-5, N(-10), N(-1)), N(3))),
                         "     _____0_\n"
                         "    /       \\\n"
                         "  __-5_     3\n"
                         " /     \\\n"
                         "-10    -1")

    def test_chains(self):
        self.assertEqual(render_tree(build_tree([3, 2, None, 1])),
                         "   _3\n  /\n _2\n/\n1")
        self.assertEqual(render_tree(build_tree([1, None, 2, None, 3])),
                         "1_\n  \\\n  2_\n    \\\n    3")

    def test_labels_do_not_overlap(self):
        """Каждое значение стоит на рисунке целиком, связи – в отдельных строках."""
        rnd = random.Random(9)
        for _ in range(300):
            tree = random_tree(rnd, rnd.randint(1, 14), -120, 120)
            lines = render_tree(tree).split("\n")
            self.assertEqual(len(lines) % 2, 1)        # подписи и связи чередуются
            labels = " ".join(lines[::2]).replace("_", " ").split()
            self.assertEqual(sorted(labels), sorted(map(str, values(tree))))
            self.assertTrue(set("".join(lines[1::2])) <= {" ", "/", "\\"})

    def test_tree_not_modified(self):
        tree = readme_tree()
        before = snapshot(tree)
        render_tree(tree)
        explain(tree)
        for (n1, v1, l1, r1), (n2, v2, l2, r2) in zip(before, snapshot(tree)):
            self.assertIs(n1, n2)
            self.assertEqual(v1, v2)
            self.assertIs(l1, l2)
            self.assertIs(r1, r2)


class TestExplain(unittest.TestCase):

    def test_empty_and_valid(self):
        self.assertIn("Пустое дерево", explain(None)[0])
        self.assertIn("является корректным BST", explain(N(7))[0])

    def test_lower_bound(self):
        lines = explain(N(10, N(5), N(15, N(6), N(20))))
        self.assertEqual(lines[0], "Дерево не является корректным BST.")
        self.assertEqual(lines[1], "Нарушение: узел 6 [корень -> П -> Л] лежит в правом "
                                   "поддереве узла 10, поэтому должен быть >= 10, а 6 < 10.")

    def test_upper_bound(self):
        self.assertIn("узел 16 [корень -> Л -> П -> П] лежит в левом поддереве узла 15",
                      explain(readme_tree())[1])

    def test_duplicate_left(self):
        line = explain(N(5, N(5)))[1]
        self.assertIn("узел 5 [корень -> Л]", line)
        self.assertIn("только в правом поддереве", line)

    def test_path_distinguishes_equal_values(self):
        # оба ребенка корня равны 5, нарушает только левый
        self.assertIn("[корень -> Л]", explain(N(5, N(5), N(5)))[1])
        # второе 29 под 26, а не первое 29
        self.assertIn("узел 29 [корень -> Л -> П -> Л -> П]", explain(readme_bad_dup_tree())[1])


class TestInteractive(unittest.TestCase):
    """Сеансы ввода через подмененный input."""

    def test_example_session(self):
        output, prompts = run_session(EXAMPLE_SESSION)
        self.assertEqual(prompts, [
            "Введите значение корня ('-' – пустое дерево): ",
            "Левый ребенок узла 10 [корень]: ",
            "Правый ребенок узла 10 [корень]: ",
            "Левый ребенок узла 5 [корень -> Л]: ",
            "Правый ребенок узла 5 [корень -> Л]: ",
            "Левый ребенок узла 15 [корень -> П]: ",
            "Правый ребенок узла 15 [корень -> П]: ",
            "Левый ребенок узла 6 [корень -> П -> Л]: ",
            "Правый ребенок узла 6 [корень -> П -> Л]: ",
            "Левый ребенок узла 20 [корень -> П -> П]: ",
            "Правый ребенок узла 20 [корень -> П -> П]: ",
        ])
        self.assertTrue(output.endswith(
            "\nПостроенное дерево:\n" + EXAMPLE_PICTURE + "\n\n"
            "Результат проверки: False\n"
            "Дерево не является корректным BST.\n"
            "Нарушение: узел 6 [корень -> П -> Л] лежит в правом поддереве узла 10, "
            "поэтому должен быть >= 10, а 6 < 10.\n"), output)

    def test_empty_tree(self):
        output, prompts = run_session(["-"])
        self.assertEqual(len(prompts), 1)
        self.assertIn("(пустое дерево)", output)
        self.assertIn("Результат проверки: True", output)
        self.assertIn("Пустое дерево считается корректным BST.", output)

    def test_single_node(self):
        output, prompts = run_session(["7", "-", "-"])
        self.assertEqual(len(prompts), 3)
        self.assertIn("Построенное дерево:\n7\n", output)
        self.assertEqual(session_result(["7", "-", "-"]), "True")

    def test_valid_bst(self):
        lines = ["8", "3", "10", "1", "6", "-", "14", "-", "-", "-", "-", "-", "-"]
        self.assertEqual(session_result(lines), "True")

    def test_ancestor_violation(self):
        # 12 правильно стоит справа от 5, но лежит в левом поддереве корня 10
        lines = ["10", "5", "15", "-", "12", "-", "-", "-", "-"]
        output, _ = run_session(lines)
        self.assertIn("Результат проверки: False", output)
        self.assertIn("узел 12 [корень -> Л -> П] лежит в левом поддереве узла 10", output)

    def test_duplicates(self):
        self.assertEqual(session_result(["5", "-", "5", "-", "-"]), "True")    # повтор справа
        self.assertEqual(session_result(["5", "5", "-", "-", "-"]), "False")   # повтор слева
        # повтор корня глубже: справа от 3 – но в левом поддереве корня 5
        self.assertEqual(session_result(["5", "3", "-", "-", "5", "-", "-"]), "False")

    def test_negative_and_zero(self):
        lines = ["0", "-5", "3", "-10", "-1", "-", "-", "-", "-", "-", "-"]
        output, _ = run_session(lines)
        self.assertIn("Результат проверки: True", output)
        self.assertIn("-10", output)
        self.assertEqual(session_result(["0", "-5", "-", "-", "1", "-", "-"]), "False")
        self.assertEqual(session_result(["-3", "-7", "0", "-", "-", "-", "-"]), "True")

    def test_bad_input_is_asked_again(self):
        lines = ["abc", "", "3.5", "10",       # корень с третьей попытки после трех ошибок
                 "5", "--", "15",              # ошибка на правом ребенке корня
                 "-", "-", "x y", "-", "-"]
        output, prompts = run_session(lines)
        self.assertEqual(output.count("Ошибка:"), 5)
        self.assertIn("Ошибка: 'abc' – не целое число и не '-'", output)
        self.assertIn("Ошибка: пустая строка", output)
        self.assertIn("Повторите ввод.", output)
        # после ошибки повторяется тот же самый запрос
        self.assertEqual(prompts[:4], [prompts[0]] * 4)
        self.assertEqual(prompts[5], prompts[6])
        self.assertEqual(prompts[5], "Правый ребенок узла 10 [корень]: ")
        self.assertIn("Результат проверки: True", output)
        self.assertIn(" _10_\n/    \\\n5    15", output)

    def test_left_only_and_right_only(self):
        left = ["5", "4", "-", "3", "-", "2", "-", "-", "-"]
        right = ["1", "-", "2", "-", "3", "-", "4", "-", "-"]
        out_left, _ = run_session(left)
        out_right, _ = run_session(right)
        self.assertIn("Результат проверки: True", out_left)
        self.assertIn("Результат проверки: True", out_right)
        self.assertIn("   _4\n  /\n _3\n/\n2", out_left)
        self.assertIn("2_\n    \\\n    3_", out_right)
        self.assertEqual(session_result(["5", "4", "-", "6", "-", "-", "-"]), "False")
        self.assertEqual(session_result(["1", "-", "3", "-", "2", "-", "-"]), "False")

    def test_prompts_unique_for_equal_values(self):
        _, prompts = run_session(["5", "5", "5", "-", "-", "-", "-"])
        self.assertEqual(len(prompts), len(set(prompts)))
        self.assertIn("Левый ребенок узла 5 [корень -> Л]: ", prompts)
        self.assertIn("Левый ребенок узла 5 [корень -> П]: ", prompts)

    def test_matches_build_tree(self):
        """Случайные деревья: сеанс ввода дает тот же ответ, что и эталон."""
        rnd = random.Random(13)
        for _ in range(200):
            tree = random_tree(rnd, rnd.randint(0, 10), -5, 5)
            answers = []
            queue = [tree]
            for node in queue:                   # ответы в порядке запросов
                answers.append("-" if node is None else str(node.value))
                if node is not None:
                    queue += [node.left, node.right]
            self.assertEqual(session_result(answers), str(oracle(tree)))

    def test_read_tree_with_custom_io(self):
        answers = iter(["2", "1", "3", "-", "-", "-", "-"])
        written = []
        root = read_tree(lambda prompt: next(answers), written.append)
        self.assertTrue(same_shape(root, N(2, N(1), N(3))))
        self.assertEqual(written, [])

    def test_interrupted_input(self):
        for error in (EOFError, KeyboardInterrupt):
            out = io.StringIO()
            with patch("builtins.input", side_effect=["10", "5", error]), redirect_stdout(out):
                main([])
            self.assertTrue(out.getvalue().endswith("\nВвод прерван.\n"))
            self.assertNotIn("Результат проверки", out.getvalue())

    def test_node_prompt(self):
        self.assertIn("корня", node_prompt(None, None, None))
        self.assertEqual(node_prompt(N(-3), "right", ((None, "left"), "right")),
                         "Правый ребенок узла -3 [корень -> Л -> П]: ")


class TestCommandLine(unittest.TestCase):

    def test_demo(self):
        output, prompts = run_session([], ["--demo"])
        self.assertEqual(output, "True\nFalse\nTrue\nFalse\n")
        self.assertEqual(prompts, [])

    def test_unknown_argument(self):
        output, prompts = run_session([], ["--help"])
        self.assertIn("python main.py --demo", output)
        self.assertEqual(prompts, [])

    def test_import_does_not_ask(self):
        with patch("builtins.input", side_effect=AssertionError("input() при импорте")):
            importlib.reload(main_module)

    def test_script_run(self):
        """Настоящий запуск python main.py и python main.py --demo."""
        here = os.path.dirname(os.path.abspath(__file__))
        env = dict(os.environ, PYTHONIOENCODING="utf-8")
        demo = subprocess.run([sys.executable, "main.py", "--demo"], cwd=here, env=env,
                              capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(demo.stdout.split(), ["True", "False", "True", "False"])
        run = subprocess.run([sys.executable, "main.py"], cwd=here, env=env,
                             input="\n".join(EXAMPLE_SESSION) + "\n",
                             capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(run.returncode, 0, run.stderr)
        self.assertIn(EXAMPLE_PICTURE, run.stdout)
        self.assertIn("Результат проверки: False", run.stdout)


if __name__ == "__main__":
    unittest.main()
