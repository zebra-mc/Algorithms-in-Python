# Домашняя работа 7. Задача 3. Heapsort
# Максим Царьков


def sift_down_max(arr, root, size):
    """Восстанавливает maxheap в поддереве root в пределах arr[:size].

    Поддеревья детей root уже являются maxheap. size исключает правую границу.
    """
    while 2 * root + 1 < size:
        child = 2 * root + 1
        right = child + 1
        if right < size and arr[child] < arr[right]:
            child = right
        if not arr[root] < arr[child]:
            break
        arr[root], arr[child] = arr[child], arr[root]
        root = child


def heapsort(arr, visit=None):
    """Сортирует arr по возрастанию на месте и возвращает тот же список.

    Без рекурсии и без вспомогательных массивов. Необязательный visit —
    наблюдатель для визуализации: (этап, индекс, размер кучи, arr).
    Сам алгоритм не делает копий, даже при переданном наблюдателе.
    """
    n = len(arr)
    for root in range(n // 2 - 1, -1, -1):
        sift_down_max(arr, root, n)
        if visit is not None:
            visit("build", root, n, arr)

    # Максимум уходит на место end. Хвост arr[end:] больше не трогаем.
    for end in range(n - 1, 0, -1):
        arr[0], arr[end] = arr[end], arr[0]
        sift_down_max(arr, 0, end)
        if visit is not None:
            visit("extract", end, end, arr)
    return arr


def trace_heapsort(arr):
    """Сортирует arr тем же heapsort и сохраняет состояния для отчета.

    Копии создаются только здесь, а не в сортировке.
    """
    log = []

    def record(phase, index, size, state):
        log.append((phase, index, size, state.copy()))

    heapsort(arr, visit=record)
    return log


def format_log(nums, log):
    lines = ["| Шаг | Действие | Активная часть | Отсортированный хвост |",
             "|---|---|---|---|", f"| 0 | начало | `{nums}` | `[]` |"]
    for step, (phase, index, size, arr) in enumerate(log, 1):
        action = (f"sift_down_max({index})" if phase == "build"
                  else f"обмен 0 и {index}, просеивание")
        lines.append(f"| {step} | {action} | `{arr[:size]}` | `{arr[size:]}` |")
    return "\n".join(lines)


EXAMPLE = [1, 4, 7, 9, 0, 3, 2, 1]


def main():
    arr = EXAMPLE.copy()
    log = trace_heapsort(arr)
    print(f"heapsort({EXAMPLE}) -> {arr}")
    print(format_log(EXAMPLE, log))


if __name__ == "__main__":
    main()
