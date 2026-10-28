"""Тесты к задаче 1 "Tree Traversal". Запуск: python -m unittest -v"""

import os
import random
import re
import subprocess
import sys
import unittest
from collections import Counter

from main import PROMPT, BinarySearchTree, Node, main, parse_values, read_values, render_tree

HERE = os.path.dirname(os.path.abspath(__file__))

README_VALUES = [41, 20, 65, 11, 29, 91, 32, 72, 26, 29]

TRAVERSALS = ("preorder", "inorder", "postorder",
              "reverse_preorder", "reverse_inorder", "reverse_postorder")


# Независимые эталоны: рекурсия прямо по определениям из Wikipedia.
# Подходят только для неглубоких деревьев, длинные цепочки проверяются отдельно.

def ref_preorder(node):
    return [] if node is None else [node.value] + ref_preorder(node.left) + ref_preorder(node.right)


def ref_inorder(node):
    return [] if node is None else ref_inorder(node.left) + [node.value] + ref_inorder(node.right)


def ref_postorder(node):
    return [] if node is None else ref_postorder(node.left) + ref_postorder(node.right) + [node.value]


def ref_reverse_preorder(node):
    return [] if node is None else [node.value] + ref_reverse_preorder(node.right) + ref_reverse_preorder(node.left)


def ref_reverse_inorder(node):
    return [] if node is None else ref_reverse_inorder(node.right) + [node.value] + ref_reverse_inorder(node.left)


def ref_reverse_postorder(node):
    return [] if node is None else ref_reverse_postorder(node.right) + ref_reverse_postorder(node.left) + [node.value]


REFERENCE = {
    "preorder": ref_preorder,
    "inorder": ref_inorder,
    "postorder": ref_postorder,
    "reverse_preorder": ref_reverse_preorder,
    "reverse_inorder": ref_reverse_inorder,
    "reverse_postorder": ref_reverse_postorder,
}


def shape(node):
    """Структура поддерева в виде вложенных кортежей (value, left, right)."""
    return None if node is None else (node.value, shape(node.left), shape(node.right))


def links(tree):
    """Снимок всех связей: id(node) -> (node, left, right). Без рекурсии."""
    result = {}
    stack = [tree.root] if tree.root is not None else []
    while stack:
        node = stack.pop()
        result[id(node)] = (node, node.left, node.right)
        stack.extend(child for child in (node.left, node.right) if child is not None)
    return result


def run_all(tree):
    return {name: getattr(tree, name)() for name in TRAVERSALS}


class BSTMixin:

    def check_bst(self, tree):
        """Инвариант left < node <= right для всех поддеревьев, а не только детей.

        Каждый узел получает от предков границы lo <= value < hi. Возвращает число узлов.
        """
        count = 0
        stack = [(tree.root, None, None)]
        while stack:
            node, lo, hi = stack.pop()
            if node is None:
                continue
            count += 1
            if lo is not None:
                self.assertLessEqual(lo, node.value)
            if hi is not None:
                self.assertLess(node.value, hi)
            stack.append((node.left, lo, node.value))
            stack.append((node.right, node.value, hi))
        return count

    def check_against_reference(self, tree, values):
        """Все шесть обходов совпадают с эталонами, длина и кратность значений сохранены."""
        results = run_all(tree)
        for name, result in results.items():
            self.assertEqual(result, REFERENCE[name](tree.root), name)
            self.assertEqual(Counter(result), Counter(values), name)
        self.assertEqual(results["inorder"], sorted(values))
        self.assertEqual(results["reverse_inorder"], sorted(values, reverse=True))


