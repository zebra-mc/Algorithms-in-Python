# Домашняя работа 5. Задача 3. AVL
# Максим Царьков


class AVLNode:
    """Узел AVL-дерева: ключ, дети и высота поддерева (лист – 1)."""

    def __init__(self, key):
        self.key = key
        self.left = None
        self.right = None
        self.height = 1


def height(node):
    """Высота поддерева: 0 для пустого, иначе сохраненная в узле."""
    return node.height if node is not None else 0


def update_height(node):
    """Пересчитывает высоту узла по уже верным высотам детей."""
    node.height = 1 + max(height(node.left), height(node.right))


def balance(node):
    """Баланс-фактор: высота левого поддерева минус высота правого."""
    return height(node.left) - height(node.right)


def rotate_right(y):
    r"""Правый поворот вокруг y; возвращает новый корень поддерева x.

          y              x
         / \            / \
        x   C   ->     A   y
       / \                / \
      A   B              B   C
    """
    x = y.left
    # B – единственное поддерево, меняющее родителя; переносим его до того,
    # как y станет ребенком x, иначе ссылка на B потеряется
    y.left = x.right
    x.right = y
    # y теперь ниже x, поэтому его высота считается первой
    update_height(y)
    update_height(x)
    return x


def rotate_left(x):
    r"""Левый поворот вокруг x – зеркальный rotate_right; возвращает новый корень y.

        x                  y
       / \                / \
      A   y      ->      x   C
         / \            / \
        B   C          A   B
    """
    y = x.right
    x.right = y.left
    y.left = x
    update_height(x)
    update_height(y)
    return y


def render_tree(root):
    r"""Рисует дерево сверху вниз и возвращает строку.

           ___20_
          /      \
         10_     30
            \
            15

    Колонка подписи – место узла в симметричном обходе, поэтому левое поддерево
    всегда левее узла, правое – правее, и подписи не пересекаются. Левый ребенок
    соединяется знаком "/", правый – "\". Тот же способ, что в ДЗ 4.
    """
    if root is None:
        return "(пустое дерево)"

    start = {}
    column = 0
    stack, node = [], root
    while stack or node is not None:
        while node is not None:
            stack.append(node)
            node = node.left
        node = stack.pop()
        start[id(node)] = column
        column += len(str(node.key)) + 1
        node = node.right

    def center(node):
        return start[id(node)] + (len(str(node.key)) - 1) // 2

    lines = []
    level = [root]
    while level:
        labels, links = {}, {}
        for node in level:
            label = str(node.key)
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


