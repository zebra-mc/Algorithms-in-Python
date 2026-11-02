# Домашняя работа 5. Задача 2. Permutations
# Максим Царьков
#
# Запуск: python main.py из папки задачи или python -m homework_5.permutations.main из корня

import os
import sys

try:
    from homework_5.tracer.main import tracer
except ModuleNotFoundError:
    # python main.py из папки задачи: корня репозитория нет в пути поиска модулей.
    # Добавляем его, чтобы взять tracer из задачи 1, а не держать здесь копию
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    from homework_5.tracer.main import tracer


def permute(nums: list[int], trace: bool = False) -> list[list[int]]:
    """Все различные перестановки nums; сам nums не изменяется.

    Поиск с возвратом: path – начало строящейся перестановки, used[i] – стоит ли
    уже nums[i] в path. Равные значения ставятся в path строго в порядке их
    индексов, поэтому при повторах в nums одинаковые перестановки не возникают.
    Для различных значений порядок результата – как в примере из условия.

    При trace=True рекурсивные вызовы печатает декоратор tracer из задачи 1.
    """
    n = len(nums)
    # prev[i] – индекс ближайшего левее элемента, равного nums[i], или -1
    prev = [max((j for j in range(i) if nums[j] == nums[i]), default=-1)
            for i in range(n)]
    used = [False] * n
    result = []

    def backtrack(path):
        """Добавляет в result все перестановки, начинающиеся с path; возвращает их число."""
        if len(path) == n:
            result.append(path.copy())
            return 1
        found = 0
        for i in range(n):
            # Равный nums[i] элемент левее еще свободен: ветка с nums[i] на этом
            # месте совпала бы с уже пройденной веткой для левого элемента
            if used[i] or (prev[i] != -1 and not used[prev[i]]):
                continue
            used[i] = True
            path.append(nums[i])
            found += backtrack(path)
            path.pop()
            used[i] = False
        return found

    # Рекурсивный вызов внутри backtrack берет имя из замыкания, поэтому после
    # подмены через tracer проходят все вложенные вызовы, а не только первый
    if trace:
        backtrack = tracer(backtrack)
    backtrack([])
    return result


def main():
    print("Трассировка permute([1, 2, 3], trace=True):")
    result = permute([1, 2, 3], trace=True)
    print(f"Результат: {result}")
    print()
    for nums in ([0, 1], [1], [], [1, 1, 2]):
        print(f"permute({nums}) = {permute(nums)}")


if __name__ == "__main__":
    main()
