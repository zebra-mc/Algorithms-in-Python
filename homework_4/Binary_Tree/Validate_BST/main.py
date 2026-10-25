# Домашняя работа 4. Задача 2. Validate BST
# Максим Царьков


class TreeNode:
    """Узел бинарного дерева."""

    def __init__(self, value, left=None, right=None):
        self.value = value
        self.left = left
        self.right = right


def check_steps(root):
    """Обход дерева с проверкой каждого узла на допустимый интервал.

    Выдает кортежи (node, low, high, ok): узел, его границы и результат
    проверки low < node.value < high. После первого ok == False обход
    заканчивается. Через этот генератор работают и is_valid_bst, и
    трассировка в README, поэтому они не могут разойтись.
    """
    # None – границы нет. Числовые "бесконечности" вроде -10**9 не подходят:
    # они отсекли бы допустимые большие по модулю значения
    stack = [(root, None, None)] if root is not None else []
    while stack:
        node, low, high = stack.pop()
        ok = (low is None or low < node.value) and (high is None or node.value < high)
        yield node, low, high, ok
        if not ok:
            return
        # правого кладем первым, чтобы левое поддерево проверялось раньше
        if node.right is not None:
            stack.append((node.right, node.value, high))
        if node.left is not None:
            stack.append((node.left, low, node.value))


def is_valid_bst(root):
    """True, если дерево с корнем root – BST со строгими неравенствами.

    В левом поддереве каждого узла все значения строго меньше его значения,
    в правом – строго больше. Пустое дерево (root is None) считается BST.
    """
    return all(ok for _, _, _, ok in check_steps(root))


if __name__ == "__main__":
    good = TreeNode(8,
                    TreeNode(3, TreeNode(1), TreeNode(6)),
                    TreeNode(10, None, TreeNode(14)))
    bad = TreeNode(15,
                   TreeNode(8, TreeNode(4), TreeNode(12, TreeNode(10), TreeNode(16))),
                   TreeNode(23, TreeNode(17), TreeNode(30)))
    print(is_valid_bst(good))    # True
    print(is_valid_bst(bad))     # False: 16 в левом поддереве корня 15
