"""Тесты к задаче 3 "AVL".

Запуск из корня репозитория:
    python -m unittest discover -s homework_5/AVL -p "test_*.py" -v
или из папки задачи: python -m unittest -v
"""

import io
import math
import os
import random
import subprocess
import sys
import unittest
from contextlib import redirect_stdout

import main
from main import AVL, AVLNode

HERE = os.path.dirname(os.path.abspath(__file__))

# Минимальное AVL-дерево высоты 5: вставка по уровням, поворотов при построении нет
FIB_KEYS = [80, 30, 100, 20, 50, 90, 110, 10, 40, 60, 120, 70]


def validate(test, tree, expected):
    """Независимая проверка всего дерева; не пользуется ни одним методом AVL.

    Рекурсивно спускается с допустимыми границами ключей (lo, hi), сам считает
    высоту каждого поддерева и сверяет ее с сохраненной, проверяет баланс,
    отсутствие повторно достижимых узлов (циклов, общих поддеревьев) и
    что ключи в симметричном порядке – это ровно sorted(expected).
    """
    seen = set()
    keys = []

    def check(node, lo, hi):
        if node is None:
            return 0
        test.assertIsInstance(node, AVLNode)
        test.assertNotIn(id(node), seen, f"узел {node.key} достижим дважды")
        seen.add(id(node))
        test.assertTrue((lo is None or lo < node.key) and (hi is None or node.key < hi),
                        f"ключ {node.key} вне границ ({lo}, {hi})")
        h_left = check(node.left, lo, node.key)
        keys.append(node.key)
        h_right = check(node.right, node.key, hi)
        test.assertLessEqual(abs(h_left - h_right), 1, f"дисбаланс в узле {node.key}")
        real = 1 + max(h_left, h_right)
        test.assertEqual(node.height, real, f"неверная высота узла {node.key}")
        return real

    real_height = check(tree.root, None, None)
    test.assertEqual(keys, sorted(expected))
    return real_height


def shape(node):
    """Дерево как вложенные кортежи (ключ, высота, левое, правое) – для точного сравнения."""
    if node is None:
        return None
    return node.key, node.height, shape(node.left), shape(node.right)


def leaf(key):
    return key, 1, None, None


def max_avl_height(n):
    """Верхняя граница высоты AVL-дерева из n узлов: 1.4405 * log2(n + 2) - 0.3277."""
    return 1.4405 * math.log2(n + 2) - 0.3277


class TestBasic(unittest.TestCase):

    def test_empty(self):
        """Пустое дерево: поиск и удаление ничего не находят"""
        tree = AVL()
        self.assertIsNone(tree.root)
        self.assertEqual(tree.inorder(), [])
        self.assertFalse(tree.search(1))
        self.assertFalse(tree.delete(1))
        self.assertEqual(str(tree), "(пустое дерево)")
        validate(self, tree, [])

    def test_one_key(self):
        tree = AVL()
        self.assertTrue(tree.insert(5))
        self.assertEqual(shape(tree.root), leaf(5))
        self.assertTrue(tree.search(5))
        self.assertFalse(tree.search(4))

    def test_several_keys_and_search(self):
        """Поиск всех присутствующих и промежуточных отсутствующих ключей"""
        keys = [50, 20, 80, 10, 30, 70, 90, 60]
        tree = AVL(keys)
        validate(self, tree, keys)
        for k in range(0, 100, 5):
            self.assertEqual(tree.search(k), k in keys, k)

    def test_duplicate_insert(self):
        """Повторная вставка возвращает False и не меняет дерево"""
        tree = AVL([20, 10, 30])
        before = shape(tree.root)
        for k in (10, 20, 30):
            self.assertFalse(tree.insert(k))
        self.assertEqual(shape(tree.root), before)

    def test_negative_and_zero(self):
        keys = [0, -5, 5, -10, -1, 3, -7]
        tree = AVL(keys)
        validate(self, tree, keys)
        self.assertTrue(tree.search(-7))
        self.assertTrue(tree.delete(0))
        validate(self, tree, set(keys) - {0})

    def test_independent_instances(self):
        """Два дерева не делят узлы и состояние"""
        a, b = AVL([1, 2, 3]), AVL()
        b.insert(10)
        a.delete(2)
        self.assertEqual((a.inorder(), b.inorder()), ([1, 3], [10]))

    def test_search_does_not_modify(self):
        tree = AVL(FIB_KEYS)
        before = shape(tree.root)
        for k in (40, 45, 80, 0, 200):
            tree.search(k)
        self.assertEqual(shape(tree.root), before)

    def test_search_follows_one_path(self):
        """Поиск использует порядок BST: сравнений не больше 2 * высота, а не n"""
        class Key:
            comparisons = 0

            def __init__(self, v):
                self.v = v

            def __eq__(self, other):
                Key.comparisons += 1
                return self.v == other.v

            def __lt__(self, other):
                Key.comparisons += 1
                return self.v < other.v

            def __gt__(self, other):
                Key.comparisons += 1
                return self.v > other.v

        tree = AVL(Key(i) for i in range(1023))
        h = tree.root.height
        for v in (0, 511, 1022, -1, 2000):
            Key.comparisons = 0
            tree.search(Key(v))
            self.assertLessEqual(Key.comparisons, 2 * h)


