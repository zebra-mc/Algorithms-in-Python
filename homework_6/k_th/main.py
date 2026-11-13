# Домашняя работа 6. Задача 3. K-th
# Максим Царьков
#
# Запуск: python main.py из папки задачи или python -m homework_6.k_th.main из корня


def partition3(arr, low, high, pivot):
    """Трехчастное разбиение arr[low..high] относительно значения pivot.

    После вызова arr[low..lt-1] < pivot, arr[lt..gt] == pivot,
    arr[gt+1..high] > pivot. Возвращает (lt, gt).
    """
    lt, i, gt = low, low, high
    # arr[low..lt-1] < pivot, arr[lt..i-1] == pivot, arr[i..gt] еще не просмотрены,
    # arr[gt+1..high] > pivot
    while i <= gt:
        if arr[i] < pivot:
            arr[lt], arr[i] = arr[i], arr[lt]
            lt += 1
            i += 1
        elif arr[i] > pivot:
            # i не сдвигается: пришедший с позиции gt элемент еще не просмотрен
            arr[i], arr[gt] = arr[gt], arr[i]
            gt -= 1
        else:
            i += 1
    return lt, gt


def find_kth_largest(nums, k, log=None):
    """k-й по величине элемент nums (k с единицы, повторы - отдельные позиции).

    Итеративный quickselect: pivot - средний элемент текущего отрезка, разбиение
    трехчастное. Работает с копией, nums не меняется. При k < 1, k > len(nums)
    (в том числе при пустом nums) - ValueError.

    Если передан список log, после каждого разбиения в него пишется
    (low, high, pivot, lt, gt, копия массива).
    """
    n = len(nums)
    if not 1 <= k <= n:
        raise ValueError(f"k должно быть от 1 до {n}, получено {k}")
    arr = list(nums)
    # k-й по величине стоит на позиции n - k отсортированного по возрастанию массива
    target = n - k
    low, high = 0, n - 1
    while True:
        pivot = arr[(low + high) // 2]
        lt, gt = partition3(arr, low, high, pivot)
        if log is not None:
            log.append((low, high, pivot, lt, gt, arr.copy()))
        if target < lt:
            high = lt - 1
        elif target > gt:
            low = gt + 1
        else:
            return pivot


def format_log(log, target):
    """Таблица шагов quickselect; в массиве отмечен блок равных pivot элементов."""
    lines = ["| Шаг | low | high | pivot | lt..gt | target | Массив после разбиения | Дальше |",
             "|---|---|---|---|---|---|---|---|"]
    for step, (low, high, pivot, lt, gt, arr) in enumerate(log, 1):
        if target < lt:
            decision = f"влево: high = {lt - 1}"
        elif target > gt:
            decision = f"вправо: low = {gt + 1}"
        else:
            decision = f"ответ {pivot}"
        cells = [str(x) for x in arr]
        cells[lt] = "[" + cells[lt]
        cells[gt] += "]"
        lines.append(f"| {step} | {low} | {high} | {pivot} | {lt}..{gt} | {target} "
                     f"| `{' '.join(cells)}` | {decision} |")
    return "\n".join(lines)


EXAMPLES = [
    ([3, 2, 1, 5, 6, 4], 2),
    ([3, 2, 3, 1, 2, 4, 5, 5, 6], 4),
    ([5, 5, 3, 1], 2),
]


def main():
    for nums, k in EXAMPLES:
        log = []
        answer = find_kth_largest(nums, k, log=log)
        print(f"find_kth_largest({nums}, k={k}) = {answer}, target = {len(nums) - k}")
        print(format_log(log, len(nums) - k))
        print()


if __name__ == "__main__":
    main()