class TestInsert(BSTMixin, unittest.TestCase):

    def test_empty(self):
        """Граница: пустое дерево"""
        self.assertIsNone(BinarySearchTree().root)
        self.assertIsNone(BinarySearchTree([]).root)

    def test_single(self):
        """Один узел становится корнем без детей"""
        tree = BinarySearchTree([7])
        self.assertEqual(shape(tree.root), (7, None, None))

    def test_two_nodes(self):
        """Меньшее значение - левый ребенок, большее - правый"""
        self.assertEqual(shape(BinarySearchTree([5, 3]).root), (5, (3, None, None), None))
        self.assertEqual(shape(BinarySearchTree([5, 8]).root), (5, None, (8, None, None)))

    def test_readme_shape(self):
        """Дерево из README: схема совпадает с реальной структурой"""
        tree = BinarySearchTree(README_VALUES)
        self.assertEqual(shape(tree.root), (
            41,
            (20,
             (11, None, None),
             (29,
              (26, None, None),
              (32, (29, None, None), None))),
            (65,
             None,
             (91, (72, None, None), None)),
        ))
        self.assertEqual(self.check_bst(tree), len(README_VALUES))

    def test_duplicates_go_right(self):
        """Равное значение уходит вправо и сохраняется отдельным узлом"""
        self.assertEqual(shape(BinarySearchTree([5, 5, 5]).root),
                         (5, None, (5, None, (5, None, None))))
        # второе 3 проходит вправо от первого 3 и встает левее 4
        self.assertEqual(shape(BinarySearchTree([5, 3, 4, 3]).root),
                         (5, (3, None, (4, (3, None, None), None)), None))

    def test_one_new_leaf_per_insert(self):
        """Каждая вставка добавляет ровно один лист и меняет ровно одну пустую ссылку"""
        rnd = random.Random(1)
        tree = BinarySearchTree()
        for _ in range(300):
            value = rnd.randint(-20, 20)
            before = links(tree)
            tree.insert(value)
            after = links(tree)
            new_ids = after.keys() - before.keys()
            self.assertEqual(len(new_ids), 1)
            new_node = after[new_ids.pop()][0]
            self.assertEqual(new_node.value, value)
            self.assertIsNone(new_node.left)
            self.assertIsNone(new_node.right)
            changed = [key for key in before if before[key][1:] != after[key][1:]]
            if not before:
                self.assertIs(tree.root, new_node)
                continue
            self.assertEqual(len(changed), 1)
            parent, old_left, old_right = before[changed[0]]
            if value < parent.value:
                self.assertIsNone(old_left)
                self.assertIs(parent.left, new_node)
            else:
                self.assertIsNone(old_right)
                self.assertIs(parent.right, new_node)
            self.check_bst(tree)

    def test_invariant_random(self):
        """После случайных вставок с повторами инвариант выполняется во всех поддеревьях"""
        rnd = random.Random(42)
        for _ in range(200):
            values = [rnd.randint(-15, 15) for _ in range(rnd.randint(0, 60))]
            tree = BinarySearchTree(values)
            self.assertEqual(self.check_bst(tree), len(values), values)

    def test_constructor_same_as_inserts(self):
        """BinarySearchTree(values) строит то же дерево, что вставки по одной"""
        tree = BinarySearchTree()
        for value in README_VALUES:
            tree.insert(value)
        self.assertEqual(shape(tree.root), shape(BinarySearchTree(README_VALUES).root))

    def test_instances_independent(self):
        """У разных деревьев нет общего состояния"""
        first = BinarySearchTree()
        second = BinarySearchTree()
        first.insert(1)
        self.assertIsNone(second.root)
        second.insert(2)
        self.assertEqual(first.inorder(), [1])
        self.assertEqual(second.inorder(), [2])


