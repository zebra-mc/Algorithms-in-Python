# Домашняя работа 3. Задача 1. Two sum
# Максим Царьков


def two_sum(arr, k):
    """Индексы (i, j), i < j, для которых arr[i] + arr[j] == k. None, если пары нет.

    Один проход со словарем seen: значение -> индекс. Для очередного x пара
    ему - это k - x; если такое значение уже встречалось левее, ответ найден.
    """
    seen = {}
    for i, x in enumerate(arr):
        need = k - x
        if need in seen:
            return seen[need], i
        # x кладем только после проверки, иначе при k == 2 * x одиночный x
        # нашел бы в seen сам себя
        seen[x] = i
    return None


def count_pairs(arr, k):
    """Сколько пар индексов i < j дают сумму k. Нужна для проверки условия задачи."""
    count = {}
    pairs = 0
    for x in arr:
        # x образует пару с каждым элементом k - x, который стоит левее
        pairs += count.get(k - x, 0)
        count[x] = count.get(x, 0) + 1
    return pairs


def trace(arr, k):
    """Тот же проход, что в two_sum, но с записью состояния после каждого шага.

    Нужна для визуализации в README: тесты сверяют с ней таблицу шагов.
    Возвращает список кортежей (i, x, need, seen, found): seen - копия словаря
    после шага, found - индекс найденной пары для x или None.
    """
    seen = {}
    steps = []
    for i, x in enumerate(arr):
        need = k - x
        if need in seen:
            steps.append((i, x, need, dict(seen), seen[need]))
            break
        seen[x] = i
        steps.append((i, x, need, dict(seen), None))
    return steps


def format_answer(pair):
    """Ответ в виде '1, 2', как в примерах из условия."""
    return f"{pair[0]}, {pair[1]}"


def parse_numbers(s):
    """Разбирает строку вида '1 3 4 10' в список целых. None, если ввод некорректный."""
    parts = s.split()
    if not parts:
        return None
    for token in parts:
        # int() принял бы '+5' и '1_000', а isdigit() без isascii() пропустил
        # бы '²', на котором int() падает; поэтому только ASCII-цифры
        body = token[1:] if token.startswith("-") else token
        if not (body.isascii() and body.isdigit()):
            return None
    return [int(token) for token in parts]


def parse_number(s):
    """Разбирает одно целое число. None, если ввод некорректный."""
    numbers = parse_numbers(s)
    if numbers is None or len(numbers) != 1:
        return None
    return numbers[0]


def read_numbers(prompt):
    """Читает целые числа через пробел с клавиатуры. None, если ввод некорректный."""
    return parse_numbers(input(prompt))


def read_number(prompt):
    """Читает одно целое число с клавиатуры. None, если ввод некорректный."""
    return parse_number(input(prompt))


def main():
    arr = read_numbers("Введите массив через пробел: ")
    if arr is None:
        print("Некорректный ввод: нужны целые числа через пробел")
        return
    k = read_number("Введите k: ")
    if k is None:
        print("Некорректный ввод: k должно быть одним целым числом")
        return
    pairs = count_pairs(arr, k)
    if pairs != 1:
        print(f"Некорректный ввод: пара с суммой k должна быть ровно одна, а их {pairs}")
        return
    print(format_answer(two_sum(arr, k)))


if __name__ == "__main__":
    main()
