"""Тесты к задаче 3 "Balanced Binary Tree". Запуск: python -m unittest -v"""

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
from main import TreeNode as N
from main import is_balanced, postorder_heights
from main import (build_tree, build_tree_bfs, explain, find_path, first_violation, format_path,
                  main, node_prompt, parse_value, read_tree, render_tree)


def naive_height(node):
    """Высота поддерева отдельным рекурсивным обходом (пустое – 0, лист – 1)."""
    if node is None:
        return 0
    return 1 + max(naive_height(node.left), naive_height(node.right))


def nodes_of(root):
    """Все узлы дерева в порядке обхода в ширину."""
    result = [root] if root is not None else []
    for node in result:
        result.extend(c for c in (node.left, node.right) if c is not None)
    return result


def naive_balanced(root):
    """Независимый оракул: для каждого узла обе высоты считаются заново, без досрочного выхода.

    Работа пропорциональна сумме размеров всех поддеревьев, на цепочке это O(n^2).
    Используется только на небольших деревьях.
    """
    return all([abs(naive_height(n.left) - naive_height(n.right)) <= 1 for n in nodes_of(root)])


def snapshot(root):
    """Структура дерева: для каждого узла сам узел, значение и оба ребенка (по id)."""
    return [(id(n), n.val, id(n.left), id(n.right)) for n in nodes_of(root)]


def chain(n, side):
    """Цепочка из n узлов, у каждого только левый или только правый ребенок."""
    root = None
    for val in range(n):
        root = N(val, root, None) if side == "left" else N(val, None, root)
    return root


def perfect(height):
    """Полное дерево заданной высоты."""
    if height == 0:
        return None
    return N(height, perfect(height - 1), perfect(height - 1))


def fibonacci(height):
    """Сбалансированное дерево с минимумом узлов: у каждого внутреннего узла разность ровно 1."""
    if height == 0:
        return None
    if height == 1:
        return N(1)
    return N(height, fibonacci(height - 1), fibonacci(height - 2))


def all_shapes(n):
    """Все формы бинарных деревьев из n узлов (их число Каталана)."""
    if n == 0:
        return [None]
    return [N(0, left, right)
            for k in range(n)
            for left in all_shapes(k)
            for right in all_shapes(n - 1 - k)]


def random_tree(rnd, n):
    """Случайное дерево из n узлов: каждый новый узел занимает случайное свободное место.

    Свободное место – пустая ссылка уже существующего узла, поэтому получается
    именно дерево: ни циклов, ни узла с двумя родителями.
    """
    if n == 0:
        return None
    root = N(rnd.randint(-50, 50))
    free = [(root, "left"), (root, "right")]
    for _ in range(n - 1):
        parent, side = free.pop(rnd.randrange(len(free)))
        child = N(rnd.randint(-50, 50))
        setattr(parent, side, child)
        free += [(child, "left"), (child, "right")]
    return root


def random_balanced(rnd, height):
    """Случайное дерево, сбалансированное по построению: высоты детей h-1/h-1, h-1/h-2 или h-2/h-1."""
    if height <= 0:
        return None
    a, b = rnd.choice([(1, 1), (1, 2), (2, 1)])
    return N(rnd.randint(-50, 50), random_balanced(rnd, height - a), random_balanced(rnd, height - b))


# пример из README: у корня 3 и 3, нарушение в правом поддереве у узла 15 без левого ребенка
def readme_unbalanced():
    return N(10,
             N(5, N(3, N(1)), N(8)),
             N(15, None, N(18, None, N(20))))


# пример из README: не полное дерево, у каждого внутреннего узла разность ровно 1
def readme_balanced():
    return N(1,
             N(2, N(4, N(7)), N(5)),
             N(3, None, N(6)))