class TestTraversals(BSTMixin, unittest.TestCase):

    def test_empty(self):
        """Пустое дерево: все шесть обходов дают пустой список"""
        for name, result in run_all(BinarySearchTree()).items():
            self.assertEqual(result, [], name)

    def test_single(self):
        """Один узел: все обходы дают [value]"""
        for name, result in run_all(BinarySearchTree([0])).items():
            self.assertEqual(result, [0], name)

    def test_two_nodes(self):
        """Левый и правый ребенок: здесь видна разница N до и после детей"""
        self.assertEqual(run_all(BinarySearchTree([5, 3])), {
            "preorder": [5, 3], "inorder": [3, 5], "postorder": [3, 5],
            "reverse_preorder": [5, 3], "reverse_inorder": [5, 3], "reverse_postorder": [3, 5],
        })
        self.assertEqual(run_all(BinarySearchTree([5, 8])), {
            "preorder": [5, 8], "inorder": [5, 8], "postorder": [8, 5],
            "reverse_preorder": [5, 8], "reverse_inorder": [8, 5], "reverse_postorder": [8, 5],
        })

    def test_full_tree(self):
        """Полное дерево из 7 узлов, у внутренних узлов по два ребенка"""
        tree = BinarySearchTree([4, 2, 6, 1, 3, 5, 7])
        self.assertEqual(run_all(tree), {
            "preorder": [4, 2, 1, 3, 6, 5, 7],
            "inorder": [1, 2, 3, 4, 5, 6, 7],
            "postorder": [1, 3, 2, 5, 7, 6, 4],
            "reverse_preorder": [4, 6, 7, 5, 2, 3, 1],
            "reverse_inorder": [7, 6, 5, 4, 3, 2, 1],
            "reverse_postorder": [7, 5, 6, 3, 1, 2, 4],
        })

    def test_only_left_and_only_right(self):
        """Цепочки: только левые дети и только правые дети"""
        left = BinarySearchTree([3, 2, 1])
        self.assertEqual(run_all(left), {
            "preorder": [3, 2, 1], "inorder": [1, 2, 3], "postorder": [1, 2, 3],
            "reverse_preorder": [3, 2, 1], "reverse_inorder": [3, 2, 1], "reverse_postorder": [1, 2, 3],
        })
        right = BinarySearchTree([1, 2, 3])
        self.assertEqual(run_all(right), {
            "preorder": [1, 2, 3], "inorder": [1, 2, 3], "postorder": [3, 2, 1],
            "reverse_preorder": [1, 2, 3], "reverse_inorder": [3, 2, 1], "reverse_postorder": [3, 2, 1],
        })

    def test_zigzag(self):
        """Несимметричное дерево со смешанными ветвями: 10 -> 2 -> 8 -> 4 -> 6"""
        tree = BinarySearchTree([10, 2, 8, 4, 6])
        self.assertEqual(shape(tree.root),
                         (10, (2, None, (8, (4, None, (6, None, None)), None)), None))
        self.assertEqual(run_all(tree), {
            "preorder": [10, 2, 8, 4, 6],
            "inorder": [2, 4, 6, 8, 10],
            "postorder": [6, 4, 8, 2, 10],
            "reverse_preorder": [10, 2, 8, 4, 6],
            "reverse_inorder": [10, 8, 6, 4, 2],
            "reverse_postorder": [6, 4, 8, 2, 10],
        })

    def test_negative_zero_big(self):
        """Отрицательные числа, ноль и длинная арифметика"""
        big = 10 ** 30
        tree = BinarySearchTree([0, -big, big, -1, 1, -big])
        self.assertEqual(run_all(tree), {
            "preorder": [0, -big, -1, -big, big, 1],
            "inorder": [-big, -big, -1, 0, 1, big],
            "postorder": [-big, -1, -big, 1, big, 0],
            "reverse_preorder": [0, big, 1, -big, -1, -big],
            "reverse_inorder": [big, 1, 0, -1, -big, -big],
            "reverse_postorder": [1, big, -big, -1, -big, 0],
        })

    def test_duplicates(self):
        """Повторы сохраняются: длина и кратность совпадают с вставленными значениями"""
        values = [5, 3, 5, 3, 8, 5, 3]
        tree = BinarySearchTree(values)
        self.assertEqual(tree.inorder(), [3, 3, 3, 5, 5, 5, 8])
        self.assertEqual(tree.reverse_inorder(), [8, 5, 5, 5, 3, 3, 3])
        self.check_against_reference(tree, values)

    def test_reverse_preorder_vs_reverse_postorder(self):
        """NRL и RLN различаются: корень первым в одном и последним в другом"""
        tree = BinarySearchTree([4, 2, 6, 1, 3, 5, 7])
        self.assertEqual(tree.reverse_preorder()[0], 4)
        self.assertEqual(tree.reverse_postorder()[-1], 4)
        self.assertNotEqual(tree.reverse_preorder(), tree.reverse_postorder())
        # NRL - зеркало LRN, RLN - зеркало NLR; так обходы не реализованы, но для проверки годится
        self.assertEqual(tree.reverse_preorder(), tree.postorder()[::-1])
        self.assertEqual(tree.reverse_postorder(), tree.preorder()[::-1])

    def test_repeated_calls(self):
        """Повторный вызов дает тот же результат в новом списке, правка списка ни на что не влияет"""
        tree = BinarySearchTree(README_VALUES)
        for name in TRAVERSALS:
            first = getattr(tree, name)()
            first.append("мусор")
            second = getattr(tree, name)()
            self.assertIsNot(first, second, name)
            self.assertEqual(second, first[:-1], name)
            self.assertEqual(getattr(tree, name)(), second, name)

    def test_traversals_do_not_modify_tree(self):
        """Узлы, значения и связи после всех обходов те же"""
        tree = BinarySearchTree(README_VALUES)
        before = {key: (node, left, right, node.value) for key, (node, left, right) in links(tree).items()}
        root = tree.root
        run_all(tree)
        after = {key: (node, left, right, node.value) for key, (node, left, right) in links(tree).items()}
        self.assertIs(tree.root, root)
        self.assertEqual(before, after)

    def test_against_reference_random(self):
        """Сверка с рекурсивными эталонами, sorted и Counter на 300 случайных деревьях"""
        rnd = random.Random(7)
        for _ in range(300):
            values = [rnd.randint(-50, 50) for _ in range(rnd.randint(0, 40))]
            self.check_against_reference(BinarySearchTree(values), values)


class TestLargeTrees(BSTMixin, unittest.TestCase):

    def test_sorted_inserts_deeper_than_recursion_limit(self):
        """3000 вставок по возрастанию: цепочка правых детей глубже лимита рекурсии"""
        n = 3000
        self.assertGreater(n, sys.getrecursionlimit())
        values = list(range(n))
        tree = BinarySearchTree(values)
        self.assertEqual(self.check_bst(tree), n)
        down = values[::-1]
        self.assertEqual(run_all(tree), {
            "preorder": values, "inorder": values, "postorder": down,
            "reverse_preorder": values, "reverse_inorder": down, "reverse_postorder": down,
        })

    def test_long_left_chain(self):
        """100 000 узлов только с левыми детьми.

        Связи собраны вручную: через insert такая цепочка строилась бы за n^2 / 2 шагов.
        """
        n = 100_000
        tree = BinarySearchTree()
        tree.root = Node(n)
        node = tree.root
        for value in range(n - 1, 0, -1):
            node.left = Node(value)
            node = node.left
        up = list(range(1, n + 1))
        down = up[::-1]
        self.assertEqual(run_all(tree), {
            "preorder": down, "inorder": up, "postorder": up,
            "reverse_preorder": down, "reverse_inorder": down, "reverse_postorder": up,
        })

    def test_big_random(self):
        """20 000 случайных значений с повторами"""
        rnd = random.Random(2024)
        values = [rnd.randint(-10 ** 9, 10 ** 9) for _ in range(19_000)]
        values += rnd.choices(values, k=1000)
        tree = BinarySearchTree(values)
        self.assertEqual(self.check_bst(tree), len(values))
        self.check_against_reference(tree, values)


