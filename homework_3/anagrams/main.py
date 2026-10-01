# Домашняя работа 3. Задача 2. Anagrams
# Максим Царьков


def group_anagrams(strs):
    """Группирует слова так, что в одной группе оказываются все анаграммы.

    Ключ группы - буквы слова, расставленные по алфавиту: у анаграмм он
    совпадает, у остальных слов различается. Группы возвращаются в порядке
    первого появления ключа, слова внутри группы - в порядке входного списка.
    """
    groups = {}
    for word in strs:
        key = "".join(sorted(word))
        groups.setdefault(key, []).append(word)
    return list(groups.values())


def sort_groups(groups):
    """Приводит ответ к виду из условия: слова в группе по алфавиту, группы по размеру.

    Порядок групп в задаче не важен, функция нужна для однозначного вывода
    и сравнения в тестах. При равном размере группы сравниваются по словам.
    """
    return sorted((sorted(group) for group in groups), key=lambda g: (len(g), g))


def parse_words(s):
    """Разбирает строку вида 'eat tea tan'. None, если ввод некорректный.

    Консольный ввод ограничен строчными латинскими буквами, как в примере из условия.
    Сама group_anagrams работает с любыми строками.
    """
    parts = s.split()
    if not parts:
        return None
    for token in parts:
        # isalpha() без isascii() пропустил бы кириллицу и буквы с диакритикой
        if not (token.isascii() and token.isalpha() and token.islower()):
            return None
    return parts


def read_words(prompt):
    """Читает слова через пробел с клавиатуры. None, если ввод некорректный."""
    return parse_words(input(prompt))


def main():
    words = read_words("Введите слова через пробел: ")
    if words is None:
        print("Некорректный ввод: нужны слова из строчных латинских букв через пробел")
        return
    print(sort_groups(group_anagrams(words)))


if __name__ == "__main__":
    main()
