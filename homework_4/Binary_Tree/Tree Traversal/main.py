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


if __name__ == "__main__":
    tree = BinarySearchTree([41, 20, 65, 11, 29, 91, 32, 72, 26, 29])
    for name in ("preorder", "inorder", "postorder",
                 "reverse_preorder", "reverse_inorder", "reverse_postorder"):
        print(f"{name:<18} {getattr(tree, name)()}")