class TestBasic(unittest.TestCase):

    def test_empty(self):
        """Пустое дерево сбалансировано"""
        self.assertIs(is_balanced(None), True)

    def test_one_node(self):
        """Один узел: оба поддерева пустые"""
        self.assertIs(is_balanced(N(1)), True)

    def test_two_nodes(self):
        """Два узла: разность 1 с любой стороны"""
        self.assertIs(is_balanced(N(1, N(2))), True)
        self.assertIs(is_balanced(N(1, None, N(2))), True)

    def test_root_with_two_leaves(self):
        self.assertIs(is_balanced(N(1, N(2), N(3))), True)

    def test_perfect(self):
        """Полностью симметричные деревья нескольких высот"""
        for height in range(1, 8):
            self.assertIs(is_balanced(perfect(height)), True, height)

    def test_not_complete(self):
        """Сбалансированное, но не полное дерево из README"""
        self.assertIs(is_balanced(readme_balanced()), True)

    def test_fibonacci(self):
        """У каждого внутреннего узла разность ровно 1 – это допустимо"""
        for height in range(1, 12):
            self.assertIs(is_balanced(fibonacci(height)), True, height)

    def test_obviously_unbalanced(self):
        self.assertIs(is_balanced(N(1, N(2, N(3)))), False)
        self.assertIs(is_balanced(N(1, N(2, N(3), N(4)), None)), False)

    def test_difference_one_and_two(self):
        """Ровно 1 – допустимо, ровно 2 – нарушение (у корня 2 против 1 и 3 против 1)"""
        self.assertIs(is_balanced(N(1, N(2, N(3)), N(4))), True)
        self.assertIs(is_balanced(N(1, N(2, N(3, N(5)), N(6)), N(4))), False)


class TestEveryNode(unittest.TestCase):
    """У корня все в порядке, а нарушение глубже. Проверка только корня здесь ошибется."""

    def assert_root_looks_balanced(self, root):
        self.assertLessEqual(abs(naive_height(root.left) - naive_height(root.right)), 1)

    def test_task_example(self):
        """Пример из условия: у корня 3 и 3, у узла 5 – 2 и 0"""
        root = N(10, N(5, N(3, N(1))), N(15, N(12, N(11)), N(18)))
        self.assert_root_looks_balanced(root)
        self.assertIs(is_balanced(root), False)

    def test_violation_in_left(self):
        root = N(1, N(2, N(3, N(4))), N(5, N(6), N(7)))
        self.assert_root_looks_balanced(root)
        self.assertIs(is_balanced(root), False)

    def test_violation_in_right(self):
        """Левое поддерево обрабатывается первым и проходит, нарушение находится позже"""
        root = readme_unbalanced()
        self.assert_root_looks_balanced(root)
        self.assertIs(is_balanced(root), False)

    def test_violation_at_node_with_one_child(self):
        """Нарушение у узла, у которого один ребенок отсутствует (высота 0)"""
        root = N(1, N(2, N(3), N(4)), N(5, N(6, N(7), N(8)), None))
        self.assert_root_looks_balanced(root)
        self.assertIs(is_balanced(root), False)

    def test_deep_violation(self):
        """Полное дерево высоты 8: к одному листу подвешена цепочка из двух узлов,
        к листу в другой половине – один узел, чтобы у корня высоты были 10 и 9"""
        for leaf_index in (0, 60, 127):
            root = perfect(8)
            leaves = [n for n in nodes_of(root) if n.left is None and n.right is None]
            leaves[leaf_index].right = N(0, None, N(0))
            leaves[127 - leaf_index].left = N(0)
            self.assert_root_looks_balanced(root)
            self.assertIs(is_balanced(root), False, leaf_index)

    def test_two_balanced_halves_of_different_height(self):
        """Каждое поддерево сбалансировано само по себе, нарушение только у корня"""
        root = N(0, perfect(4), perfect(2))
        self.assertIs(is_balanced(root.left), True)
        self.assertIs(is_balanced(root.right), True)
        self.assertIs(is_balanced(root), False)

    def test_leaf_depths_are_not_the_criterion(self):
        """Разброс глубин листьев не равносилен балансу ни в одну сторону"""
        def leaf_depths(root):
            depths, stack = [], [(root, 1)]
            while stack:
                node, depth = stack.pop()
                if node.left is None and node.right is None:
                    depths.append(depth)
                stack += [(c, depth + 1) for c in (node.left, node.right) if c is not None]
            return depths

        fib = fibonacci(5)                     # листья на глубинах 3..5, но сбалансировано
        depths = leaf_depths(fib)
        self.assertEqual(max(depths) - min(depths), 2)
        self.assertIs(is_balanced(fib), True)

        line = chain(3, "left")                # один лист, разброс 0, но не сбалансировано
        self.assertEqual(leaf_depths(line), [3])
        self.assertIs(is_balanced(line), False)