class TestReadmeExample(unittest.TestCase):

    def test_traversals(self):
        """Все шесть последовательностей из таблицы визуализации в README"""
        tree = BinarySearchTree(README_VALUES)
        self.assertEqual(run_all(tree), {
            "preorder": [41, 20, 11, 29, 26, 32, 29, 65, 91, 72],
            "inorder": [11, 20, 26, 29, 29, 32, 41, 65, 72, 91],
            "postorder": [11, 26, 29, 32, 29, 20, 72, 91, 65, 41],
            "reverse_preorder": [41, 65, 91, 72, 20, 29, 32, 29, 26, 11],
            "reverse_inorder": [91, 72, 65, 41, 32, 29, 29, 26, 20, 11],
            "reverse_postorder": [72, 91, 65, 29, 32, 26, 29, 11, 20, 41],
        })

    def test_duplicate_position(self):
        """Второе 29 из README - левый ребенок 32 в правом поддереве первого 29"""
        tree = BinarySearchTree(README_VALUES)
        first = tree.root.left.right
        second = first.right.left
        self.assertEqual((first.value, first.right.value, second.value), (29, 32, 29))
        self.assertIsNot(first, second)


README_OUTPUT = (
    "preorder           [41, 20, 11, 29, 26, 32, 29, 65, 91, 72]\n"
    "inorder            [11, 20, 26, 29, 29, 32, 41, 65, 72, 91]\n"
    "postorder          [11, 26, 29, 32, 29, 20, 72, 91, 65, 41]\n"
    "reverse_preorder   [41, 65, 91, 72, 20, 29, 32, 29, 26, 11]\n"
    "reverse_inorder    [91, 72, 65, 41, 32, 29, 29, 26, 20, 11]\n"
    "reverse_postorder  [72, 91, 65, 29, 32, 26, 29, 11, 20, 41]\n"
)

README_PICTURE = (
    "    ______________41_\n"
    "   /                 \\\n"
    " __20____            65____\n"
    "/        \\                 \\\n"
    "11     __29____          __91\n"
    "      /        \\        /\n"
    "      26     __32       72\n"
    "            /\n"
    "            29"
)

# Полный вывод main после приглашения: пустая строка, рисунок, пустая строка, обходы
README_SESSION = "\nПостроенное дерево:\n" + README_PICTURE + "\n\n" + README_OUTPUT


class FakeConsole:
    """Подмена input и print: отдает строки по очереди, затем EOFError, и копит вывод."""

    def __init__(self, *lines):
        self.lines = list(lines)
        self.prompts = []
        self.output = []

    def read(self, prompt=""):
        self.prompts.append(prompt)
        if not self.lines:
            raise EOFError
        return self.lines.pop(0)

    def write(self, *args):
        self.output.append(" ".join(str(arg) for arg in args))


def run_script(stdin_text, *args):
    """Запускает интерпретатор в папке задачи отдельным процессом, возвращает CompletedProcess."""
    return subprocess.run([sys.executable, *args], input=stdin_text, capture_output=True,
                          text=True, encoding="utf-8", cwd=HERE, timeout=30,
                          env={**os.environ, "PYTHONIOENCODING": "utf-8"})


class TestParseValues(unittest.TestCase):

    def test_order_kept(self):
        """Порядок чисел сохраняется - это порядок вставки"""
        self.assertEqual(parse_values("41 20 65 11 29 91 32 72 26 29"), README_VALUES)

    def test_empty(self):
        """Пустая строка и одни пробельные символы - пустой список"""
        for text in ("", "   ", "\t \n"):
            self.assertEqual(parse_values(text), [], repr(text))

    def test_single(self):
        self.assertEqual(parse_values("7"), [7])

    def test_negative_zero_duplicates(self):
        """Отрицательные, ноль, -0, знак плюс и повторы"""
        self.assertEqual(parse_values("-5 0 -0 +3 -5 3"), [-5, 0, 0, 3, -5, 3])

    def test_extra_spaces(self):
        """Лишние пробелы и табуляции между числами не мешают"""
        self.assertEqual(parse_values("  1   -2\t3  "), [1, -2, 3])

    def test_big_number(self):
        self.assertEqual(parse_values(str(10 ** 30) + " -" + str(10 ** 30)), [10 ** 30, -10 ** 30])

    def test_invalid(self):
        """Не целые числа: ValueError, в сообщении перечислены все плохие токены"""
        for text, bad in (("abc", ["abc"]), ("1 2.5 3", ["2.5"]), ("1,2", ["1,2"]),
                          ("1 x 2 y", ["x", "y"]), ("- 5", ["-"]), ("1e3", ["1e3"])):
            with self.assertRaises(ValueError, msg=text) as ctx:
                parse_values(text)
            for token in bad:
                self.assertIn(token, str(ctx.exception), text)


