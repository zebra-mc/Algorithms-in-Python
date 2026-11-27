"""Сравнение heapsort, sorted и merge_sort из ДЗ 6."""

if not __package__:
    import os
    import sys
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

try:
    from homework_6.compare.main import merge_sort
except ModuleNotFoundError as exc:
    # Без ДЗ 6 доступны только два сравниваемых алгоритма.
    if exc.name not in ("homework_6", "homework_6.compare", "homework_6.compare.main"):
        raise
    merge_sort = None

from homework_7.benchmark_utils import CASES, REPEATS, environment, make_input, measure
from homework_7.heapsort.main import heapsort


def benchmark(cases=CASES, repeats=REPEATS):
    algorithms = (heapsort, sorted)
    if merge_sort is not None:
        algorithms += (merge_sort,)
    rows = []
    for kind, n in cases:
        data = make_input(kind, n)
        expected = sorted(data)

        def check(work, result):
            if result != expected:
                raise AssertionError("некорректная сортировка")

        t = measure(algorithms, data, check, repeats)
        rows.append((kind, n, t["heapsort"], t["sorted"], t.get("merge_sort")))
    return rows


def format_benchmark(rows):
    lines = ["| Массив | n | heapsort, мс | sorted, мс | merge_sort, мс |",
             "|---|---:|---:|---:|---:|"]
    for kind, n, heap, builtin, merge in rows:
        merge_ms = "—" if merge is None else f"{merge * 1000:.3f}"
        lines.append(f"| {kind} | {n} | {heap * 1000:.3f} | {builtin * 1000:.3f} "
                     f"| {merge_ms} |")
    return "\n".join(lines)


def main():
    if merge_sort is None:
        print("Предупреждение: merge_sort из ДЗ 6 недоступна; сравниваются только "
              "heapsort и sorted. Для полного сравнения нужна папка homework_6 "
              "рядом с homework_7.")
    print(f"{environment()}, медиана {REPEATS} запусков")
    print(format_benchmark(benchmark()))


if __name__ == "__main__":
    main()