class AVL:
    """AVL-дерево уникальных ключей.

    insert(key) -> bool – True, если ключ добавлен; False, если он уже был
                          (дубликаты не хранятся, дерево не меняется).
    delete(key) -> bool – True, если ключ удален; False, если его не было.
    search(key) -> bool – есть ли ключ в дереве.
    inorder()   -> list – ключи по возрастанию.

    log – необязательный список: если передан, операции дописывают в него
    текстовые шаги (путь поиска, удаленный узел, дисбаланс, каждый поворот
    с рисунком поддерева). Нужен только для демонстрации и README.
    """

    def __init__(self, keys=(), log=None):
        self.root = None
        self.log = log
        for key in keys:
            self.insert(key)

    def __str__(self):
        return render_tree(self.root)

    def search(self, key):
        """Спуск от корня по правилу BST; дерево не меняется."""
        node = self.root
        path = []
        while node is not None and node.key != key:
            path.append(node.key)
            node = node.left if key < node.key else node.right
        found = node is not None
        if self.log is not None:
            path += [node.key] if found else ["пусто"]
            self.log.append(f"search({key}): {' -> '.join(map(str, path))} – "
                            + ("найден" if found else "не найден"))
        return found

    def insert(self, key):
        # Предварительный поиск – еще один путь O(log n), зато _insert не нужно
        # сообщать наверх, был ли ключ, и повторная вставка ничего не трогает
        if self._contains(key):
            return False
        self.root = self._insert(self.root, key)
        return True

    def delete(self, key):
        if not self._contains(key):
            return False
        self.root = self._delete(self.root, key)
        return True

    def inorder(self):
        result = []

        def visit(node):
            if node is not None:
                visit(node.left)
                result.append(node.key)
                visit(node.right)

        visit(self.root)
        return result

    def _contains(self, key):
        node = self.root
        while node is not None and node.key != key:
            node = node.left if key < node.key else node.right
        return node is not None

    def _insert(self, node, key):
        """Вставляет отсутствующий key в поддерево node; возвращает новый корень поддерева."""
        if node is None:
            return AVLNode(key)
        if key < node.key:
            node.left = self._insert(node.left, key)
        else:
            node.right = self._insert(node.right, key)
        return self._rebalance(node)

    def _delete(self, node, key):
        """Удаляет присутствующий key из поддерева node; возвращает новый корень поддерева."""
        if key < node.key:
            node.left = self._delete(node.left, key)
        elif key > node.key:
            node.right = self._delete(node.right, key)
        elif node.left is None or node.right is None:
            # Лист или один ребенок: на место узла встает ребенок (или None).
            # Его поддерево уже сбалансировано, и высота у него верная
            child = node.left if node.left is not None else node.right
            self._note(f"удален узел {key}: " + ("лист" if child is None else
                                                 f"на его место встал ребенок {child.key}"))
            return child
        else:
            # Два ребенка: ключ заменяется преемником – минимумом правого
            # поддерева. У преемника нет левого ребенка, поэтому его удаление
            # из правого поддерева – уже разобранный случай листа или одного ребенка
            successor = node.right
            while successor.left is not None:
                successor = successor.left
            self._note(f"у узла {key} два ребенка: ключ заменен преемником "
                       f"{successor.key}, дальше удаляется {successor.key} из правого поддерева")
            node.key = successor.key
            node.right = self._delete(node.right, successor.key)
        return self._rebalance(node)

    def _rebalance(self, node):
        """Обновляет высоту node и при |баланс| = 2 выполняет повороты; возвращает корень поддерева.

        Дети node к этому моменту уже сбалансированы и имеют верные высоты.
        """
        update_height(node)
        b = balance(node)
        if b > 1:
            # Баланс ребенка 0 бывает только после удаления; тогда одинарного
            # поворота достаточно, а двойной здесь ошибочен
            child = node.left
            case = "LL" if balance(child) >= 0 else "LR"
        elif b < -1:
            child = node.right
            case = "RR" if balance(child) <= 0 else "RL"
        else:
            return node

        self._note(f"дисбаланс в узле {node.key}: баланс {b:+d}, у ребенка "
                   f"{child.key} баланс {balance(child):+d} – случай {case}", node)
        if case == "LR":
            node.left = rotate_left(child)
            self._note(f"{case}, шаг 1: левый поворот вокруг {child.key}", node)
        elif case == "RL":
            node.right = rotate_right(child)
            self._note(f"{case}, шаг 1: правый поворот вокруг {child.key}", node)
        step = f"{case}, шаг 2: " if case in ("LR", "RL") else f"{case}: "
        if case in ("LL", "LR"):
            new_root = rotate_right(node)
            self._note(step + f"правый поворот вокруг {node.key}", new_root)
        else:
            new_root = rotate_left(node)
            self._note(step + f"левый поворот вокруг {node.key}", new_root)
        return new_root

    def _note(self, text, subtree=None):
        if self.log is not None:
            self.log.append(text if subtree is None else text + "\n" + render_tree(subtree))


def show(title, tree, action):
    """Печатает заголовок, выполняет action и печатает шаги из журнала и итоговое дерево."""
    print(f"=== {title} ===")
    tree.log.clear()
    action()
    for step in tree.log:
        print(step)
    # После поворота в корне последний шаг журнала уже рисует все дерево
    picture = str(tree)
    if not tree.log or not tree.log[-1].endswith("\n" + picture):
        print("итог:")
        print(picture)
    print()


def main():
    for case, keys in (("LL", [30, 20, 10]), ("RR", [10, 20, 30]),
                       ("LR", [30, 10, 20]), ("RL", [10, 30, 20])):
        tree = AVL(keys[:2], log=[])
        print(f"=== Вставка, случай {case}: {keys} ===")
        print(f"до вставки {keys[2]}:")
        print(tree)
        tree.insert(keys[2])
        print("\n".join(tree.log))
        print()

    small = AVL([20, 10, 30, 25, 40], log=[])
    print("=== Удаление, баланс ребенка 0: дерево [20, 10, 30, 25, 40] ===")
    print(small)
    print()
    show("delete(10)", small, lambda: small.delete(10))

    # Минимальное AVL-дерево высоты 5 (12 узлов): вставка по уровням, без поворотов
    tree = AVL([80, 30, 100, 20, 50, 90, 110, 10, 40, 60, 120, 70], log=[])
    print("=== Удаление с балансировкой на двух уровнях: дерево из 12 ключей ===")
    print(tree)
    print()
    show("delete(90)", tree, lambda: tree.delete(90))
    show("delete(50) – узел с двумя детьми", tree, lambda: tree.delete(50))

    print("=== Поиск ===")
    tree.log.clear()
    tree.search(40)
    tree.search(45)
    print("\n".join(tree.log))


if __name__ == "__main__":
    main()
