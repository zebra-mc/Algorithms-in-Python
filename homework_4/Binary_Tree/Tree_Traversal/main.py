# Домашняя работа 4. Задача 1. Tree Traversal
# Максим Царьков


class Node:
    """Узел дерева: значение и ссылки на левое и правое поддеревья."""

    def __init__(self, value, left=None, right=None):
        self.value = value
        self.left = left
        self.right = right


class BinarySearchTree:
    """Бинарное дерево поиска без балансировки.

    Равные значения уходят вправо, и каждое вставленное значение хранится
    в своем узле. Для любого узла все значения его левого поддерева меньше
    значения узла, а все значения правого - не меньше: left < node <= right.
    """

    def __init__(self, values=()):
        self.root = None
        for value in values:
            self.insert(value)

    def insert(self, value):
        """Добавляет value новым листом. Остальные связи дерева не меняются."""
        new_node = Node(value)
        if self.root is None:
            self.root = new_node
            return
        node = self.root
        while True:
            if value < node.value:
                if node.left is None:
                    node.left = new_node
                    return
                node = node.left
            else:
                if node.right is None:
                    node.right = new_node
                    return
                node = node.right

    def _traverse(self, order):
        """Обход в порядке order - строке из букв N, L, R, например "LRN".

        Рекурсии нет, вместо нее явный стек пар (node, ready). ready=False -
        узел еще надо разложить на части по order, ready=True - пора записать
        его значение. Возвращает новый список значений.
        """
        result = []
        stack = [(self.root, False)] if self.root is not None else []
        while stack:
            node, ready = stack.pop()
            if ready:
                result.append(node.value)
                continue
            # стек снимает элементы в обратном порядке, поэтому части кладем с конца order
            for part in reversed(order):
                if part == "N":
                    stack.append((node, True))
                else:
                    child = node.left if part == "L" else node.right
                    if child is not None:
                        stack.append((child, False))
        return result

    def preorder(self):
        """NLR: узел, левое поддерево, правое поддерево."""
        return self._traverse("NLR")

    def inorder(self):
        """LNR: левое поддерево, узел, правое. Для BST - значения по неубыванию."""
        return self._traverse("LNR")

    def postorder(self):
        """LRN: левое поддерево, правое поддерево, узел."""
        return self._traverse("LRN")

    def reverse_preorder(self):
        """NRL: узел, правое поддерево, левое поддерево."""
        return self._traverse("NRL")

    def reverse_inorder(self):
        """RNL: правое поддерево, узел, левое. Для BST - значения по невозрастанию."""
        return self._traverse("RNL")

    def reverse_postorder(self):
        """RLN: правое поддерево, левое поддерево, узел."""
        return self._traverse("RLN")


def render_tree(root):
    r"""Рисует дерево сверху вниз и возвращает строку без завершающего перевода строки.

           ___8_
          /     \
         _3_    10_
        /   \      \
        1   6      14

    Тот же алгоритм, что в задачах 2 и 3. Колонка узла – его место в симметричном
    обходе, поэтому все левое поддерево стоит левее узла, а правое правее: подписи
    не пересекаются при любой форме дерева. Левый ребенок соединяется знаком "/",
    правый – "\", так что единственного ребенка всегда видно, с какой он стороны.
    Дерево только читается. Рекурсии нет.
    """
    if root is None:
        return "(пустое дерево)"

    # 1. Симметричный обход со стеком: каждому узлу – колонка начала подписи
    start = {}
    column = 0
    stack, node = [], root
    while stack or node is not None:
        while node is not None:
            stack.append(node)
            node = node.left
        node = stack.pop()
        start[id(node)] = column
        column += len(str(node.value)) + 1           # подпись и пробел после нее
        node = node.right

    def center(node):
        return start[id(node)] + (len(str(node.value)) - 1) // 2

    # 2. Обход в ширину по уровням: строка подписей и строка связей на каждый уровень
    lines = []
    level = [root]
    while level:
        labels, links = {}, {}
        for node in level:
            label = str(node.value)
            x = start[id(node)]
            for i, ch in enumerate(label):
                labels[x + i] = ch
            if node.left is not None:
                for c in range(center(node.left) + 1, x):
                    labels[c] = "_"
                links[center(node.left)] = "/"
            if node.right is not None:
                for c in range(x + len(label), center(node.right)):
                    labels[c] = "_"
                links[center(node.right)] = "\\"
        for row in (labels, links):
            if row:
                lines.append("".join(row.get(c, " ") for c in range(max(row) + 1)))
        level = [child for node in level for child in (node.left, node.right) if child is not None]
    return "\n".join(lines)


TRAVERSALS = ("preorder", "inorder", "postorder",
              "reverse_preorder", "reverse_inorder", "reverse_postorder")

PROMPT = "Введите целые числа через пробел в порядке вставки в BST: "


def parse_values(text):
    """Строку вида "41 20 -5 0" превращает в список int в порядке ввода.

    Пустая строка или одни пробелы - пустой список. Если есть токены, которые
    не являются целыми числами, бросает ValueError со списком этих токенов.
    """
    values = []
    bad = []
    for token in text.split():
        try:
            values.append(int(token))
        except ValueError:
            bad.append(token)
    if bad:
        raise ValueError("не целые числа: " + ", ".join(bad))
    return values


def read_values(read=input, write=print):
    """Спрашивает числа, пока ввод не станет корректным. Возвращает список int.

    read и write - функции ввода и вывода, по умолчанию input и print;
    тесты подставляют вместо них свои. Если ввод закончился (EOF, Ctrl+D)
    или прерван (Ctrl+C), возвращает None.
    """
    while True:
        try:
            text = read(PROMPT)
        except (EOFError, KeyboardInterrupt):
            write()
            write("Ввод прерван.")
            return None
        try:
            return parse_values(text)
        except ValueError as error:
            write(f"Ошибка: {error}. Повторите ввод.")


def print_traversals(tree, write=print):
    """Печатает все шесть обходов: имя обхода, выровненное по ширине, и список."""
    for name in TRAVERSALS:
        write(f"{name:<18} {getattr(tree, name)()}")


def main(read=input, write=print):
    """Спрашивает числа, вставляет их в BST в порядке ввода, рисует дерево и печатает обходы."""
    values = read_values(read, write)
    if values is None:
        return
    tree = BinarySearchTree(values)
    write()
    write("Построенное дерево:")
    write(render_tree(tree.root))
    write()
    print_traversals(tree, write)


if __name__ == "__main__":
    main()
