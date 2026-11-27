# Домашняя работа 7. Задача 1. Makeheap
# Максим Царьков


def sift_up(arr, index):
    """Восстанавливает minheap после добавления элемента в конец кучи."""
    while index > 0:
        parent = (index - 1) // 2
        if not arr[index] < arr[parent]:
            break
        arr[parent], arr[index] = arr[index], arr[parent]
        index = parent


def sift_down(arr, root, size):
    """Восстанавливает minheap в поддереве root внутри arr[:size].

    Предусловие: поддеревья детей root уже являются minheap.
    size — исключительная правая граница кучи.
    """
    while 2 * root + 1 < size:
        child = 2 * root + 1
        right = child + 1
        if right < size and arr[right] < arr[child]:
            child = right
        if not arr[child] < arr[root]:
            break
        arr[root], arr[child] = arr[child], arr[root]
        root = child


def makeheap_n_log_n(arr, log=None):
    """Строит minheap на месте последовательным sift_up, возвращает arr.

    log, если передан, хранит (индекс добавленного элемента, состояние arr).
    """
    for index in range(1, len(arr)):
        sift_up(arr, index)
        if log is not None:
            log.append((index, arr.copy()))
    return arr


def makeheap(arr, log=None):
    """Строит minheap на месте снизу вверх за O(n), возвращает arr.

    log, если передан, хранит (корень обработанного поддерева, состояние arr).
    """
    n = len(arr)
    # Индексы от n // 2 до n - 1 — листья, просеивать их не нужно.
    for root in range(n // 2 - 1, -1, -1):
        sift_down(arr, root, n)
        if log is not None:
            log.append((root, arr.copy()))
    return arr


def format_log(nums, log, bottom_up=False):
    """Таблица состояний после каждого просеивания."""
    lines = ["| Шаг | Действие | Массив |", "|---|---|---|",
             f"| 0 | начало | `{nums}` |"]
    for step, (index, arr) in enumerate(log, 1):
        if bottom_up:
            action = f"sift_down({index})"
            state = str(arr)
        else:
            action = f"sift_up({index})"
            # Слева от черты — уже построенная куча.
            state = f"{arr[:index + 1]} / {arr[index + 1:]}"
        lines.append(f"| {step} | {action} | `{state}` |")
    return "\n".join(lines)


EXAMPLE = [9, 4, 7, 1, 0, 3, 2, 1]


def main():
    for algorithm in (makeheap_n_log_n, makeheap):
        log = []
        arr = EXAMPLE.copy()
        algorithm(arr, log=log)
        print(f"{algorithm.__name__}({EXAMPLE}) -> {arr}")
        print(format_log(EXAMPLE, log, bottom_up=algorithm is makeheap))
        print()


if __name__ == "__main__":
    main()