class TestReadValues(unittest.TestCase):

    def test_valid_first_try(self):
        console = FakeConsole("3 1 2")
        self.assertEqual(read_values(console.read, console.write), [3, 1, 2])
        self.assertEqual(console.prompts, [PROMPT])
        self.assertEqual(console.output, [])

    def test_prompt_text(self):
        """Приглашение совпадает с условием"""
        self.assertEqual(PROMPT.strip(), "Введите целые числа через пробел в порядке вставки в BST:")

    def test_empty_input(self):
        console = FakeConsole("")
        self.assertEqual(read_values(console.read, console.write), [])

    def test_retry_after_invalid(self):
        """Некорректный ввод: сообщение об ошибке и повторный запрос, пока ввод не станет верным"""
        console = FakeConsole("abc", "1 2.5", "-1 0 -1")
        self.assertEqual(read_values(console.read, console.write), [-1, 0, -1])
        self.assertEqual(console.prompts, [PROMPT] * 3)
        self.assertEqual(len(console.output), 2)
        self.assertIn("abc", console.output[0])
        self.assertIn("2.5", console.output[1])
        for line in console.output:
            self.assertTrue(line.startswith("Ошибка:"), line)
            self.assertIn("Повторите ввод", line)

    def test_eof_and_interrupt(self):
        """Ctrl+D и Ctrl+C: без исключения, возвращается None"""
        console = FakeConsole("x")
        self.assertIsNone(read_values(console.read, console.write))
        self.assertIn("Ввод прерван.", console.output)

        def interrupted(prompt):
            raise KeyboardInterrupt

        console = FakeConsole()
        self.assertIsNone(read_values(interrupted, console.write))
        self.assertIn("Ввод прерван.", console.output)


class TestMain(unittest.TestCase):

    def check_main(self, lines, expected):
        """main с подменным вводом печатает шесть обходов дерева из expected"""
        console = FakeConsole(*lines)
        main(console.read, console.write)
        tree = BinarySearchTree(expected)
        self.assertEqual(console.output[-6:],
                         [f"{name:<18} {getattr(tree, name)()}" for name in TRAVERSALS])

    def test_readme_input(self):
        console = FakeConsole("41 20 65 11 29 91 32 72 26 29")
        main(console.read, console.write)
        self.assertEqual("\n".join(console.output) + "\n", README_SESSION)

    def test_empty(self):
        """Пустой ввод: пустое дерево, все шесть списков пустые"""
        console = FakeConsole("")
        main(console.read, console.write)
        self.assertEqual(console.output, ["", "Построенное дерево:", "(пустое дерево)", ""]
                         + [f"{name:<18} []" for name in TRAVERSALS])

    def test_single(self):
        self.check_main(["42"], [42])

    def test_negative_and_duplicates(self):
        """Отрицательные, ноль и повторы проходят через ввод так же, как через конструктор"""
        self.check_main(["-3 0 -3 5 0 -10"], [-3, 0, -3, 5, 0, -10])

    def test_invalid_then_valid(self):
        """После ошибки дерево строится из второй, корректной строки"""
        self.check_main(["1 два 3", "1 2 3"], [1, 2, 3])
        console = FakeConsole("1 два 3", "1 2 3")
        main(console.read, console.write)
        # ошибка, пустая строка, заголовок, рисунок, пустая строка, шесть обходов
        self.assertEqual(len(console.output), 11)
        self.assertIn("два", console.output[0])
        self.assertEqual(console.output[3], "1_\n  \\\n  2_\n    \\\n    3")

    def test_eof_prints_nothing_else(self):
        console = FakeConsole()
        main(console.read, console.write)
        self.assertEqual(console.output, ["", "Ввод прерван."])


