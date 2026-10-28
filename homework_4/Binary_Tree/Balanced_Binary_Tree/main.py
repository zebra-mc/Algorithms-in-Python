# Домашняя работа 4. Задача 3. Balanced Binary Tree
# Максим Царьков

import sys
from collections import deque


class TreeNode:
    """Узел бинарного дерева: значение и ссылки на левого и правого ребенка."""

    def __init__(self, val, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


def postorder_heights(root):
    """Обходит дерево снизу вверх и для каждого узла выдает (node, h_left, h_right).

    Высота пустого дерева 0, листа 1. Узел выдается только после обоих его
    поддеревьев, высота самого узла считается из уже готовых высот детей.
    Рекурсии нет, поэтому глубина дерева не ограничена лимитом Python.
    """
    stack = [(root, False)]
    # высоты готовых поддеревьев, чей родитель еще не обработан;
    # правое поддерево заканчивается позже левого, поэтому лежит сверху
    heights = []
    while stack:
        node, children_done = stack.pop()
        if node is None:
            heights.append(0)
        elif children_done:
            h_right = heights.pop()
            h_left = heights.pop()
            yield node, h_left, h_right
            heights.append(1 + max(h_left, h_right))
        else:
            stack.append((node, True))
            stack.append((node.right, False))
            stack.append((node.left, False))


def is_balanced(root):
    """True, если у каждого узла высоты левого и правого поддеревьев отличаются не больше чем на 1."""
    for _, h_left, h_right in postorder_heights(root):
        if abs(h_left - h_right) > 1:
            # остальные узлы не нужны: генератор дальше не продвигается
            return False
    return True


# ---------------------------------------------------------------------------
# Построение произвольного дерева по уровням. Дерево собирается ровно таким,
# каким его задали: никакой вставки по правилам BST, значения могут быть любыми.
# ---------------------------------------------------------------------------

SIDES = (("left", "Левый", "Л"), ("right", "Правый", "П"))


def build_tree_bfs(get_value):
    """Строит дерево по уровням (обход в ширину) без рекурсии.

    get_value(parent, side, path) возвращает значение очередного узла или None,
    если узла нет. Для корня parent и side равны None. Для ребенка parent – уже
    созданный узел, side – "left" или "right", path – путь от корня до parent.
    Путь хранится связным списком (path_родителя, side), а у корня равен None:
    каждый узел добавляет к пути родителя O(1) памяти, а не копию длины h.
    Детей спрашивают слева направо для каждого узла в порядке очереди, поэтому
    ввод идет уровень за уровнем.
    """
    value = get_value(None, None, None)
    if value is None:
        return None
    root = TreeNode(value)
    queue = deque([(root, None)])
    while queue:
        node, path = queue.popleft()
        for side, _, _ in SIDES:
            value = get_value(node, side, path)
            if value is not None:
                child = TreeNode(value)
                setattr(node, side, child)
                queue.append((child, (path, side)))
    return root


def build_tree(level_order):
    """Дерево из списка значений по уровням, None – узла нет.

    Формат как у LeetCode: [10, 5, 15, None, None, 6, 20]. Нехватающие в конце
    None можно не писать. Если после построения остались значения, не попавшие
    в дерево, бросает ValueError.
    """
    values = iter(level_order)
    root = build_tree_bfs(lambda parent, side, path: next(values, None))
    extra = [value for value in values if value is not None]
    if extra:
        raise ValueError(f"лишние значения, которым нет места в дереве: {extra}")
    return root


def format_path(path):
    """Путь от корня для подсказки: "корень", "корень -> П -> Л" и т.п."""
    letters = {side: letter for side, _, letter in SIDES}
    parts = []
    while path is not None:          # идем от узла вверх, потом разворачиваем
        path, side = path
        parts.append(letters[side])
    return " -> ".join(["корень"] + parts[::-1])


def find_path(root, target):
    """Путь от корня до узла target (сравнение по объекту, а не по значению)."""
    queue = deque([(root, None)] if root is not None else [])
    while queue:
        node, path = queue.popleft()
        if node is target:
            return path
        for side, _, _ in SIDES:
            child = getattr(node, side)
            if child is not None:
                queue.append((child, (path, side)))
    raise ValueError("узла нет в дереве")


# ---------------------------------------------------------------------------
# Визуализация
# ---------------------------------------------------------------------------

def render_tree(root):
    """Рисует дерево сверху вниз и возвращает строку без завершающего перевода строки.

         _10___
        /      \
        5     _15_
             /    \
             6    20

    Колонка узла – его место в симметричном обходе, поэтому все левое поддерево
    стоит левее узла, а правое правее: подписи не пересекаются при любой форме
    дерева. Левый ребенок соединяется знаком "/", правый – "\", так что
    единственного ребенка всегда видно, с какой он стороны. Рекурсии нет.
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
        column += len(str(node.val)) + 1             # подпись и пробел после нее
        node = node.right

    def center(node):
        return start[id(node)] + (len(str(node.val)) - 1) // 2

    # 2. Обход в ширину по уровням: строка подписей и строка связей на каждый уровень
    lines = []
    level = [root]
    while level:
        labels, links = {}, {}
        for node in level:
            label = str(node.val)
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


# ---------------------------------------------------------------------------
# Пояснение результата
# ---------------------------------------------------------------------------

def first_violation(root):
    """Первый несбалансированный узел в том порядке, в котором его находит is_balanced.

    Возвращает (node, h_left, h_right) или None, если нарушений нет. Работает
    через тот же генератор postorder_heights и так же останавливается на первом
    нарушении, поэтому пояснение не может разойтись с ответом is_balanced.
    """
    for node, h_left, h_right in postorder_heights(root):
        if abs(h_left - h_right) > 1:
            return node, h_left, h_right
    return None


def explain(root):
    """Текстовое пояснение к ответу is_balanced(root): список строк."""
    if root is None:
        return ["Пустое дерево считается сбалансированным: в нем нет ни одного узла, "
                "у которого могло бы нарушиться условие."]
    violation = first_violation(root)
    if violation is None:
        return ["Дерево сбалансировано: для каждого узла высоты левого и правого "
                "поддеревьев отличаются не больше чем на 1."]
    node, h_left, h_right = violation
    return ["Дерево не сбалансировано.",
            f"Нарушение: узел {node.val} [{format_path(find_path(root, node))}] – высота "
            f"левого поддерева {h_left}, правого {h_right}, разность "
            f"{abs(h_left - h_right)} > 1."]


# ---------------------------------------------------------------------------
# Взаимодействие с пользователем
# ---------------------------------------------------------------------------

EMPTY = "-"


def parse_value(text):
    """Значение узла из строки: int или None, если введен "-" (узла нет).

    Пробелы по краям игнорируются. Для всего остального, что не является одним
    целым числом, бросает ValueError с понятным сообщением.
    """
    text = text.strip()
    if text == EMPTY:
        return None
    try:
        return int(text)
    except ValueError:
        shown = f"'{text}'" if text else "пустая строка"
        raise ValueError(f"{shown} – не целое число и не '{EMPTY}'") from None


def node_prompt(parent, side, path):
    """Текст запроса. Путь от корня делает его однозначным и при одинаковых значениях."""
    if parent is None:
        return f"Введите значение корня ('{EMPTY}' – пустое дерево): "
    name = {s: word for s, word, _ in SIDES}[side]
    return f"{name} ребенок узла {parent.val} [{format_path(path)}]: "


class InputInterrupted(Exception):
    """Ввод закончился (EOF, Ctrl+D) или прерван (Ctrl+C)."""


def read_value(prompt, read=None, write=print):
    """Спрашивает значение, пока ввод не станет корректным. Возвращает int или None.

    read=None значит встроенный input. Он берется в момент вызова, а не при
    определении функции, поэтому unittest.mock.patch("builtins.input") работает.
    """
    read = input if read is None else read
    while True:
        try:
            text = read(prompt)
        except (EOFError, KeyboardInterrupt):
            raise InputInterrupted from None
        try:
            return parse_value(text)
        except ValueError as error:
            write(f"Ошибка: {error}. Введите целое число (например, 7, 0, -3) "
                  f"или '{EMPTY}', если узла нет. Повторите ввод.")


def read_tree(read=None, write=print):
    """Интерактивно строит дерево по уровням. None, если дерево пустое.

    read и write – функции ввода и вывода, по умолчанию input и print;
    тесты подставляют вместо них свои.
    """
    return build_tree_bfs(
        lambda parent, side, path: read_value(node_prompt(parent, side, path), read, write))


def interactive(read=None, write=print):
    """Ввод дерева, его рисунок, результат is_balanced и пояснение."""
    write("Постройте бинарное дерево по уровням. Значения – целые числа (можно "
          f"отрицательные и 0), '{EMPTY}' – узла нет.")
    write("В квадратных скобках – путь от корня к узлу: Л – влево, П – вправо.")
    try:
        root = read_tree(read, write)
    except InputInterrupted:
        write()
        write("Ввод прерван.")
        return
    write()
    write("Построенное дерево:")
    write(render_tree(root))
    write()
    write(f"Результат проверки: {is_balanced(root)}")
    for line in explain(root):
        write(line)


def demo(write=print):
    """Прежние демонстрационные примеры (деревья из README)."""
    # у корня высоты 3 и 3, но узел 15 несбалансирован
    unbalanced = TreeNode(10,
                          TreeNode(5, TreeNode(3, TreeNode(1)), TreeNode(8)),
                          TreeNode(15, None, TreeNode(18, None, TreeNode(20))))
    balanced = TreeNode(1,
                        TreeNode(2, TreeNode(4, TreeNode(7)), TreeNode(5)),
                        TreeNode(3, None, TreeNode(6)))
    write(is_balanced(unbalanced))    # False
    write(is_balanced(balanced))      # True


USAGE = "Использование: python main.py          интерактивный ввод дерева\n" \
        "               python main.py --demo   демонстрационные примеры"


def main(argv=None, read=None, write=print):
    args = sys.argv[1:] if argv is None else argv
    if not args:
        interactive(read, write)
    elif args == ["--demo"]:
        demo(write)
    else:
        write(USAGE)


if __name__ == "__main__":
    main()
