"""Тесты к задаче 3 "Balanced Binary Tree". Запуск: python -m unittest -v"""

import random
import sys
import unittest

from main import TreeNode as N
from main import is_balanced, postorder_heights


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


if __name__ == "__main__":
    unittest.main()