class TestEdgeCases(unittest.TestCase):

    def test_chains(self):
        """Цепочки только из левых и только из правых детей"""
        for side in ("left", "right"):
            self.assertIs(is_balanced(chain(2, side)), True, side)
            for n in (3, 4, 50):
                self.assertIs(is_balanced(chain(n, side)), False, (side, n))

    def test_zigzag(self):
        """Ломаная цепочка: дети попеременно слева и справа"""
        root = cur = N(0)
        for i in range(1, 6):
            child = N(i)
            if i % 2:
                cur.left = child
            else:
                cur.right = child
            cur = child
        self.assertIs(is_balanced(root), False)

    def test_chain_deeper_than_recursion_limit(self):
        """Цепочка из 100 000 узлов: без RecursionError, ответ False"""
        n = 100_000
        self.assertGreater(n, sys.getrecursionlimit())
        for side in ("left", "right"):
            root = chain(n, side)
            self.assertIs(is_balanced(root), False, side)
            # нарушение находит самый нижний узел с двумя потомками в цепочке
            node, h_left, h_right = next(s for s in postorder_heights(root)
                                         if abs(s[1] - s[2]) > 1)
            self.assertEqual(sorted((h_left, h_right)), [0, 2])
            self.assertEqual(node.val, 2)

    def test_big_balanced(self):
        """Большие сбалансированные деревья"""
        self.assertIs(is_balanced(perfect(15)), True)        # 32 767 узлов
        self.assertIs(is_balanced(fibonacci(20)), True)      # 10 945 узлов, разность 1 везде
        self.assertIs(is_balanced(random_balanced(random.Random(5), 16)), True)

    def test_big_unbalanced(self):
        """Большое дерево с одним нарушением в самом последнем обработанном узле – корне"""
        root = N(0, perfect(14), perfect(12))
        self.assertIs(is_balanced(root), False)


class TestValues(unittest.TestCase):
    """Ответ зависит только от формы дерева."""

    def relabel(self, root, values):
        for node in nodes_of(root):
            node.val = next(values)

    def test_values_do_not_matter(self):
        """Одна форма с разными наборами значений: положительные, отрицательные, ноль, повторы, не BST"""
        rnd = random.Random(11)
        value_sets = [
            lambda: iter(range(1, 1000)),
            lambda: iter(range(-1, -1000, -1)),
            lambda: iter([0] * 1000),
            lambda: iter([7, 7, 3, 7, 3] * 200),
            lambda: (rnd.randint(-5, 5) for _ in range(1000)),
            lambda: iter(range(1000, 0, -1)),
        ]
        for make_tree in (readme_unbalanced, readme_balanced):
            expected = is_balanced(make_tree())
            for values in value_sets:
                root = make_tree()
                self.relabel(root, values())
                self.assertIs(is_balanced(root), expected)

    def test_incomparable_values(self):
        """Значения, которые нельзя сравнивать: алгоритм их не трогает"""
        class Opaque:
            def __eq__(self, other):
                raise AssertionError("значение сравнивали")
            __lt__ = __gt__ = __le__ = __ge__ = __eq__
            __hash__ = object.__hash__

        for make_tree in (readme_unbalanced, readme_balanced):
            root = make_tree()
            expected = is_balanced(root)
            self.relabel(root, iter([Opaque() for _ in range(20)]))
            self.assertIs(is_balanced(root), expected)

    def test_none_values(self):
        """None в значении узла – не то же, что пустое поддерево"""
        self.assertIs(is_balanced(N(None, N(None, N(None)))), False)
        self.assertIs(is_balanced(N(None, N(None), N(None))), True)


class TestNoSideEffects(unittest.TestCase):

    def test_tree_not_modified(self):
        """Узлы, значения и ссылки на детей после проверки те же"""
        rnd = random.Random(3)
        trees = [readme_unbalanced(), readme_balanced(), chain(10, "left"),
                 random_tree(rnd, 40), random_balanced(rnd, 6)]
        for root in trees:
            before = snapshot(root)
            is_balanced(root)
            self.assertEqual(snapshot(root), before)

    def test_repeated_calls(self):
        """Повторный вызов и чередование разных деревьев не влияют на ответ"""
        good, bad = readme_balanced(), readme_unbalanced()
        for _ in range(3):
            self.assertIs(is_balanced(good), True)
            self.assertIs(is_balanced(bad), False)
            self.assertIs(is_balanced(None), True)

    def test_subtree_of_unbalanced_tree(self):
        """Сбалансированное поддерево внутри несбалансированного дерева проверяется само по себе"""
        root = readme_unbalanced()
        self.assertIs(is_balanced(root), False)
        self.assertIs(is_balanced(root.left), True)
        self.assertIs(is_balanced(root.right), False)


