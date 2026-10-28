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


if __name__ == "__main__":
    unittest.main()
