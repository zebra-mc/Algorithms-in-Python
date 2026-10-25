"""Тесты к задаче 2 "Validate BST". Запуск: python -m unittest -v"""

import random
import sys
import unittest

from main import TreeNode, check_steps, is_valid_bst

N = TreeNode


def readme_tree():
    """Дерево из визуализации в README: 16 нарушает границу, заданную корнем 15."""
    return N(15,
             N(8, N(4), N(12, N(10), N(16))),
             N(23, N(17), N(30)))


def nodes(root):
    """Все узлы дерева в прямом порядке (рекурсия, только для небольших деревьев)."""
    if root is None:
        return []
    return [root] + nodes(root.left) + nodes(root.right)


def values(root):
    return [node.value for node in nodes(root)]


def oracle(root):
    """Независимый эталон прямо по определению, O(n^2):
    для каждого узла сравниваем его со всеми значениями левого и правого поддеревьев."""
    return all(all(v < node.value for v in values(node.left)) and
               all(v > node.value for v in values(node.right))
               for node in nodes(root))


def inorder_oracle(root):
    """Второй эталон: симметричный обход должен строго возрастать."""
    def inorder(node):
        return [] if node is None else inorder(node.left) + [node.value] + inorder(node.right)
    seq = inorder(root)
    return all(a < b for a, b in zip(seq, seq[1:]))


def parents_only(root):
    """Ошибочная проверка: каждый узел сравнивается только со своими детьми."""
    return all((node.left is None or node.left.value < node.value) and
               (node.right is None or node.right.value > node.value)
               for node in nodes(root))


def insert(root, value):
    """Вставка в BST (без повторов), нужна только для генерации корректных деревьев."""
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
        # 10 справа от 5 корректно относительно родителя, но равно корню
        self.assertIs(is_valid_bst(N(10, N(5, None, N(10)))), False)
        self.assertIs(is_valid_bst(N(10, None, N(15, N(10)))), False)


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

    def test_duplicates(self):
        self.assertIs(is_valid_bst(N(5, N(5))), False)
        self.assertIs(is_valid_bst(N(5, None, N(5))), False)
        self.assertIs(is_valid_bst(N(5, N(3, None, N(5)))), False)
        self.assertIs(is_valid_bst(N(5, None, N(8, N(5)))), False)
        # повтор глубоко, не у соседних узлов
        self.assertIs(is_valid_bst(N(20, N(10, N(5), N(15, N(12), N(15))), N(30))), False)
        self.assertIs(is_valid_bst(N(20, N(10), N(30, N(25, None, N(28, N(25)))))), False)

    def test_chains(self):
        left, _ = chain([5, 4, 3, 2, 1], "left")
        right, _ = chain([1, 2, 3, 4, 5], "right")
        self.assertIs(is_valid_bst(left), True)
        self.assertIs(is_valid_bst(right), True)
        bad_left, _ = chain([5, 4, 6, 3], "left")
        bad_right, _ = chain([1, 2, 2, 3], "right")
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
            self.assertEqual(ok, (low is None or low < node.value) and
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


if __name__ == "__main__":
    unittest.main()
