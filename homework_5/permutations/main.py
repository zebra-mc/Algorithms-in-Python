# Домашняя работа 5. Задача 2. Permutations
# Максим Царьков
#
# Запуск: python main.py из папки задачи или python -m homework_5.permutations.main из корня

import math
import os
import sys
from collections import Counter

try:
    from homework_5.tracer.main import tracer
except ModuleNotFoundError:
    # python main.py из папки задачи: корня репозитория нет в пути поиска модулей.
    # Добавляем его, чтобы взять tracer из задачи 1, а не держать здесь копию
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    from homework_5.tracer.main import tracer


def permute(nums: list[int], trace: bool = False) -> list[list[int]]:
    """Все различные перестановки nums; сам nums не изменяется.

    Поиск с возвратом: path – начало строящейся перестановки, used[i] – стоит ли
    уже nums[i] в path. Равные значения ставятся в path строго в порядке их
    индексов, поэтому при повторах в nums одинаковые перестановки не возникают.
    Для различных значений порядок результата – как в примере из условия.

    При trace=True рекурсивные вызовы печатает декоратор tracer из задачи 1.
    """
    n = len(nums)
    # prev[i] – индекс ближайшего левее элемента, равного nums[i], или -1
    prev = [max((j for j in range(i) if nums[j] == nums[i]), default=-1)
            for i in range(n)]
    used = [False] * n
    result = []

    def backtrack(path):
        """Добавляет в result все перестановки, начинающиеся с path; возвращает их число."""
        if len(path) == n:
            result.append(path.copy())
            return 1
        found = 0
        for i in range(n):
            # Равный nums[i] элемент левее еще свободен: ветка с nums[i] на этом
            # месте совпала бы с уже пройденной веткой для левого элемента
            if used[i] or (prev[i] != -1 and not used[prev[i]]):
                continue
            used[i] = True
            path.append(nums[i])
            found += backtrack(path)
            path.pop()
            used[i] = False
        return found

    # Рекурсивный вызов внутри backtrack берет имя из замыкания, поэтому после
    # подмены через tracer проходят все вложенные вызовы, а не только первый
    if trace:
        backtrack = tracer(backtrack)
    backtrack([])
    return result


# Ниже – только консольный интерфейс; на permute() эти пороги не влияют.
# Больше LARGE_N элементов: до вычисления спрашиваем, выводить ли все перестановки
# (при 9 различных их уже 362 880). Больше TRACE_WARN_N: перед трассировкой
# предупреждаем, сколько в ней может быть строк.
LARGE_N = 8
TRACE_WARN_N = 4


def ask(prompt):
    """input(prompt); None, если ввод закрыт (Ctrl+D/Ctrl+Z) или прерван (Ctrl+C)."""
    try:
        return input(prompt)
    except (EOFError, KeyboardInterrupt):
        print()
        return None


def is_yes(answer):
    """Ответ 'д' (или 'да', 'y', 'yes'); Enter, 'н' и все остальное – нет."""
    return answer is not None and answer.strip().lower() in ("д", "да", "y", "yes")


def parse_numbers(line):
    """'1 -2 0' -> [1, -2, 0]; пустая строка -> []. ValueError с первым неверным токеном."""
    nums = []
    for token in line.split():
        try:
            nums.append(int(token))
        except ValueError:
            raise ValueError(token) from None
    return nums


def count_permutations(nums):
    """Число различных перестановок: n! / (k₁! · … · k_m!), без их построения."""
    count = math.factorial(len(nums))
    for k in Counter(nums).values():
        count //= math.factorial(k)
    return count


def main():
    line = ask("Введите числа через пробел: ")
    if line is None:
        return
    try:
        nums = parse_numbers(line)
    except ValueError as exc:
        print(f"Ошибка: '{exc}' – не целое число. Нужны целые числа через пробел, "
              f"например: 1 2 3")
        return

    total = count_permutations(nums)
    if len(nums) > LARGE_N:
        total_text = f"{total:,}".replace(",", " ")
        print(f"\nВнимание: {len(nums)} элементов дают {total_text} перестановок "
              f"(число растет как n!), вычисление и вывод займут много времени и памяти.")
        if not is_yes(ask("Продолжить? (д/н): ")):
            return

    print("\nПерестановки:")
    for p in permute(nums):
        print(p)
    print(f"Всего: {total}")

    if len(nums) > TRACE_WARN_N:
        # Для различных значений вызовов Σ n!/(n-k)!, по две строки на вызов;
        # с повторами строк меньше, так что это оценка сверху
        lines = 2 * sum(math.perm(len(nums), k) for k in range(len(nums) + 1))
        print(f"\nВнимание: трассировка для {len(nums)} элементов – до {lines} строк.")
    if not is_yes(ask("\nПоказать стек вызовов? (д/н): ")):
        return

    # Перестановки уже напечатаны, но трассировку печатает tracer во время
    # перебора, поэтому permute вызывается еще раз – уже с trace=True
    print("\nСтек рекурсивных вызовов (повторный вызов permute(nums, trace=True)):")
    permute(nums, trace=True)


if __name__ == "__main__":
    main()