class TestScript(unittest.TestCase):
    """Настоящий запуск python main.py через stdin в отдельном процессе."""

    def test_readme_example(self):
        result = run_script("41 20 65 11 29 91 32 72 26 29\n", "main.py")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, PROMPT + README_SESSION)
        self.assertEqual(result.stderr, "")

    def test_invalid_then_valid(self):
        result = run_script("5 q\n5\n", "main.py")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stderr, "")
        self.assertEqual(result.stdout.count(PROMPT), 2)
        self.assertIn("Ошибка: не целые числа: q. Повторите ввод.", result.stdout)
        self.assertIn("inorder            [5]", result.stdout)

    def test_eof_without_traceback(self):
        """Ввод закончился раньше корректной строки: код 0, без трассировки"""
        for stdin_text in ("", "bad\n"):
            result = run_script(stdin_text, "main.py")
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(result.stderr, "")
            self.assertIn("Ввод прерван.", result.stdout)

    def test_import_does_not_ask(self):
        """При импорте модуля ничего не спрашивается и не печатается"""
        result = run_script("", "-c", "import main; print(main.BinarySearchTree([2, 1]).inorder())")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "[1, 2]\n")


# ---------------------------------------------------------------------------
# Визуализация дерева
# ---------------------------------------------------------------------------

SAMPLE_VALUES = [8, 3, 10, 1, 6, 14]

SAMPLE_PICTURE = (
    "   ___8_\n"
    "  /     \\\n"
    " _3_    10_\n"
    "/   \\      \\\n"
    "1   6      14"
)

SORTED_PICTURE = (
    "1_\n"
    "  \\\n"
    "  3_\n"
    "    \\\n"
    "    6_\n"
    "      \\\n"
    "      8_\n"
    "        \\\n"
    "        10_\n"
    "           \\\n"
    "           14"
)


