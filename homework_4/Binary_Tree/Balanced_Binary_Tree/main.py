# Домашняя работа 4. Задача 3. Balanced Binary Tree
# Максим Царьков


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


if __name__ == "__main__":
    # пример из README: у корня высоты 3 и 3, но узел 15 несбалансирован
    unbalanced = TreeNode(10,
                          TreeNode(5, TreeNode(3, TreeNode(1)), TreeNode(8)),
                          TreeNode(15, None, TreeNode(18, None, TreeNode(20))))
    balanced = TreeNode(1,
                        TreeNode(2, TreeNode(4, TreeNode(7)), TreeNode(5)),
                        TreeNode(3, None, TreeNode(6)))
    print(is_balanced(unbalanced))
    print(is_balanced(balanced))