class TestRotations(unittest.TestCase):

    def check_case(self, keys, case):
        log = []
        tree = AVL(keys, log=log)
        validate(self, tree, keys)
        self.assertEqual(shape(tree.root), (20, 2, leaf(10), leaf(30)))
        self.assertIn(f"случай {case}", log[0])
        return log

    def test_ll(self):
        log = self.check_case([30, 20, 10], "LL")
        self.assertEqual(len(log), 2)
        self.assertTrue(log[1].startswith("LL: правый поворот вокруг 30"))

    def test_rr(self):
        log = self.check_case([10, 20, 30], "RR")
        self.assertEqual(len(log), 2)
        self.assertTrue(log[1].startswith("RR: левый поворот вокруг 10"))

    def test_lr(self):
        """Два поворота в правильном порядке; промежуточное дерево – цепочка 30-20-10"""
        log = self.check_case([30, 10, 20], "LR")
        self.assertEqual(len(log), 3)
        self.assertEqual(log[1], "LR, шаг 1: левый поворот вокруг 10\n"
                                 "    __30\n   /\n __20\n/\n10")
        self.assertTrue(log[2].startswith("LR, шаг 2: правый поворот вокруг 30"))

    def test_rl(self):
        log = self.check_case([10, 30, 20], "RL")
        self.assertEqual(len(log), 3)
        self.assertEqual(log[1], "RL, шаг 1: правый поворот вокруг 30\n"
                                 "10_\n   \\\n   20_\n      \\\n      30")
        self.assertTrue(log[2].startswith("RL, шаг 2: левый поворот вокруг 10"))

    def test_rotation_below_root(self):
        """Поворот в глубине: родитель получает новый корень поддерева, корень дерева прежний"""
        tree = AVL([50, 30, 70, 80, 90])
        self.assertEqual(shape(tree.root), (50, 3, leaf(30), (80, 2, leaf(70), leaf(90))))

    def test_subtrees_kept(self):
        """При повороте с непустыми внутренними поддеревьями ничего не теряется"""
        keys = [40, 20, 60, 10, 30, 25]       # LR в корне, у узлов есть внуки
        tree = AVL(keys)
        validate(self, tree, keys)
        self.assertEqual(shape(tree.root),
                         (30, 3, (20, 2, leaf(10), leaf(25)), (40, 2, None, leaf(60))))