def parse_picture(picture):
    """Восстанавливает по рисунку структуру дерева (вложенные кортежи, как shape).

    Независимый от render_tree разбор, без рекурсии. Четные строки – подписи, нечетные –
    связи. "/" в колонке c: ребенок – подпись следующего уровня с центром c, родитель –
    подпись, к которой ведет цепочка "_", начинающаяся в колонке c + 1. "\" – зеркально:
    цепочка "_" заканчивается в колонке c - 1 сразу за подписью родителя.
    Если рисунок противоречив (ребенка не нашлось, у узла два левых ребенка и т.п.),
    срабатывает assert.
    """
    if picture == "(пустое дерево)":
        return None
    lines = picture.split("\n")
    assert len(lines) % 2 == 1, "подписи и связи должны чередоваться"
    rows = []        # для каждого уровня: список [start, end, value, left, right]
    for text in lines[::2]:
        rows.append([[m.start(), m.end(), int(m.group()), None, None]
                     for m in re.finditer(r"-?\d+", text)])
    assert len(rows[0]) == 1, "на верхнем уровне ровно один корень"
    for depth, links_row in enumerate(lines[1::2]):
        upper, lower = lines[2 * depth], rows[depth + 1]
        by_center = {item[0] + (item[1] - item[0] - 1) // 2: item for item in lower}
        used = set()
        for c, ch in enumerate(links_row):
            if ch == " ":
                continue
            child = by_center[c]
            used.add(id(child))
            if ch == "/":
                x = c + 1
                assert upper[x] == "_"
                while upper[x] == "_":
                    x += 1
                parent = next(i for i in rows[depth] if i[0] == x)
                assert parent[3] is None
                parent[3] = child
            else:
                assert ch == "\\", ch
                x = c - 1
                assert upper[x] == "_"
                while upper[x] == "_":
                    x -= 1
                parent = next(i for i in rows[depth] if i[1] == x + 1)
                assert parent[4] is None
                parent[4] = child
        assert len(used) == len(lower), "у каждого узла уровня есть связь с родителем"
    # из списков [start, end, value, left, right] собираем кортежи снизу вверх
    built = {}
    for row in reversed(rows):
        for item in row:
            built[id(item)] = (item[2],
                               None if item[3] is None else built[id(item[3])],
                               None if item[4] is None else built[id(item[4])])
    return built[id(rows[0][0])]


class TestRender(unittest.TestCase):

    def check_picture(self, values):
        """Рисунок дерева из values разбирается обратно ровно в структуру этого дерева."""
        tree = BinarySearchTree(values)
        self.assertEqual(parse_picture(render_tree(tree.root)), shape(tree.root), values)

    def test_empty(self):
        """Пустое дерево: надпись вместо рисунка, все обходы пустые"""
        tree = BinarySearchTree([])
        self.assertEqual(render_tree(tree.root), "(пустое дерево)")
        for name, result in run_all(tree).items():
            self.assertEqual(result, [], name)

    def test_single(self):
        self.assertEqual(render_tree(BinarySearchTree([7]).root), "7")
        self.assertEqual(render_tree(BinarySearchTree([-15]).root), "-15")

    def test_sample(self):
        """Пример из условия: 8 3 10 1 6 14 – точный рисунок и его структура"""
        tree = BinarySearchTree(SAMPLE_VALUES)
        self.assertEqual(render_tree(tree.root), SAMPLE_PICTURE)
        self.assertEqual(parse_picture(SAMPLE_PICTURE),
                         (8, (3, (1, None, None), (6, None, None)), (10, None, (14, None, None))))

    def test_readme_tree(self):
        tree = BinarySearchTree(README_VALUES)
        self.assertEqual(render_tree(tree.root), README_PICTURE)
        self.assertEqual(parse_picture(README_PICTURE), shape(tree.root))

    def test_left_chain(self):
        """Вставки по убыванию: только левые дети, лесенка влево"""
        self.assertEqual(render_tree(BinarySearchTree([3, 2, 1]).root),
                         "   _3\n  /\n _2\n/\n1")
        self.check_picture([50, 40, 30, 20, 10])

    def test_right_chain(self):
        """Вставки по возрастанию: только правые дети, лесенка вправо"""
        self.assertEqual(render_tree(BinarySearchTree([1, 2, 3]).root),
                         "1_\n  \\\n  2_\n    \\\n    3")
        self.assertEqual(render_tree(BinarySearchTree(sorted(SAMPLE_VALUES)).root), SORTED_PICTURE)

    def test_negative_and_multidigit(self):
        """Отрицательные, ноль и многозначные числа: подписи целиком и не налезают"""
        self.assertEqual(render_tree(BinarySearchTree([0, -5, 3, -10, -1]).root),
                         "     _____0_\n"
                         "    /       \\\n"
                         "  __-5_     3\n"
                         " /     \\\n"
                         "-10    -1")
        self.assertEqual(render_tree(BinarySearchTree([100, -7, 2048, -7, 0, 99999]).root),
                         " _______100__\n"
                         "/            \\\n"
                         "-7_         2048___\n"
                         "   \\               \\\n"
                         "   -7_           99999\n"
                         "      \\\n"
                         "      0")
        big = 10 ** 30
        self.check_picture([0, -big, big, -1, 1, -big])

    def test_duplicates(self):
        """Повторы рисуются отдельными узлами справа от более раннего равного"""
        self.assertEqual(render_tree(BinarySearchTree([5, 5, 5]).root),
                         "5_\n  \\\n  5_\n    \\\n    5")
        picture = render_tree(BinarySearchTree([5, 3, 4, 3]).root)
        self.assertEqual(picture, " _____5\n/\n3___\n    \\\n   _4\n  /\n  3")
        self.assertEqual(parse_picture(picture), (5, (3, None, (4, (3, None, None), None)), None))

    def test_left_and_right_child_differ(self):
        """Единственный левый и единственный правый ребенок рисуются по-разному"""
        left = render_tree(BinarySearchTree([5, 3]).root)
        right = render_tree(BinarySearchTree([5, 8]).root)
        self.assertEqual(left, " _5\n/\n3")
        self.assertEqual(right, "5_\n  \\\n  8")
        self.assertEqual(parse_picture(left), (5, (3, None, None), None))
        self.assertEqual(parse_picture(right), (5, None, (8, None, None)))
        # левый ребенок левее родителя, правый правее
        left_lines, right_lines = left.split("\n"), right.split("\n")
        self.assertLess(left_lines[2].index("3"), left_lines[0].index("5"))
        self.assertGreater(right_lines[2].index("8"), right_lines[0].index("5"))

    def test_inorder_left_to_right(self):
        """Подписи на рисунке слева направо идут в порядке inorder"""
        rnd = random.Random(11)
        for _ in range(100):
            tree = BinarySearchTree([rnd.randint(-99, 999) for _ in range(rnd.randint(1, 25))])
            lines = render_tree(tree.root).split("\n")
            found = sorted((m.start(), int(m.group()))
                           for line in lines[::2] for m in re.finditer(r"-?\d+", line))
            self.assertEqual([value for _, value in found], tree.inorder())

    def test_structure_random(self):
        """300 случайных деревьев с повторами и отрицательными: рисунок = структура дерева"""
        rnd = random.Random(5)
        for _ in range(300):
            self.check_picture([rnd.randint(-120, 1200) for _ in range(rnd.randint(1, 30))])

    def test_tree_not_modified(self):
        """После рисования узлы, значения и связи те же"""
        tree = BinarySearchTree(README_VALUES)
        before = {key: (node, left, right, node.value) for key, (node, left, right) in links(tree).items()}
        root = tree.root
        render_tree(tree.root)
        render_tree(tree.root)
        after = {key: (node, left, right, node.value) for key, (node, left, right) in links(tree).items()}
        self.assertIs(tree.root, root)
        self.assertEqual(before, after)
        self.assertEqual(run_all(tree)["preorder"], [41, 20, 11, 29, 26, 32, 29, 65, 91, 72])

    def test_deeper_than_recursion_limit(self):
        """Цепочки глубже лимита рекурсии рисуются без RecursionError"""
        n = sys.getrecursionlimit() + 200
        right = BinarySearchTree(range(n))
        lines = render_tree(right.root).split("\n")
        self.assertEqual(len(lines), 2 * n - 1)
        self.assertEqual(lines[-1].strip(), str(n - 1))
        self.assertTrue(all(line.strip() == "\\" for line in lines[1::2]))

        left = BinarySearchTree()           # связи вручную, как в TestLargeTrees
        left.root = node = Node(n)
        for value in range(n - 1, 0, -1):
            node.left = Node(value)
            node = node.left
        lines = render_tree(left.root).split("\n")
        self.assertEqual(len(lines), 2 * n - 1)
        self.assertEqual(lines[-1], "1")
        self.assertTrue(all(line.strip() == "/" for line in lines[1::2]))


class TestInsertionOrder(unittest.TestCase):
    """Числа вставляются в порядке ввода: первое – корень, сортировки нет."""

    def test_same_values_different_trees(self):
        """8 3 10 1 6 14 и 1 3 6 8 10 14 – одни и те же числа, но разные BST"""
        first = BinarySearchTree(SAMPLE_VALUES)
        second = BinarySearchTree(sorted(SAMPLE_VALUES))
        self.assertEqual(first.inorder(), second.inorder())
        self.assertNotEqual(shape(first.root), shape(second.root))
        self.assertEqual(render_tree(first.root), SAMPLE_PICTURE)
        self.assertEqual(render_tree(second.root), SORTED_PICTURE)
        self.assertEqual(first.preorder(), [8, 3, 1, 6, 10, 14])
        self.assertEqual(second.preorder(), [1, 3, 6, 8, 10, 14])

    def test_main_uses_input_order(self):
        """main рисует дерево, построенное вставками в порядке ввода"""
        for line, picture, preorder in (("8 3 10 1 6 14", SAMPLE_PICTURE, [8, 3, 1, 6, 10, 14]),
                                        ("1 3 6 8 10 14", SORTED_PICTURE, [1, 3, 6, 8, 10, 14])):
            console = FakeConsole(line)
            main(console.read, console.write)
            self.assertEqual(console.output[2], picture, line)
            self.assertEqual(console.output[4], f"{'preorder':<18} {preorder}", line)

    def test_first_value_is_root(self):
        """Корень рисунка – первое введенное число, даже если оно не наименьшее"""
        rnd = random.Random(3)
        for _ in range(100):
            values = [rnd.randint(-50, 50) for _ in range(rnd.randint(1, 15))]
            console = FakeConsole(" ".join(map(str, values)))
            main(console.read, console.write)
            top = re.findall(r"-?\d+", console.output[2].split("\n")[0])
            self.assertEqual(top, [str(values[0])], values)
            self.assertEqual(parse_picture(console.output[2]), shape(BinarySearchTree(values).root))

    def test_no_sorting(self):
        """Неотсортированный ввод не сортируется: рисунок не совпадает с рисунком sorted"""
        values = [5, 1, 9, 3, 7]
        console = FakeConsole("5 1 9 3 7")
        main(console.read, console.write)
        self.assertEqual(console.output[2], render_tree(BinarySearchTree(values).root))
        self.assertNotEqual(console.output[2], render_tree(BinarySearchTree(sorted(values)).root))
        self.assertEqual(parse_picture(console.output[2]),
                         (5, (1, None, (3, None, None)), (9, (7, None, None), None)))


class TestMainRender(unittest.TestCase):

    def test_output_order(self):
        """Сначала пустая строка и заголовок, потом рисунок, пустая строка и шесть обходов"""
        console = FakeConsole("8 3 10 1 6 14")
        main(console.read, console.write)
        tree = BinarySearchTree(SAMPLE_VALUES)
        self.assertEqual(console.output, ["", "Построенное дерево:", SAMPLE_PICTURE, ""]
                         + [f"{name:<18} {getattr(tree, name)()}" for name in TRAVERSALS])

    def test_script_sample(self):
        """Настоящий запуск python main.py на примере из условия"""
        result = run_script("8 3 10 1 6 14\n", "main.py")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stderr, "")
        self.assertEqual(result.stdout,
                         PROMPT + "\nПостроенное дерево:\n" + SAMPLE_PICTURE + "\n\n"
                         "preorder           [8, 3, 1, 6, 10, 14]\n"
                         "inorder            [1, 3, 6, 8, 10, 14]\n"
                         "postorder          [1, 6, 3, 14, 10, 8]\n"
                         "reverse_preorder   [8, 10, 14, 3, 6, 1]\n"
                         "reverse_inorder    [14, 10, 8, 6, 3, 1]\n"
                         "reverse_postorder  [14, 10, 6, 1, 3, 8]\n")

    def test_script_empty(self):
        result = run_script("\n", "main.py")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout,
                         PROMPT + "\nПостроенное дерево:\n(пустое дерево)\n\n"
                         + "".join(f"{name:<18} []\n" for name in TRAVERSALS))

    def test_eof_no_picture(self):
        """Прерванный ввод: дерево не рисуется"""
        console = FakeConsole()
        main(console.read, console.write)
        self.assertNotIn("Построенное дерево:", console.output)


if __name__ == "__main__":
    unittest.main()
