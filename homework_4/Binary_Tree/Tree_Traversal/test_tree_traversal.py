"""Тесты к задаче 1 "Tree Traversal". Запуск: python -m unittest -v"""

import os
import random
import subprocess
import sys
import unittest
from collections import Counter

from main import PROMPT, BinarySearchTree, Node, main, parse_values, read_values

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
        self.assertEqual(PROMPT.strip(), "Введите целые числа через пробел:")

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
        self.assertEqual("\n".join(console.output) + "\n", README_OUTPUT)

    def test_empty(self):
        """Пустой ввод: пустое дерево, все шесть списков пустые"""
        console = FakeConsole("")
        main(console.read, console.write)
        self.assertEqual(console.output, [f"{name:<18} []" for name in TRAVERSALS])

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
        self.assertEqual(len(console.output), 7)
        self.assertIn("два", console.output[0])

    def test_eof_prints_nothing_else(self):
        console = FakeConsole()
        main(console.read, console.write)
        self.assertEqual(console.output, ["", "Ввод прерван."])


class TestScript(unittest.TestCase):
    """Настоящий запуск python main.py через stdin в отдельном процессе."""

    def test_readme_example(self):
        result = run_script("41 20 65 11 29 91 32 72 26 29\n", "main.py")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, PROMPT + README_OUTPUT)
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


if __name__ == "__main__":
    unittest.main()
