"""Сравнение heapsort, sorted и merge_sort из ДЗ 6."""

if not __package__:
    import os
    import sys
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from homework_6.compare.main import merge_sort
from homework_7.benchmark_utils import CASES, REPEATS, environment, make_input, measure
from homework_7.heapsort.main import heapsort


def benchmark(cases=CASES, repeats=REPEATS):
    rows = []
    for kind, n in cases:
        data = make_input(kind, n)
        expected = sorted(data)

        def check(work, result):
            if result != expected:
                raise AssertionError("некорректная сортировка")

        t = measure((heapsort, sorted, merge_sort), data, check, repeats)
        rows.append((kind, n, t["heapsort"], t["sorted"], t["merge_sort"]))
    return rows


def format_benchmark(rows):
    lines = ["| Массив | n | heapsort, мс | sorted, мс | merge_sort, мс |",
             "|---|---:|---:|---:|---:|"]
    for kind, n, heap, builtin, merge in rows:
        lines.append(f"| {kind} | {n} | {heap * 1000:.3f} | {builtin * 1000:.3f} "
                     f"| {merge * 1000:.3f} |")
    return "\n".join(lines)


def main():
    print(f"{environment()}, медиана {REPEATS} запусков")
    print(format_benchmark(benchmark()))


if __name__ == "__main__":
    main()
