"""Сравнение времени двух методов построения minheap."""

if not __package__:
    import os
    import sys
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from homework_7.benchmark_utils import CASES, REPEATS, environment, make_input, measure
from homework_7.makeheap.main import makeheap, makeheap_n_log_n


def benchmark(cases=CASES, repeats=REPEATS):
    rows = []
    for kind, n in cases:
        data = make_input(kind, n)
        expected = sorted(data)

        def check(work, result):
            if (result is not work or sorted(work) != expected or
                    any(work[i] < work[(i - 1) // 2] for i in range(1, len(work)))):
                raise AssertionError("некорректная куча")

        t = measure((makeheap_n_log_n, makeheap), data, check, repeats)
        rows.append((kind, n, t["makeheap_n_log_n"], t["makeheap"]))
    return rows


def format_benchmark(rows):
    lines = ["| Массив | n | makeheap_n_log_n, мс | makeheap, мс | Отношение |",
             "|---|---:|---:|---:|---:|"]
    for kind, n, slow, fast in rows:
        lines.append(f"| {kind} | {n} | {slow * 1000:.3f} | {fast * 1000:.3f} "
                     f"| {slow / fast:.2f} |")
    return "\n".join(lines)


def main():
    print(f"{environment()}, медиана {REPEATS} запусков")
    print(format_benchmark(benchmark()))


if __name__ == "__main__":
    main()
