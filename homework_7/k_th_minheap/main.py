# Домашняя работа 7. Задача 2. K-th minheap
# Максим Царьков

import heapq

if not __package__:
    # Для python main.py из папки задачи нужен корень репозитория.
    import os
    import sys
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from homework_7.makeheap.main import makeheap, sift_down


def _validate_k(nums, k):
    if not isinstance(k, int) or isinstance(k, bool):
        raise TypeError("k должно быть целым числом (bool не допускается)")
    if not 1 <= k <= len(nums):
        raise ValueError(f"k должно быть от 1 до {len(nums)}, получено {k}")


def find_kth_largest(nums, k, log=None):
    """k-й по величине элемент: собственная minheap размера k.

    nums не меняется. Повторы считаются отдельными позициями.
    Некорректный диапазон k — ValueError, тип k — TypeError.
    log хранит (индекс, значение, действие, копия кучи); при построении
    первые два поля равны None.
    """
    _validate_k(nums, k)
    heap = [nums[i] for i in range(k)]
    makeheap(heap)
    if log is not None:
        log.append((None, None, "построение", heap.copy()))

    for i in range(k, len(nums)):
        value = nums[i]
        if heap[0] < value:
            heap[0] = value
            sift_down(heap, 0, k)
            action = "замена"
        else:
            action = "пропуск"
        if log is not None:
            log.append((i, value, action, heap.copy()))
    return heap[0]


def find_kth_largest_heapq(nums, k, log=None):
    """Тот же алгоритм, но операции с кучей выполняются через heapq."""
    _validate_k(nums, k)
    heap = [nums[i] for i in range(k)]
    heapq.heapify(heap)
    if log is not None:
        log.append((None, None, "построение", heap.copy()))

    for i in range(k, len(nums)):
        value = nums[i]
        if heap[0] < value:
            heapq.heapreplace(heap, value)
            action = "замена"
        else:
            action = "пропуск"
        if log is not None:
            log.append((i, value, action, heap.copy()))
    return heap[0]


def format_log(log):
    lines = ["| Шаг | Индекс | Элемент | Действие | Куча | Корень |",
             "|---|---|---|---|---|---|"]
    for step, (i, value, action, heap) in enumerate(log):
        index = "—" if i is None else i
        item = "—" if value is None else value
        lines.append(f"| {step} | {index} | {item} | {action} | `{heap}` | {heap[0]} |")
    return "\n".join(lines)


EXAMPLE = [3, 2, 3, 1, 2, 4, 2, 5, 5, 6, 0]
K = 4


def main():
    for algorithm in (find_kth_largest, find_kth_largest_heapq):
        log = []
        answer = algorithm(EXAMPLE, K, log=log)
        print(f"{algorithm.__name__}({EXAMPLE}, k={K}) = {answer}")
        print(format_log(log))
        print()


if __name__ == "__main__":
    main()
