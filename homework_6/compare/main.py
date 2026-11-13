# Домашняя работа 6. Задача 1. Compare
# Максим Царьков
#
# Запуск: python main.py из папки задачи или python -m homework_6.compare.main из корня

import functools
import random
import statistics
import time


def timer(func):
    """Декоратор: замеряет время каждого вызова func через time.perf_counter().

    Длительность последнего вызова в секундах хранится в атрибуте last_time
    обертки (None, пока вызовов не было). Результат и исключения func не
    меняются, время записывается и при выходе с исключением.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        try:
            return func(*args, **kwargs)
        finally:
            wrapper.last_time = time.perf_counter() - start

    wrapper.last_time = None
    return wrapper


def merge(left, right):
    """Слияние двух отсортированных списков в новый отсортированный список.

    При равенстве первым берется элемент из left (сравнение <=), поэтому
    слияние устойчиво.
    """
    result = []
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
    # Одна из частей закончилась, остаток другой уже отсортирован
    result.extend(left[i:])
    result.extend(right[j:])
    return result


def partition(arr, low, high):
    """Разбиение Ломуто отрезка arr[low..high] по опорному arr[high], как на лекции.

    После вызова arr[low..p-1] < pivot, arr[p] == pivot, arr[p+1..high] >= pivot.
    Возвращает p.
    """
    pivot = arr[high]
    i = low  # arr[low..i-1] - уже найденные элементы меньше pivot
    for j in range(low, high):
        if arr[j] < pivot:
            arr[i], arr[j] = arr[j], arr[i]
            i += 1
    arr[i], arr[high] = arr[high], arr[i]
    return i


@timer
def merge_sort(nums, log=None):
    """Рекурсивная сортировка слиянием. Возвращает новый список, nums не меняется.

    Если передан список log, в него в порядке выполнения пишутся
    ("call", глубина, часть) при входе в вызов и
    ("merge", глубина, left, right, результат) после слияния.
    """
    return _merge_sort(nums, 0, log)


def _merge_sort(nums, depth, log):
    if log is not None:
        log.append(("call", depth, list(nums)))
    if len(nums) <= 1:
        return list(nums)
    mid = len(nums) // 2
    left = _merge_sort(nums[:mid], depth + 1, log)
    right = _merge_sort(nums[mid:], depth + 1, log)
    result = merge(left, right)
    if log is not None:
        log.append(("merge", depth, left, right, result))
    return result


@timer
def quick_sort(nums, log=None):
    """Рекурсивная быстрая сортировка: pivot - последний элемент отрезка.

    Сортирует копию nums на месте и возвращает ее, nums не меняется.
    Если передан список log, после каждого partition в него пишется
    (глубина, low, high, pivot, p, копия массива).
    """
    arr = list(nums)
    _quick_sort(arr, 0, len(arr) - 1, 0, log)
    return arr


def _quick_sort(arr, low, high, depth, log):
    if low >= high:
        return
    pivot = arr[high]
    p = partition(arr, low, high)
    if log is not None:
        log.append((depth, low, high, pivot, p, arr.copy()))
    _quick_sort(arr, low, p - 1, depth + 1, log)
    _quick_sort(arr, p + 1, high, depth + 1, log)


# Визуализация

def format_array(arr, mark=None):
    """'1 2 (3) 4': элементы через пробел, элемент с индексом mark - в скобках."""
    return " ".join(f"({x})" if i == mark else str(x) for i, x in enumerate(arr))


def format_merge_log(log):
    """Дерево вызовов merge_sort: вход в вызов и, ниже детей, его слияние."""
    lines = []
    for kind, depth, *data in log:
        pad = "  " * depth
        if kind == "call":
            lines.append(f"{pad}{data[0]}")
        else:
            left, right, result = data
            lines.append(f"{pad}{left} + {right} -> {result}")
    return "\n".join(lines)


def format_quick_log(log):
    """Таблица разбиений quick_sort в порядке выполнения."""
    lines = ["| Шаг | Глубина | Отрезок | pivot | p | Массив после partition | Дальше |",
             "|---|---|---|---|---|---|---|"]
    for step, (depth, low, high, pivot, p, arr) in enumerate(log, 1):
        lines.append(f"| {step} | {depth} | [{low}, {high}] | {pivot} | {p} "
                     f"| `{format_array(arr, p)}` | [{low}, {p - 1}], [{p + 1}, {high}] |")
    return "\n".join(lines)


# Эксперимент

# Отсортированный массив дает рекурсию quick_sort глубины n. При стандартном
# пределе в 1000 кадров берем размеры с запасом, чтобы не было RecursionError
WORST_SIZES = (100, 300, 900)
RANDOM_SIZES = (900, 10_000, 100_000)
REPEATS = 7


def make_input(kind, n, seed=6):
    """Тестовый массив длины n одного из видов: random, sorted, reversed, equal."""
    if kind == "random":
        rng = random.Random(seed)
        return [rng.randrange(10 * n) for _ in range(n)]
    if kind == "sorted":
        return list(range(n))
    if kind == "reversed":
        return list(range(n, 0, -1))
    if kind == "equal":
        return [7] * n
    raise ValueError(f"неизвестный вид массива: {kind}")


def measure(sorts, data, repeats=REPEATS):
    """Медиана времени каждой сортировки на одном и том же data за repeats запусков.

    Запуски сортировок чередуются, чтобы фоновая нагрузка влияла на них
    одинаково. Результат последнего запуска сверяется с sorted() вне замера.
    """
    times = {sort.__name__: [] for sort in sorts}
    expected = sorted(data)
    for _ in range(repeats):
        for sort in sorts:
            result = sort(data)
            times[sort.__name__].append(sort.last_time)
            if result != expected:
                raise AssertionError(f"{sort.__name__} отсортировала неверно")
    return {name: statistics.median(values) for name, values in times.items()}


def benchmark(cases, repeats=REPEATS):
    """Строки (вид, n, время merge_sort, время quick_sort) для пар (вид, n)."""
    rows = []
    for kind, n in cases:
        data = make_input(kind, n)
        t = measure([merge_sort, quick_sort], data, repeats)
        rows.append((kind, n, t["merge_sort"], t["quick_sort"]))
    return rows


def format_benchmark(rows):
    lines = ["| Массив | n | merge_sort, мс | quick_sort, мс | quick / merge |",
             "|---|---|---|---|---|"]
    for kind, n, t_merge, t_quick in rows:
        lines.append(f"| {kind} | {n} | {t_merge * 1000:.2f} | {t_quick * 1000:.2f} "
                     f"| {t_quick / t_merge:.1f} |")
    return "\n".join(lines)


EXAMPLE = [5, 2, 7, 2, 9, 1, 2, 6]
BAD_EXAMPLE = [1, 2, 3, 4, 5, 6]


def main():
    log = []
    merge_sort(EXAMPLE, log=log)
    print(f"merge_sort({EXAMPLE}):")
    print(format_merge_log(log))

    log = []
    print(f"\nquick_sort({EXAMPLE}) -> {quick_sort(EXAMPLE, log=log)}")
    print(format_quick_log(log))

    log = []
    quick_sort(BAD_EXAMPLE, log=log)
    print(f"\nquick_sort({BAD_EXAMPLE}):")
    print(format_quick_log(log))

    cases = [(kind, n) for kind in ("random", "sorted", "reversed", "equal")
             for n in WORST_SIZES]
    cases += [("random", n) for n in RANDOM_SIZES if n not in WORST_SIZES]
    print(f"\nМедиана {REPEATS} запусков:")
    print(format_benchmark(benchmark(cases)))


if __name__ == "__main__":
    main()