class TestOracle(unittest.TestCase):

    def test_oracle_on_known_trees(self):
        """Сам оракул согласен с ручными примерами"""
        self.assertTrue(naive_balanced(readme_balanced()))
        self.assertFalse(naive_balanced(readme_unbalanced()))
        self.assertFalse(naive_balanced(chain(3, "right")))

    def test_all_shapes(self):
        """Все формы деревьев до 9 узлов (4862 формы при n = 9, всего 6918) против оракула"""
        for n in range(10):
            balanced_count = 0
            for root in all_shapes(n):
                expected = naive_balanced(root)
                self.assertIs(is_balanced(root), expected, n)
                balanced_count += expected
            # среди форм есть и сбалансированные, и нет – иначе перебор ничего бы не проверял
            if n >= 3:
                self.assertTrue(0 < balanced_count < len(all_shapes(n)), n)

    def test_random_trees(self):
        """1000 случайных деревьев разной формы против оракула"""
        rnd = random.Random(42)
        answers = set()
        for _ in range(1000):
            root = random_tree(rnd, rnd.randint(0, 60))
            expected = naive_balanced(root)
            self.assertIs(is_balanced(root), expected)
            answers.add(expected)
        self.assertEqual(answers, {True, False})

    def test_random_balanced_and_spoiled(self):
        """Сбалансированные по построению деревья, затем к случайному месту подвешена цепочка"""
        rnd = random.Random(7)
        for _ in range(300):
            root = random_balanced(rnd, rnd.randint(1, 8))
            self.assertIs(is_balanced(root), True)
            free = [(n, side) for n in nodes_of(root) for side in ("left", "right")
                    if getattr(n, side) is None]
            parent, side = rnd.choice(free)
            setattr(parent, side, chain(rnd.randint(1, 3), rnd.choice(["left", "right"])))
            self.assertIs(is_balanced(root), naive_balanced(root))


