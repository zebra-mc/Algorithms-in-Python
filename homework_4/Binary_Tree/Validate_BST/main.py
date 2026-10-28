# Домашняя работа 4. Задача 2. Validate BST
# Максим Царьков

import sys
from collections import deque


class TreeNode:
    """Узел бинарного дерева."""

    def __init__(self, value, left=None, right=None):
        self.value = value
        self.left = left
        self.right = right


def check_steps(root):
    """Обход дерева с проверкой каждого узла на допустимый интервал.

    Выдает кортежи (node, low, high, ok): узел, его границы и результат
    проверки low <= node.value < high. Нижняя граница нестрогая (ее задает
    предок, в правом поддереве которого лежит узел, а там допустимы равные),
    верхняя строгая (ее задает предок, в левом поддереве которого лежит узел).
    После первого ok == False обход заканчивается. Через этот генератор
    работают и is_valid_bst, и трассировка в README, поэтому они не могут
    разойтись.
    """
    # None – границы нет. Числовые "бесконечности" вроде -10**9 не подходят:
    # они отсекли бы допустимые большие по модулю значения
    stack = [(root, None, None)] if root is not None else []
    while stack:
        node, low, high = stack.pop()
        ok = (low is None or low <= node.value) and (high is None or node.value < high)
        yield node, low, high, ok
        if not ok:
            return
        # правого кладем первым, чтобы левое поддерево проверялось раньше
        if node.right is not None:
            stack.append((node.right, node.value, high))
        if node.left is not None:
            stack.append((node.left, low, node.value))


def is_valid_bst(root):
    """True, если дерево с корнем root – BST в том же смысле, что в задаче 1.

    В левом поддереве каждого узла все значения строго меньше его значения,
    в правом – больше либо равны: left < node <= right. Повторы допустимы
    только справа. Пустое дерево (root is None) считается BST.
    """
    return all(ok for _, _, _, ok in check_steps(root))


# ---------------------------------------------------------------------------
# Построение произвольного дерева. insert() из задачи 1 здесь не используется:
# дерево собирается ровно таким, каким его задали, в том числе не BST.
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


# ---------------------------------------------------------------------------
# Пояснение результата
# ---------------------------------------------------------------------------

def explain(root):
    """Текстовое пояснение к ответу is_valid_bst(root): список строк."""
    if root is None:
        return ["Пустое дерево считается корректным BST."]
    *_, (node, low, high, ok) = check_steps(root)    # последний шаг проверки
    if ok:
        return ["Дерево является корректным BST: для каждого узла все значения "
                "левого поддерева меньше него, а правого – больше либо равны "
                "(left < node <= right)."]
    value = node.value
    where = f"Нарушение: узел {value} [{format_path(find_path(root, node))}]"
    if low is not None and value < low:
        reason = (f"лежит в правом поддереве узла {low}, поэтому должен быть >= {low}, "
                  f"а {value} < {low}.")
    elif value == high:
        reason = (f"лежит в левом поддереве узла {high}, поэтому должен быть < {high}; "
                  f"равные значения допускаются только в правом поддереве.")
    else:
        reason = (f"лежит в левом поддереве узла {high}, поэтому должен быть < {high}, "
                  f"а {value} > {high}.")
    return ["Дерево не является корректным BST.", f"{where} {reason}"]


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
    return f"{name} ребенок узла {parent.value} [{format_path(path)}]: "


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
    """Ввод дерева, его рисунок, результат is_valid_bst и пояснение."""
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
    write(f"Результат проверки: {is_valid_bst(root)}")
    for line in explain(root):
        write(line)


def demo(write=print):
    """Прежние демонстрационные примеры."""
    good = TreeNode(8,
                    TreeNode(3, TreeNode(1), TreeNode(6)),
                    TreeNode(10, None, TreeNode(14)))
    bad = TreeNode(15,
                   TreeNode(8, TreeNode(4), TreeNode(12, TreeNode(10), TreeNode(16))),
                   TreeNode(23, TreeNode(17), TreeNode(30)))
    write(is_valid_bst(good))    # True
    write(is_valid_bst(bad))     # False: 16 в левом поддереве корня 15
    write(is_valid_bst(TreeNode(5, None, TreeNode(5))))    # True: повтор справа
    write(is_valid_bst(TreeNode(5, TreeNode(5))))          # False: повтор слева


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
