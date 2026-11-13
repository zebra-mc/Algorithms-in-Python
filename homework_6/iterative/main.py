# Домашняя работа 6. Задача 2. Iterative
# Максим Царьков
#
# Запуск: python main.py из папки задачи или python -m homework_6.iterative.main из корня

import os
import sys

try:
    from homework_6.compare.main import format_array, merge, partition
except ModuleNotFoundError:
    # python main.py из папки задачи: корня репозитория нет в пути поиска модулей.
    # Добавляем его, чтобы взять merge и partition из задачи 1, а не держать копию
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    from homework_6.compare.main import format_array, merge, partition


def merge_sort_iterative(nums, log=None):
    """Сортировка слиянием снизу вверх. Возвращает новый список, nums не меняется.

    Сначала массив - это блоки длины 1, на каждом проходе соседние блоки
    длины width сливаются в блоки длины 2 * width. Если передан список log,
    после каждого прохода в него пишется (width, массив после прохода).
    """
    result = list(nums)
    n = len(result)
    width = 1
    while width < n:
        merged = []
        for start in range(0, n, 2 * width):
            # Правый блок у последней пары может быть короче или пустым
            merged.extend(merge(result[start:start + width],
                                result[start + width:start + 2 * width]))
        result = merged
        if log is not None:
            log.append((width, result.copy()))
        width *= 2
    return result


def quick_sort_iterative(nums, log=None):
    """Быстрая сортировка с явным стеком отрезков вместо рекурсии.

    Тот же partition, что в задаче 1 (pivot - последний элемент отрезка).
    В стеке лежат пары (low, high) еще не отсортированных отрезков длины >= 2.
    После разбиения больший отрезок кладется в стек первым, меньший вторым,
    поэтому следующим берется меньший; так в стеке не больше log2(n) пар.
    Возвращает отсортированную копию nums.

    Если передан список log, на каждом шаге в него пишется
    (стек до извлечения, low, high, pivot, p, массив после partition, добавленные отрезки).
    """
    arr = list(nums)
    stack = [(0, len(arr) - 1)] if len(arr) > 1 else []
    while stack:
        before = list(stack) if log is not None else None
        low, high = stack.pop()
        pivot = arr[high]
        p = partition(arr, low, high)
        left, right = (low, p - 1), (p + 1, high)
        if p - low < high - p:
            left, right = right, left  # теперь left - больший из двух отрезков
        pushed = [part for part in (left, right) if part[0] < part[1]]
        stack.extend(pushed)
        if log is not None:
            log.append((before, low, high, pivot, p, arr.copy(), pushed))
    return arr


# Визуализация

def format_blocks(arr, size):
    """'2 5 | 2 7 | 1': элементы через пробел, блоки длины size разделены чертой."""
    return " | ".join(" ".join(map(str, arr[i:i + size])) for i in range(0, len(arr), size))


def format_merge_log(nums, log):
    """Массив до сортировки и после каждого прохода, с границами слитых блоков."""
    lines = [f"начало:      {format_blocks(nums, 1)}"]
    for width, arr in log:
        lines.append(f"{f'width = {width}:':<13}{format_blocks(arr, 2 * width)}")
    return "\n".join(lines)


def format_ranges(ranges):
    return " ".join(f"[{low}, {high}]" for low, high in ranges) or "-"


def format_quick_log(log):
    lines = ["| Шаг | Стек до шага | Извлечен | pivot | p | Массив после partition | В стек |",
             "|---|---|---|---|---|---|---|"]
    for step, (before, low, high, pivot, p, arr, pushed) in enumerate(log, 1):
        lines.append(f"| {step} | {format_ranges(before)} | [{low}, {high}] | {pivot} | {p} "
                     f"| `{format_array(arr, p)}` | {format_ranges(pushed)} |")
    return "\n".join(lines)


MERGE_EXAMPLE = [5, 2, 7, 2, 9, 1, 2, 6, 3]
QUICK_EXAMPLE = [5, 2, 7, 2, 9, 1, 2, 6]
BAD_EXAMPLE = [1, 2, 3, 4, 5, 6]


def main():
    log = []
    result = merge_sort_iterative(MERGE_EXAMPLE, log=log)
    print(f"merge_sort_iterative({MERGE_EXAMPLE}) -> {result}")
    print(format_merge_log(MERGE_EXAMPLE, log))
    for example in (QUICK_EXAMPLE, BAD_EXAMPLE):
        log = []
        result = quick_sort_iterative(example, log=log)
        print(f"\nquick_sort_iterative({example}) -> {result}")
        print(format_quick_log(log))


if __name__ == "__main__":
    main()