class TestHeights(unittest.TestCase):
    """postorder_heights: порядок обработки, высоты и отсутствие повторных вычислений."""

    def test_each_node_once_children_first(self):
        """Каждый узел выдается один раз и только после своих детей, высоты совпадают с оракулом"""
        rnd = random.Random(1)
        for _ in range(200):
            root = random_tree(rnd, rnd.randint(1, 50))
            order = [s[0] for s in postorder_heights(root)]
            position = {id(node): i for i, node in enumerate(order)}
            self.assertEqual(len(order), len(nodes_of(root)))
            self.assertEqual(len(position), len(order))
            for node, h_left, h_right in postorder_heights(root):
                self.assertEqual(h_left, naive_height(node.left))
                self.assertEqual(h_right, naive_height(node.right))
                for child in (node.left, node.right):
                    if child is not None:
                        self.assertLess(position[id(child)], position[id(node)])

    def test_linear_work(self):
        """Ссылки на детей читаются ровно 2n раз: высоты не пересчитываются заново"""
        class CountingNode(N):
            reads = 0

            def __getattribute__(self, name):
                if name in ("left", "right"):
                    CountingNode.reads += 1
                return super().__getattribute__(name)

        def counting_chain(n):
            root = None
            for _ in range(n):
                root = CountingNode(0, None, root)
            return root

        def counting_perfect(height):
            if height == 0:
                return None
            return CountingNode(0, counting_perfect(height - 1), counting_perfect(height - 1))

        for root, n in ((counting_perfect(10), 1023), (counting_chain(500), 500)):
            CountingNode.reads = 0
            list(postorder_heights(root))
            self.assertEqual(CountingNode.reads, 2 * n)

        # для сравнения: наивный оракул на той же цепочке читает ссылки квадратичное число раз
        root = counting_chain(500)
        CountingNode.reads = 0
        naive_balanced(root)
        self.assertGreater(CountingNode.reads, 500 * 500 // 2)

    def test_early_exit(self):
        """После нарушения в левом поддереве правое не обходится вовсе"""
        class Untouchable:
            def __getattr__(self, name):
                raise AssertionError("обход дошел до правого поддерева")

        root = N(0, chain(3, "left"), Untouchable())
        self.assertIs(is_balanced(root), False)


def processed_steps(root):
    """Шаги в том объеме, в котором их делает is_balanced: до первого нарушения включительно."""
    steps = []
    for node, h_left, h_right in postorder_heights(root):
        steps.append((node.val, h_left, h_right))
        if abs(h_left - h_right) > 1:
            break
    return steps


class TestReadmeExample(unittest.TestCase):

    def test_unbalanced_table(self):
        """Таблица шагов из README для несбалансированного примера"""
        self.assertEqual(processed_steps(readme_unbalanced()), [
            (1, 0, 0),
            (3, 1, 0),
            (8, 0, 0),
            (5, 2, 1),
            (20, 0, 0),
            (18, 0, 1),
            (15, 0, 2),        # нарушение, корень 10 не обрабатывается
        ])

    def test_balanced_table(self):
        """Таблица шагов из README для сбалансированного примера"""
        self.assertEqual(processed_steps(readme_balanced()), [
            (7, 0, 0),
            (4, 1, 0),
            (5, 0, 0),
            (2, 2, 1),
            (6, 0, 0),
            (3, 0, 1),
            (1, 3, 2),
        ])

    def test_root_heights_hidden_by_early_exit(self):
        """Высоты поддеревьев корня 10, которые в README даны отдельно: 3 и 3"""
        root = readme_unbalanced()
        self.assertEqual((naive_height(root.left), naive_height(root.right)), (3, 3))


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
            if x.val != y.val:
                return False
            stack += [(x.left, y.left), (x.right, y.right)]
    return True


def answers_for(tree):
    """Ответы на запросы программы, которые строят дерево tree: по уровням, '-' – узла нет."""
    answers, queue = [], [tree]
    for node in queue:
        answers.append("-" if node is None else str(node.val))
        if node is not None:
            queue += [node.left, node.right]
    return answers


def values(root):
    return [node.val for node in nodes_of(root)]


EXAMPLE_SESSION = ["10", "5", "15", "-", "-", "6", "20", "-", "-", "-", "-"]

EXAMPLE_PICTURE = (" _10___\n"
                   "/      \\\n"
                   "5     _15_\n"
                   "     /    \\\n"
                   "     6    20")

# дерево из README: у корня высоты 3 и 3, нарушение у узла 15
README_UNBALANCED_SESSION = ["10", "5", "15", "3", "8", "-", "18", "1", "-",
                             "-", "-", "-", "20", "-", "-", "-", "-"]

README_UNBALANCED_PICTURE = ("     ___10_\n"
                             "    /      \\\n"
                             "   _5_     15_\n"
                             "  /   \\       \\\n"
                             " _3   8       18_\n"
                             "/                \\\n"
                             "1                20")


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
    """Дерево строится ровно таким, как задано: без вставки по правилам BST."""

    def test_empty(self):
        self.assertIsNone(build_tree([]))
        self.assertIsNone(build_tree([None]))
        self.assertIs(is_balanced(build_tree([])), True)

    def test_single(self):
        self.assertTrue(same_shape(build_tree([7]), N(7)))

    def test_example_from_task(self):
        root = build_tree([10, 5, 15, None, None, 6, 20])
        self.assertTrue(same_shape(root, N(10, N(5), N(15, N(6), N(20)))))
        self.assertIs(is_balanced(root), True)

    def test_readme_trees(self):
        self.assertTrue(same_shape(
            build_tree([10, 5, 15, 3, 8, None, 18, 1, None, None, None, None, 20]),
            readme_unbalanced()))
        self.assertTrue(same_shape(build_tree([1, 2, 3, 4, 5, None, 6, 7]), readme_balanced()))

    def test_non_bst_kept_as_is(self):
        # вставка в BST положила бы 12 вправо от 10; здесь 12 остается слева
        root = build_tree([10, 12])
        self.assertEqual(root.left.val, 12)
        self.assertIsNone(root.right)

    def test_extra_values(self):
        with self.assertRaises(ValueError):
            build_tree([None, 5])
        with self.assertRaises(ValueError):
            build_tree([1, None, None, 2])
        self.assertTrue(same_shape(build_tree([1, None, None, None]), N(1)))

    def test_random_round_trip(self):
        """Дерево -> список по уровням -> то же самое дерево."""
        rnd = random.Random(5)
        for _ in range(300):
            tree = random_tree(rnd, rnd.randint(0, 15))
            order = [None if a == "-" else int(a) for a in answers_for(tree)]
            rebuilt = build_tree(order)
            self.assertTrue(same_shape(rebuilt, tree))
            self.assertIs(is_balanced(rebuilt), naive_balanced(tree))

    def test_bfs_order_of_questions(self):
        asked = []

        def answer(parent, side, path):
            asked.append(None if parent is None else (parent.val, side, format_path(path)))
            return {None: 1, (1, "left"): 2, (1, "right"): 3,
                    (2, "right"): 4, (3, "left"): 5}.get(
                None if parent is None else (parent.val, side))

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
        """Построение, путь, рисунок и пояснение без рекурсии на цепочке длиннее лимита."""
        n = sys.getrecursionlimit() + 200
        right = build_tree([v for i in range(n) for v in (None, i)][1:])
        node, depth = right, 1
        while node.right is not None:
            self.assertIsNone(node.left)
            node, depth = node.right, depth + 1
        self.assertEqual(depth, n)
        self.assertIs(is_balanced(right), False)
        self.assertEqual(format_path(find_path(right, node)),
                         " -> ".join(["корень"] + ["П"] * (n - 1)))
        self.assertEqual(len(render_tree(right).split("\n")), 2 * n - 1)
        # нарушение – третий снизу узел, на глубине n - 2
        self.assertIn("[" + " -> ".join(["корень"] + ["П"] * (n - 3)) + "]", explain(right)[1])

        left = build_tree([n] + [v for i in range(n - 1, 0, -1) for v in (i, None)])
        self.assertIsNone(left.right)
        self.assertEqual(left.left.val, n - 1)
        self.assertIs(is_balanced(left), False)


class TestRender(unittest.TestCase):

    def test_empty(self):
        self.assertEqual(render_tree(None), "(пустое дерево)")

    def test_single(self):
        self.assertEqual(render_tree(N(7)), "7")
        self.assertEqual(render_tree(N(-15)), "-15")
        self.assertEqual(render_tree(N(0)), "0")

    def test_example(self):
        self.assertEqual(render_tree(N(10, N(5), N(15, N(6), N(20)))), EXAMPLE_PICTURE)

    def test_readme_unbalanced(self):
        self.assertEqual(render_tree(readme_unbalanced()), README_UNBALANCED_PICTURE)

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

    def test_duplicates(self):
        self.assertEqual(render_tree(N(7, N(7), N(7))), " _7_\n/   \\\n7   7")

    def test_chains(self):
        self.assertEqual(render_tree(build_tree([3, 2, None, 1])),
                         "   _3\n  /\n _2\n/\n1")
        self.assertEqual(render_tree(build_tree([1, None, 2, None, 3])),
                         "1_\n  \\\n  2_\n    \\\n    3")

    def test_labels_do_not_overlap(self):
        """Каждое значение стоит на рисунке целиком, связи – в отдельных строках."""
        rnd = random.Random(9)
        for _ in range(300):
            tree = random_tree(rnd, rnd.randint(1, 14))
            lines = render_tree(tree).split("\n")
            self.assertEqual(len(lines), 2 * naive_height(tree) - 1)
            labels = " ".join(lines[::2]).replace("_", " ").split()
            self.assertEqual(sorted(labels), sorted(map(str, values(tree))))
            self.assertTrue(set("".join(lines[1::2])) <= {" ", "/", "\\"})

    def test_tree_not_modified(self):
        tree = readme_unbalanced()
        before = snapshot(tree)
        render_tree(tree)
        explain(tree)
        self.assertEqual(snapshot(tree), before)


class TestExplain(unittest.TestCase):

    def test_empty(self):
        self.assertIn("Пустое дерево считается сбалансированным", explain(None)[0])

    def test_balanced(self):
        for tree in (N(7), readme_balanced(), perfect(4), fibonacci(6)):
            lines = explain(tree)
            self.assertEqual(len(lines), 1)
            self.assertIn("Дерево сбалансировано", lines[0])
            self.assertIn("не больше чем на 1", lines[0])

    def test_inner_violation(self):
        self.assertEqual(explain(readme_unbalanced()), [
            "Дерево не сбалансировано.",
            "Нарушение: узел 15 [корень -> П] – высота левого поддерева 0, правого 2, "
            "разность 2 > 1."])

    def test_root_violation(self):
        self.assertEqual(explain(N(0, perfect(4), perfect(2)))[1],
                         "Нарушение: узел 0 [корень] – высота левого поддерева 4, правого 2, "
                         "разность 2 > 1.")

    def test_same_node_as_is_balanced(self):
        """Пояснение указывает тот узел, на котором остановилась is_balanced (первый снизу)."""
        rnd = random.Random(21)
        for _ in range(300):
            tree = random_tree(rnd, rnd.randint(0, 30))
            violation = first_violation(tree)
            self.assertEqual(violation is None, is_balanced(tree))
            if violation is not None:
                node, h_left, h_right = violation
                self.assertEqual((h_left, h_right),
                                 (naive_height(node.left), naive_height(node.right)))
                self.assertIn(f"узел {node.val} [{format_path(find_path(tree, node))}]",
                              explain(tree)[1])

    def test_path_distinguishes_equal_values(self):
        # все значения 0: путь однозначно указывает узел, а не значение
        tree = N(0, N(0), N(0, None, N(0, None, N(0))))
        self.assertIn("узел 0 [корень -> П]", explain(tree)[1])


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
        self.assertEqual(output,
            "Постройте бинарное дерево по уровням. Значения – целые числа (можно "
            "отрицательные и 0), '-' – узла нет.\n"
            "В квадратных скобках – путь от корня к узлу: Л – влево, П – вправо.\n"
            "\nПостроенное дерево:\n" + EXAMPLE_PICTURE + "\n\n"
            "Результат проверки: True\n"
            "Дерево сбалансировано: для каждого узла высоты левого и правого "
            "поддеревьев отличаются не больше чем на 1.\n")

    def test_empty_tree(self):
        output, prompts = run_session(["-"])
        self.assertEqual(len(prompts), 1)
        self.assertIn("Построенное дерево:\n(пустое дерево)\n", output)
        self.assertIn("Результат проверки: True", output)
        self.assertIn("Пустое дерево считается сбалансированным", output)

    def test_single_node(self):
        output, prompts = run_session(["7", "-", "-"])
        self.assertEqual(len(prompts), 3)
        self.assertIn("Построенное дерево:\n7\n", output)
        self.assertIn("Результат проверки: True", output)

    def test_balanced(self):
        self.assertEqual(session_result(answers_for(readme_balanced())), "True")
        self.assertEqual(session_result(["1", "2", "3", "-", "-", "-", "-"]), "True")

    def test_unbalanced(self):
        # левая цепочка 1 -> 2 -> 3: нарушение у корня
        output, _ = run_session(["1", "2", "-", "3", "-", "-", "-"])
        self.assertIn("Результат проверки: False\nДерево не сбалансировано.\n"
                      "Нарушение: узел 1 [корень] – высота левого поддерева 2, правого 0, "
                      "разность 2 > 1.\n", output)

    def test_root_balanced_inner_not(self):
        output, prompts = run_session(README_UNBALANCED_SESSION)
        self.assertEqual(len(prompts), 17)                   # 2n + 1 для n = 8
        self.assertIn(README_UNBALANCED_PICTURE, output)
        self.assertIn("Результат проверки: False", output)
        self.assertIn("Нарушение: узел 15 [корень -> П] – высота левого поддерева 0, "
                      "правого 2", output)

    def test_left_only_and_right_only(self):
        left = ["5", "4", "-", "3", "-", "2", "-", "-", "-"]
        right = ["1", "-", "2", "-", "3", "-", "-"]
        out_left, _ = run_session(left)
        out_right, _ = run_session(right)
        self.assertIn("   _4\n  /\n _3\n/\n2", out_left)
        self.assertIn("1_\n  \\\n  2_\n    \\\n    3", out_right)
        self.assertIn("Результат проверки: False", out_left)
        self.assertIn("Нарушение: узел 4 [корень -> Л] – высота левого поддерева 2, правого 0",
                      out_left)
        self.assertIn("Результат проверки: False", out_right)
        self.assertIn("Нарушение: узел 1 [корень] – высота левого поддерева 0, правого 2",
                      out_right)
        # из двух узлов – сбалансированы с любой стороны
        self.assertEqual(session_result(["5", "4", "-", "-", "-"]), "True")
        self.assertEqual(session_result(["5", "-", "6", "-", "-"]), "True")

    def test_non_bst(self):
        # 20 слева от 10, 5 справа: не BST, но сбалансировано
        output, _ = run_session(["10", "20", "5", "-", "-", "-", "-"])
        self.assertIn(" __10_\n/     \\\n20    5", output)
        self.assertIn("Результат проверки: True", output)

    def test_duplicates(self):
        lines = ["7", "7", "7", "7", "-", "-", "-", "-", "-"]
        output, prompts = run_session(lines)
        self.assertEqual(len(prompts), len(set(prompts)))   # пути различают равные значения
        self.assertIn("Левый ребенок узла 7 [корень -> Л]: ", prompts)
        self.assertIn("Левый ребенок узла 7 [корень -> П]: ", prompts)
        self.assertIn("Результат проверки: True", output)
        self.assertEqual(session_result(["7", "7", "-", "7", "-", "-", "-"]), "False")

    def test_negative_and_zero(self):
        lines = ["0", "-5", "3", "-10", "-1", "-", "-", "-", "-", "-", "-"]
        output, _ = run_session(lines)
        self.assertIn("     _____0_\n    /       \\\n  __-5_     3\n /     \\\n-10    -1",
                      output)
        self.assertIn("Результат проверки: True", output)
        output, _ = run_session(["0", "-1", "-", "-2", "-", "-", "-"])
        self.assertIn("Результат проверки: False", output)
        self.assertIn("Нарушение: узел 0 [корень]", output)

    def test_missing_nodes(self):
        """'-' в середине уровня: у отсутствующего узла дети не спрашиваются."""
        output, prompts = run_session(["1", "-", "2", "3", "-", "-", "-"])
        self.assertEqual(prompts[1:], [
            "Левый ребенок узла 1 [корень]: ",
            "Правый ребенок узла 1 [корень]: ",
            "Левый ребенок узла 2 [корень -> П]: ",
            "Правый ребенок узла 2 [корень -> П]: ",
            "Левый ребенок узла 3 [корень -> П -> Л]: ",
            "Правый ребенок узла 3 [корень -> П -> Л]: ",
        ])
        self.assertIn("1___\n    \\\n   _2\n  /\n  3", output)
        self.assertIn("Результат проверки: False", output)

    def test_bad_input_is_asked_again(self):
        lines = ["abc", "", "3.5", "10",       # корень с четвертой попытки после трех ошибок
                 "5", "--", "15",              # ошибка на правом ребенке корня
                 "-", "-", "x y", "-", "-"]
        output, prompts = run_session(lines)
        self.assertEqual(output.count("Ошибка:"), 5)
        self.assertIn("Ошибка: 'abc' – не целое число и не '-'. Введите целое число "
                      "(например, 7, 0, -3) или '-', если узла нет. Повторите ввод.", output)
        self.assertIn("Ошибка: пустая строка", output)
        self.assertIn("Ошибка: '--'", output)
        # после ошибки повторяется тот же самый запрос
        self.assertEqual(prompts[:4], [prompts[0]] * 4)
        self.assertEqual(prompts[5], prompts[6])
        self.assertEqual(prompts[5], "Правый ребенок узла 10 [корень]: ")
        self.assertIn("Результат проверки: True", output)
        self.assertIn(" _10_\n/    \\\n5    15", output)

    def test_matches_oracle(self):
        """Случайные деревья: сеанс ввода дает то же дерево и тот же ответ, что и оракул."""
        rnd = random.Random(13)
        answers = set()
        for _ in range(200):
            tree = random_tree(rnd, rnd.randint(0, 12))
            output, _ = run_session(answers_for(tree))
            expected = naive_balanced(tree)
            answers.add(expected)
            self.assertIn(f"Построенное дерево:\n{render_tree(tree)}\n", output)
            self.assertIn(f"Результат проверки: {expected}\n", output)
        self.assertEqual(answers, {True, False})

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
            self.assertNotIn("Traceback", out.getvalue())

    def test_node_prompt(self):
        self.assertIn("корня", node_prompt(None, None, None))
        self.assertEqual(node_prompt(N(-3), "right", ((None, "left"), "right")),
                         "Правый ребенок узла -3 [корень -> Л -> П]: ")


class TestCommandLine(unittest.TestCase):

    def test_demo(self):
        output, prompts = run_session([], ["--demo"])
        self.assertEqual(output, "False\nTrue\n")
        self.assertEqual(prompts, [])

    def test_unknown_argument(self):
        for argv in (["--help"], ["--demo", "x"], ["demo"]):
            output, prompts = run_session([], argv)
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
        self.assertEqual(demo.stdout.split(), ["False", "True"])
        run = subprocess.run([sys.executable, "main.py"], cwd=here, env=env,
                             input="\n".join(README_UNBALANCED_SESSION) + "\n",
                             capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(run.returncode, 0, run.stderr)
        self.assertIn(README_UNBALANCED_PICTURE, run.stdout)
        self.assertIn("Результат проверки: False", run.stdout)
        eof = subprocess.run([sys.executable, "main.py"], cwd=here, env=env, input="10\n",
                             capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(eof.returncode, 0, eof.stderr)
        self.assertIn("Ввод прерван.", eof.stdout)
        self.assertNotIn("Traceback", eof.stderr)


if __name__ == "__main__":
    unittest.main()
