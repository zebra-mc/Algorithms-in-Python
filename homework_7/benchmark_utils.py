"""Общая методика измерения времени для задач 1 и 3."""

import platform
import random
import statistics
import time

REPEATS = 7
SEED = 7
SIZES = (1_000, 10_000, 100_000)
CASES = [(kind, n) for kind in ("random", "reversed") for n in SIZES]
CASES += [(kind, SIZES[-1]) for kind in ("sorted", "equal")]


def make_input(kind, n):
    if kind == "random":
        rng = random.Random(SEED)
        return [rng.randrange(10 * n) for _ in range(n)]
    if kind == "reversed":
        return list(range(n, 0, -1))
    if kind == "sorted":
        return list(range(n))
    if kind == "equal":
        return [7] * n
    raise ValueError(f"неизвестный вид массива: {kind}")


def measure(algorithms, data, check, repeats=REPEATS):
    """Медиана замеров каждой функции; подготовка и проверка вне замера.

    check(work, result) проверяет результат после каждого вызова.
    Первый круг — прогрев; далее начальная функция меняется в каждом круге.
    """
    times = {algorithm.__name__: [] for algorithm in algorithms}
    for algorithm in algorithms:
        work = data.copy()
        check(work, algorithm(work))

    for step in range(repeats):
        for offset in range(len(algorithms)):
            algorithm = algorithms[(step + offset) % len(algorithms)]
            work = data.copy()
            start = time.perf_counter()
            result = algorithm(work)
            elapsed = time.perf_counter() - start
            check(work, result)
            times[algorithm.__name__].append(elapsed)
    return {name: statistics.median(values) for name, values in times.items()}


def environment():
    return (f"{platform.python_implementation()} {platform.python_version()}, "
            f"{platform.system()} {platform.machine()}")