class TestDelete(unittest.TestCase):

    def delete(self, keys, key, expected_shape=None):
        tree = AVL(keys, log=[])
        tree.log.clear()
        self.assertTrue(tree.delete(key))
        validate(self, tree, set(keys) - {key})
        self.assertFalse(tree.search(key))
        if expected_shape is not None:
            self.assertEqual(shape(tree.root), expected_shape)
        return tree

    def test_leaf(self):
        self.delete([20, 10, 30], 30, (20, 2, leaf(10), None))

    def test_one_child(self):
        self.delete([20, 10, 30, 40], 30, (20, 2, leaf(10), leaf(40)))

    def test_two_children_successor(self):
        """Ключ заменяется минимумом правого поддерева, сам преемник удаляется"""
        self.delete([20, 10, 30, 25, 40], 20, (25, 3, leaf(10), (30, 2, None, leaf(40))))
        # у преемника есть правый ребенок
        self.delete([20, 10, 40, 5, 30, 50, 35], 20,
                    (30, 3, (10, 2, leaf(5), None), (40, 2, leaf(35), leaf(50))))

    def test_root_and_single_node(self):
        tree = AVL([7])
        self.assertTrue(tree.delete(7))
        self.assertIsNone(tree.root)
        self.delete([20, 10], 20, leaf(10))
        self.delete([20, 30], 20, leaf(30))

    def test_missing_key(self):
        """Удаление отсутствующего ключа: False и дерево не меняется"""
        tree = AVL(FIB_KEYS)
        before = shape(tree.root)
        for k in (0, 45, 85, 1000):
            self.assertFalse(tree.delete(k))
        self.assertEqual(shape(tree.root), before)

    def test_single_rotation(self):
        tree = self.delete([20, 10, 30, 40], 10, (30, 2, leaf(20), leaf(40)))
        self.assertIn("случай RR", tree.log[1])

    def test_double_rotation(self):
        tree = self.delete([20, 10, 30, 25], 10, (25, 2, leaf(20), leaf(30)))
        self.assertIn("случай RL", tree.log[1])

    def test_child_balance_zero(self):
        """Баланс ребенка 0 – одинарный поворот; двойной дал бы другое (тоже AVL) дерево"""
        tree = self.delete([20, 10, 30, 25, 40], 10, (30, 3, (20, 2, None, leaf(25)), leaf(40)))
        self.assertIn("баланс +0 – случай RR", tree.log[1])
        tree = self.delete([20, 10, 30, 5, 15], 30, (10, 3, leaf(5), (20, 2, leaf(15), None)))
        self.assertIn("баланс +0 – случай LL", tree.log[1])

    def test_rebalance_on_two_levels(self):
        """Минимальное дерево высоты 5: удаление листа дает RR внизу и LR в корне"""
        tree = self.delete(FIB_KEYS, 90,
                           (50, 4,
                            (30, 3, (20, 2, leaf(10), None), leaf(40)),
                            (80, 3, (60, 2, None, leaf(70)), (110, 2, leaf(100), leaf(120)))))
        cases = [s.split("случай ")[1].split("\n")[0] for s in tree.log if s.startswith("дисбаланс")]
        self.assertEqual(cases, ["RR", "LR"])

    def test_delete_all(self):
        """Удаление всех ключей в разных порядках с проверкой после каждого шага"""
        keys = list(range(1, 32))
        orders = [keys, keys[::-1], random.Random(5).sample(keys, len(keys))]
        for order in orders:
            tree = AVL(keys)
            rest = set(keys)
            for k in order:
                self.assertTrue(tree.delete(k))
                rest.discard(k)
                validate(self, tree, rest)
            self.assertIsNone(tree.root)

    def test_reinsert_after_delete(self):
        tree = AVL([1, 2, 3, 4, 5])
        tree.delete(3)
        self.assertTrue(tree.insert(3))
        self.assertFalse(tree.insert(3))
        validate(self, tree, [1, 2, 3, 4, 5])


class TestRandom(unittest.TestCase):

    def test_random_operations(self):
        """Случайные операции против эталона set; проверка после каждой операции"""
        for seed in range(5):
            rnd = random.Random(seed)
            tree, reference = AVL(), set()
            for _ in range(600):
                key = rnd.randint(-50, 50)
                op = rnd.random()
                if op < 0.5:
                    self.assertEqual(tree.insert(key), key not in reference)
                    reference.add(key)
                elif op < 0.85:
                    self.assertEqual(tree.delete(key), key in reference)
                    reference.discard(key)
                else:
                    self.assertEqual(tree.search(key), key in reference)
                h = validate(self, tree, reference)
                self.assertEqual(tree.inorder(), sorted(reference))
                if reference:
                    self.assertLessEqual(h, max_avl_height(len(reference)))

    def test_sorted_insertions(self):
        """Возрастающие и убывающие вставки не вырождают дерево в цепочку"""
        n = 2000
        for keys in (range(n), range(n, 0, -1)):
            tree = AVL(keys)
            h = validate(self, tree, keys)
            self.assertLessEqual(h, max_avl_height(n))
            self.assertEqual(h, 11)                 # ceil(log2(2001)) = 11 – почти идеально

    def test_large_mixed(self):
        """Большое дерево: вставка, удаление половины, проверка в конце"""
        rnd = random.Random(42)
        keys = rnd.sample(range(10 ** 6), 5000)
        tree = AVL(keys)
        for k in keys[::2]:
            tree.delete(k)
        h = validate(self, tree, keys[1::2])
        self.assertLessEqual(h, max_avl_height(2500))


class TestDemo(unittest.TestCase):

    def test_readme_matches_program(self):
        """Каждый блок вывода python main.py дословно есть в README"""
        buf = io.StringIO()
        with redirect_stdout(buf):
            main.main()
        with open(os.path.join(HERE, "README.md"), encoding="utf-8") as f:
            readme = f.read()
        for block in buf.getvalue().strip().split("\n\n"):
            self.assertIn(block, readme)

    def test_import_is_silent(self):
        out = subprocess.run([sys.executable, "-c", "import main"], cwd=HERE,
                             capture_output=True, text=True, check=True).stdout
        self.assertEqual(out, "")


if __name__ == "__main__":
    unittest.main()
